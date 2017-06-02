from cloudshell.devices.snmp_handler import SnmpHandler
from cloudshell.networking.cisco.aireos.cli.aireos_cli_handler import CiscoAireosCliHandler
from cloudshell.networking.cisco.aireos.flows.aireos_disable_snmp_flow import CiscoAireosDisableSnmpFlow
from cloudshell.networking.cisco.aireos.flows.aireos_enable_snmp_flow import CiscoAireosEnableSnmpFlow


class CiscoAireosSnmpHandler(SnmpHandler):
    def __init__(self, cli, resource_config, logger, api):
        super(CiscoAireosSnmpHandler, self).__init__(resource_config, logger, api)
        self._cli = cli
        self._api = api

    @property
    def aireos_cli_handler(self):
        return CiscoAireosCliHandler(self._cli, self.resource_config, self._logger, self._api)

    def _create_enable_flow(self):
        return CiscoAireosEnableSnmpFlow(self.aireos_cli_handler, self._logger)

    def _create_disable_flow(self):
        return CiscoAireosDisableSnmpFlow(self.aireos_cli_handler,
                                          self._logger)
