from cloudshell.networking.autoload.networking_model import RootElement, Chassis, Port, PortChannel
from cloudshell.networking.autoload.networking_attributes import RootAttributes, ChassisAttributes, PortAttributes, \
    PortChannelAttributes
from cloudshell.networking.operations.interfaces.autoload_operations_interface import AutoloadOperationsInterface
from cloudshell.shell.core.config_utils import override_attributes_from_config
import inject
from cloudshell.configuration.cloudshell_snmp_binding_keys import SNMP_HANDLER
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER
from cloudshell.shell.core.driver_context import AutoLoadDetails
import os
import re


class AireOSAutoload(AutoloadOperationsInterface):
    PORT_DESCRIPTION_FILTER = [r'[Vv]irtual', r'[Cc]hannel']
    SUPPORTED_OS = [r'Controller']

    def __init__(self, snmp_hander=None, logger=None):
        self._snmp_handler = None
        self.snmp_handler = snmp_hander
        self._root = RootElement()
        self._chassis = None
        self._ports = {}
        self._snmp_cache = {}
        self._logger = logger

        overridden_config = override_attributes_from_config(AireOSAutoload)
        self.supported_os = overridden_config.SUPPORTED_OS

    @property
    def snmp_handler(self):
        if self._snmp_handler is None:
            self.snmp_handler = inject.instance(SNMP_HANDLER)
        return self._snmp_handler

    @snmp_handler.setter
    def snmp_handler(self, snmp_handler):
        if snmp_handler:
            self._snmp_handler = snmp_handler
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
            self._snmp_handler.update_mib_sources(path)

    @property
    def logger(self):
        if self._logger is not None:
            return self._logger
        return inject.instance(LOGGER)

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
        root_attributes = dict()
        root_attributes[RootAttributes.CONTACT_NAME] = self._snmp_request(('SNMPv2-MIB', 'sysContact', '0'))
        root_attributes[RootAttributes.SYSTEM_NAME] = self._snmp_request(('SNMPv2-MIB', 'sysName', '0'))
        root_attributes[RootAttributes.LOCATION] = self._snmp_request(('SNMPv2-MIB', 'sysLocation', '0'))
        root_attributes[RootAttributes.OS_VERSION] = self._snmp_request(('ENTITY-MIB', 'entPhysicalSoftwareRev', '1'))
        root_attributes[RootAttributes.VENDOR] = self._snmp_request(('SNMPv2-MIB', 'sysObjectID', '0'))
        root_attributes[RootAttributes.MODEL] = self._snmp_request(('ENTITY-MIB', 'entPhysicalDescr', '1'))
        self._root.build_attributes(root_attributes)

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
            raise Exception('_build_chassis_elements', 'Entity table is empty')

        if chassis_id and entity_data:
            self._chassis = Chassis(chassis_id)
        else:
            raise Exception('_build_chassis_elements', 'Cannot find chassis data in entity table')

        chassis_attributes = dict()
        chassis_attributes[ChassisAttributes.MODEL] = self._get_from_table('entPhysicalModelName', entity_data)
        chassis_attributes[ChassisAttributes.SERIAL_NUMBER] = self._get_from_table('entPhysicalSerialNum', entity_data)
        self._chassis.build_attributes(chassis_attributes)
        self._root.chassis.append(self._chassis)

    def _build_ports(self):
        if_mib_table = self._snmp_request(('IF-MIB', 'ifTable'))

        for index, table in if_mib_table.iteritems():
            port_description = self._get_from_table('ifDescr', table)
            if self._match_pattern_list(self.PORT_DESCRIPTION_FILTER, port_description):
                break
            port_index = self._get_from_table('ifIndex', table)
            port = Port(port_index, self._convert_port_description(port_description))
            port_attributes = dict()
            port_attributes[PortAttributes.PORT_DESCRIPTION] = self._snmp_request(('IF-MIB', 'ifAlias', index))
            port_attributes[PortAttributes.L2_PROTOCOL_TYPE] = str(self._get_from_table('ifType', table)).replace(
                """'""", '')
            port_attributes[PortAttributes.MAC_ADDRESS] = self._get_from_table('ifPhysAddress', table)
            port_attributes[PortAttributes.MTU] = self._get_from_table('ifMtu', table)
            port_attributes[PortAttributes.BANDWIDTH] = self._get_from_table('ifSpeed', table)
            port_attributes[PortAttributes.IPV4_ADDRESS] = self._find_associated_ipv4(index)
            port_attributes[PortAttributes.IPV6_ADDRESS] = self._find_associated_ipv6(index)
            port_attributes[PortAttributes.DUPLEX] = self._get_duplex(index)
            port_attributes[PortAttributes.AUTO_NEGOTIATION] = self._get_autonegotiation(index)
            # port_attributes[PortAttributes.ADJACENT] = self._get_adjacent(index)
            port.build_attributes(port_attributes)
            self._ports[port_index] = port
            self._chassis.ports.append(port)

    def _build_port_channels(self):
        if_mib_table = self._snmp_request(('IF-MIB', 'ifTable'))
        for index, table in if_mib_table.iteritems():
            description = table['ifDescr']
            if re.search(r'[Cc]hannel', description) and '.' not in description:
                suitable_description = self._convert_port_description(description)
                port = PortChannel(self._get_from_table('ifIndex', table), suitable_description)
                pc_attributes = dict()
                pc_attributes[PortChannelAttributes.PORT_DESCRIPTION] = self._snmp_request(('IF-MIB', 'ifAlias', index))
                pc_attributes[PortChannelAttributes.PROTOCOL_TYPE] = self._get_from_table('ifType', table)
                pc_attributes[PortChannelAttributes.IPV4_ADDRESS] = self._find_associated_ipv4(index)
                pc_attributes[PortChannelAttributes.IPV6_ADDRESS] = self._find_associated_ipv6(index)
                pc_attributes[PortChannelAttributes.ASSOCIATED_PORTS] = self._get_associated_ports(index)
                port.build_attributes(pc_attributes)
                self._root.port_channels.append(port)

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

    def _is_valid_device_os(self):
        """Validate device OS using snmp
            :return: True or False
        """

        system_description = self._snmp_request(('SNMPv2-MIB', 'sysDescr', 0))
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))
        result = re.search(r"({0})".format("|".join(self.supported_os)),
                           system_description,
                           flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for \'{0}\' operation system(s)'. \
                format(str(tuple(self.supported_os)))
            self.logger.error(error_message)
            return False

    def discover(self):
        if not self._is_valid_device_os():
            raise Exception(self.__class__.__name__, 'Unsupported device OS, see logs for more details')
        self._build_root_elements()
        self._build_chassis_elements()
        self._build_ports()
        self._build_port_channels()
        self._root.build_relative_path()
        autoload_details = AutoLoadDetails(self._root.get_resources(), self._root.get_attributes())
        return autoload_details
