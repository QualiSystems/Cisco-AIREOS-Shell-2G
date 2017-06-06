#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.run_command_runner import RunCommandRunner
from cloudshell.networking.cisco.aireos.cli.aireos_cli_handler import CiscoAireosCliHandler


class CiscoAireosRunCommandRunner(RunCommandRunner):
    def __init__(self, cli, resource_config, logger, api):
        """Create CiscoRunCommandOperations

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        super(CiscoAireosRunCommandRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.resource_config = resource_config

    @property
    def cli_handler(self):
        return CiscoAireosCliHandler(self.cli, self.resource_config, self._logger, self.api)
