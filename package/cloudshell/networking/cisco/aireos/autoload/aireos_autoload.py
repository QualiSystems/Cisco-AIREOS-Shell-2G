import re

from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.networking.autoload_structure import GenericResource, GenericChassis, GenericPort, \
    GenericPortChannel


class AireOSAutoload(object):
    PORT_DESCRIPTION_FILTER = [r'[Vv]irtual', r'[Cc]hannel']
    SUPPORTED_OS = [r'Controller']

    def __init__(self, snmp_handler, shell_name, shell_type, resource_name, logger):
        self.shell_name = shell_name
        self.shell_type = shell_type
        self._content_indexes = None
        self._if_indexes = None
        self.logger = logger
        self.snmp_handler = snmp_handler
        self._resource_name = resource_name

        self.resource = GenericResource(shell_name=shell_name,
                                        shell_type=shell_type,
                                        name=resource_name,
                                        unique_id=resource_name)

        self._chassis = None
        self._ports = {}
        self._snmp_cache = {}

    def _snmp_request(self, request_data):
        if isinstance(request_data, tuple):
            if request_data in self._snmp_cache:
                result = self._snmp_cache[request_data]
            else:
                if len(request_data) == 2:
                    result = self.snmp_handler.walk(request_data)
                elif len(request_data) == 3:
                    result = self.snmp_handler.get_property(*request_data)
                else:
                    raise Exception('_snmp_request', 'Request tuple len has to be 2 or 3')
                self._snmp_cache[request_data] = result
        else:
            raise Exception('_snmp_request', 'Has to be tuple')
        return result

    def _get_from_table(self, key, table):
        if key in table:
            return table[key]
        else:
            return None

    def _match_pattern_list(self, pattern_list, data):
        for pattern in pattern_list:
            if re.search(pattern, data):
                return True
        return False

    def _build_root_elements(self):
        self.resource.contact_name = self._snmp_request(('SNMPv2-MIB', 'sysContact', '0'))
        self.resource.system_name = self._snmp_request(('SNMPv2-MIB', 'sysName', '0'))
        self.resource.location = self._snmp_request(('SNMPv2-MIB', 'sysLocation', '0'))
        self.resource.os_version = self._snmp_request(('ENTITY-MIB', 'entPhysicalSoftwareRev', '1'))
        self.resource.vendor = self._snmp_request(('SNMPv2-MIB', 'sysObjectID', '0'))
        self.resource.model = self._snmp_request(('ENTITY-MIB', 'entPhysicalDescr', '1'))

    def _build_chassis_elements(self):

        entity_table = self._snmp_request(('ENTITY-MIB', 'entPhysicalTable'))

        chassis_id = None
        entity_data = None

        if entity_table is not None and len(entity_table) > 0:
            for id, table in entity_table.iteritems():
                if re.search(r'[Cc]hassis', table.get('entPhysicalName')) and table.get(
                        'entPhysicalParentRelPos') == '-1':
                    chassis_id = id
                    entity_data = table
                    break
        else:
            raise Exception(self.__class__.__name__, 'Entity table is empty')

        if chassis_id and entity_data:
            self._chassis = GenericChassis(shell_name=self.shell_name,
                                           name="Chassis {}".format(chassis_id),
                                           unique_id="{0}.{1}.{2}".format(self._resource_name, "chassis", chassis_id))
        else:
            raise Exception(self.__class__.__name__, 'Cannot find chassis data in entity table')

        self._chassis.model = self._get_from_table('entPhysicalModelName', entity_data)
        self._chassis.serial_number = self._get_from_table('entPhysicalSerialNum', entity_data)
        self.resource.add_sub_resource(chassis_id, self._chassis)

    def _build_ports(self):
        if_mib_table = self._snmp_request(('IF-MIB', 'ifTable'))

        for index, table in if_mib_table.iteritems():
            port_description = self._get_from_table('ifDescr', table)
            if self._match_pattern_list(self.PORT_DESCRIPTION_FILTER, port_description):
                break
            port_index = self._get_from_table('ifIndex', table)
            port = GenericPort(shell_name=self.shell_name,
                               name=self._convert_port_description(port_description),
                               unique_id='{0}.{1}.{2}'.format(self._resource_name, 'port', port_index))

            # port = Port(port_index, self._convert_port_description(port_description))
            # port_attributes = dict()
            port.port_description = self._snmp_request(('IF-MIB', 'ifAlias', index))
            port.l2_protocol_type = str(self._get_from_table('ifType', table)).replace("""'""", '')
            port.mac_address = self._get_from_table('ifPhysAddress', table)
            port.mtu = self._get_from_table('ifMtu', table)
            port.bandwidth = self._get_from_table('ifSpeed', table)
            port.ipv4_address = self._find_associated_ipv4(index)
            port.ipv6_address = self._find_associated_ipv6(index)
            port.duplex = self._get_duplex(index)
            port.auto_negotiation = self._get_autonegotiation(index)
            self._ports[port_index] = port
            self._chassis.add_sub_resource(port_index, port)

    def _build_port_channels(self):
        if_mib_table = self._snmp_request(('IF-MIB', 'ifTable'))
        for index, table in if_mib_table.iteritems():
            description = table['ifDescr']
            if re.search(r'[Cc]hannel', description) and '.' not in description:
                suitable_description = self._convert_port_description(description)
                port_channel_index = self._get_from_table('ifIndex', table)
                port_channel = GenericPortChannel(shell_name=self.shell_name,
                                                  name=suitable_description,
                                                  unique_id='{0}.{1}.{2}'.format(self._resource_name,
                                                                                 'port_channel',
                                                                                 port_channel_index))

                # port = PortChannel(self._get_from_table('ifIndex', table), suitable_description)
                # pc_attributes = dict()
                port_channel.port_description = self._snmp_request(('IF-MIB', 'ifAlias', index))
                # pc_attributes[PortChannelAttributes.PROTOCOL_TYPE] = self._get_from_table('ifType', table)
                port_channel.ipv4_address = self._find_associated_ipv4(index)
                port_channel.ipv6_address = self._find_associated_ipv6(index)
                port_channel.associated_ports = self._get_associated_ports(index)
                self.resource.add_sub_resource(port_channel_index, port_channel)

    def _get_duplex(self, index):
        duplex_table = self._snmp_request(('EtherLike-MIB', 'dot3StatsDuplexStatus'))
        duplex = None
        if len(duplex_table) > 0:
            if index in duplex_table:
                duplex = duplex_table[index]
        return duplex

    def _get_autonegotiation(self, index):
        """Get Autonegotiation for interface

        :param index: port id
        :return: Autonegotiation for interface
        :rtype string
        """
        autoneg = 'False'
        try:
            auto_negotiation = self.snmp_handler.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', index, 1)).values()[0]
            if 'enabled' in auto_negotiation.lower():
                autoneg = 'True'
        except Exception as e:
            self.logger.error('Failed to load auto negotiation property for interface {0}'.format(e.message))
        return autoneg

    def _get_adjacent(self, interface_id):
        """Get connected device interface and device name to the specified port id, using cdp or lldp protocols

        :param interface_id: port id
        :return: device's name and port connected to port id
        :rtype string
        """

        lldp_local_table = self._snmp_request(('LLDP-MIB', 'lldpLocPortDesc'))
        lldp_remote_table = self._snmp_request(('LLDP-MIB', 'lldpRemTable'))
        # cdp_index_table = self._snmp_request(('CISCO-CDP-MIB', 'cdpInterface'))
        cdp_table = self._snmp_request(('CISCO-CDP-MIB', 'cdpCacheTable'))

        result = ''
        for key, value in cdp_table.iteritems():
            if 'cdpCacheDeviceId' in value and 'cdpCacheDevicePort' in value:
                if re.search('^\d+', str(key)).group(0) == interface_id:
                    result = '{0} through {1}'.format(value['cdpCacheDeviceId'], value['cdpCacheDevicePort'])
        if result == '' and lldp_remote_table:
            for key, value in lldp_local_table.iteritems():
                interface_name = self._snmp_request(('IF-MIB', 'ifTable'))[interface_id]['ifDescr']
                if interface_name == '':
                    break
                if 'lldpLocPortDesc' in value and interface_name in value['lldpLocPortDesc']:
                    if 'lldpRemSysName' in lldp_remote_table and 'lldpRemPortDesc' in lldp_remote_table:
                        result = '{0} through {1}'.format(lldp_remote_table[key]['lldpRemSysName'],
                                                          lldp_remote_table[key]['lldpRemPortDesc'])
        return result

    def _find_associated_ipv4(self, port_index):
        ip_addr_table = self._snmp_request(('IP-MIB', 'ipAddrTable'))
        for ip, data in ip_addr_table.iteritems():
            if 'ipAdEntIfIndex' in data and port_index == data['ipAdEntIfIndex']:
                return data['ipAdEntAddr']
        return None

    def _find_associated_ipv6(self, port_index):
        ipv6_table = self._snmp_request(('IPV6-MIB', 'ipv6AddrEntry'))
        for ip, data in ipv6_table.iteritems():
            if 'ipAdEntIfIndex' in data and port_index == data['ipAdEntIfIndex']:
                return data['ipAdEntAddr']
        return None

    def _get_associated_ports(self, index):
        agg_table = self._snmp_request(('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'))
        result = ''
        for key, value in agg_table.iteritems():
            if str(index) in value['dot3adAggPortAttachedAggID']:
                if key in self._ports:
                    phisical_port = self._ports[key]
                    if result:
                        result += ',' + phisical_port.name
                    else:
                        result = phisical_port.name
        return result.strip(' \t\n\r')

    def _convert_port_description(self, description):
        return description.replace('/', '-').replace(' ', '').replace(':', '-')

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp
            :return: True or False
        """

        system_description = self._snmp_request(('SNMPv2-MIB', 'sysDescr', 0))
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))
        result = re.search(r"({0})".format("|".join(supported_os)),
                           system_description,
                           flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for \'{0}\' operation system(s)'. \
                format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def discover(self, supported_os):
        if not self._is_valid_device_os(supported_os):
            raise Exception(self.__class__.__name__, 'Unsupported device OS, see logs for more details')
        self._build_root_elements()
        self._build_chassis_elements()
        self._build_ports()
        self._build_port_channels()
        # self._root.build_relative_path()
        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        # autoload_details = AutoLoadDetails(self._root.get_resources(), self._root.get_attributes())
        return autoload_details
