#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.connectivity_runner import ConnectivityRunner
from cloudshell.networking.cisco.aireos.cli.aireos_cli_handler import CiscoAireosCliHandler
from cloudshell.networking.cisco.aireos.exceptions.aireos_connectivity_error import AireosConnectivityError


class CiscoAireosConnectivityRunner(ConnectivityRunner):
    def __init__(self, cli, logger, api, resource_config):
        """ Handle add/remove vlan flows
            :param cli:
            :param logger:
            :param api:
            :param resource_config:
            """

        super(CiscoAireosConnectivityRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.resource_config = resource_config

    @property
    def cli_handler(self):
        return CiscoAireosCliHandler(self.cli, self.resource_config, self._logger, self.api)

    @property
    def add_vlan_flow(self):
        raise AireosConnectivityError(self.__class__.__name__, "Vlan Connectivity is not supported.")

    @property
    def remove_vlan_flow(self):
        raise AireosConnectivityError(self.__class__.__name__, "Vlan Connectivity is not supported.")
