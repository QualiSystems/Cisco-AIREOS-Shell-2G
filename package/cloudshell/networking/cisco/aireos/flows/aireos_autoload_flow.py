from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow
from cloudshell.networking.cisco.aireos.autoload.aireos_autoload import AireOSAutoload


class CiscoAireosSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snpm_service:
            aireos_snmp_autoload = AireOSAutoload(snpm_service,
                                                       shell_name,
                                                       shell_type,
                                                       resource_name,
                                                       self._logger)
            return aireos_snmp_autoload.discover(supported_os)
