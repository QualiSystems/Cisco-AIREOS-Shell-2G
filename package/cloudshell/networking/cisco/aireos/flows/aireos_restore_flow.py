#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.aireos.command_actions.aireos_restore_actions import AireosRestoreActions


class CiscoAireosRestoreFlow(RestoreConfigurationFlow):
    DATA_TYPE = "config"

    def __init__(self, cli_handler, logger):
        super(CiscoAireosRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
        """ Execute flow which restore selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        if "-config" not in configuration_type:
            configuration_type += "-config"

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            restore_action = AireosRestoreActions(session, self._logger)
            url = UrlParser.parse_url(path)
            restore_action.restore_data_type(self.DATA_TYPE)
            restore_action.restore_mode(url.get(UrlParser.SCHEME))
            restore_action.restore_user(url.get(UrlParser.USERNAME))
            restore_action.restore_password(url.get(UrlParser.PASSWORD))
            restore_action.restore_server_ip(url.get(UrlParser.HOSTNAME))
            port = url.get(UrlParser.PORT)
            if port:
                restore_action.restore_server_port(url.get(UrlParser.PORT))
            restore_action.restore_config_name(url.get(UrlParser.FILENAME))
            url_path = url.get(UrlParser.PATH)
            if url_path and url_path.startswith("/"):
                url_path = url_path[1:]
            restore_action.restore_path(url_path)
            restore_action.restore_start()
