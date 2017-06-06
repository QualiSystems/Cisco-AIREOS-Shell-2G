#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.state_runner import StateRunner
from cloudshell.networking.cisco.aireos.cli.aireos_cli_handler import CiscoAireosCliHandler


class CiscoAireOSStateRunner(StateRunner):
    def __init__(self, cli, logger, api, resource_config):
        """

        :param cli:
        :param logger:
        :param api:
        :param resource_config:
        """

        super(CiscoAireOSStateRunner, self).__init__(logger, api, resource_config)
        self.cli = cli
        self.api = api

    @property
    def cli_handler(self):
        return CiscoAireosCliHandler(self.cli, self.resource_config, self._logger, self.api)
