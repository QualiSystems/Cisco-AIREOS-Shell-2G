#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner
from cloudshell.networking.cisco.aireos.flows.aireos_autoload_flow import CiscoAireosSnmpAutoloadFlow
from cloudshell.networking.cisco.aireos.snmp.aireos_snmp_handler import CiscoAireosSnmpHandler


class CiscoAireosAutoloadRunner(AutoloadRunner):
    def __init__(self, cli, logger, resource_config, api):
        super(CiscoAireosAutoloadRunner, self).__init__(resource_config)
        self._cli = cli
        self._api = api
        self._logger = logger

    @property
    def snmp_handler(self):
        return CiscoAireosSnmpHandler(self._cli, self.resource_config, self._logger, self._api)

    @property
    def autoload_flow(self):
        return CiscoAireosSnmpAutoloadFlow(self.snmp_handler, self._logger)
