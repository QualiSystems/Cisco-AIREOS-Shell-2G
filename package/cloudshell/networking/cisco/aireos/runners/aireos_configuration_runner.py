#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.networking.cisco.aireos.cli.aireos_cli_handler import CiscoAireosCliHandler
from cloudshell.networking.cisco.aireos.flows.aireos_restore_flow import CiscoAireosRestoreFlow
from cloudshell.networking.cisco.aireos.flows.aireos_save_flow import CiscoAireosSaveFlow


class CiscoAireosConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli, logger, resource_config, api):
        super(CiscoAireosConfigurationRunner, self).__init__(logger, resource_config, api)
        self._cli = cli

    @property
    def cli_handler(self):
        """ CLI Handler property
        :return: CLI handler
        """
        return CiscoAireosCliHandler(self._cli, self.resource_config, self._logger, self._api)

    @property
    def restore_flow(self):
        return CiscoAireosRestoreFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def save_flow(self):
        return CiscoAireosSaveFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def file_system(self):
        raise Exception(self.__class__.__name__, "Device doesn't support copying files to local folders")
