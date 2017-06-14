#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.aireos.command_actions.aireos_save_actions import AireosSaveActions


class CiscoAireosSaveFlow(SaveConfigurationFlow):
    DATA_TYPE = "config"

    def __init__(self, cli_handler, logger):
        super(CiscoAireosSaveFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """

        if configuration_type.lower() == "startup":
            raise Exception(self.__class__.__name__, "Device doesn't have startup config")
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            save_action = AireosSaveActions(enable_session, self._logger)
            url = UrlParser.parse_url(folder_path)
            url_path = url.get(UrlParser.PATH)
            if url_path and len(url_path) > 1 and url_path.startswith("/"):
                url_path = url_path[1:]
            save_action.save_data_type(self.DATA_TYPE)
            save_action.save_config_name(url.get(UrlParser.FILENAME))
            save_action.save_mode(url.get(UrlParser.SCHEME))
            save_action.save_server_ip(url.get(UrlParser.HOSTNAME))
            save_action.save_path(url_path)
            save_action.save_user(url.get(UrlParser.USERNAME))
            save_action.save_password(url.get(UrlParser.PASSWORD))
            port = url.get(UrlParser.PORT)
            if port:
                save_action.save_server_port(url.get(UrlParser.PORT))

            save_action.save_start()
