#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.aireos.command_actions.aireos_restore_actions import AireosRestoreActions


class CiscoAireosLoadFirmwareFlow(LoadFirmwareFlow):
    DATA_TYPE = 'code'

    def __init__(self, cli_handler, logger):
        super(CiscoAireosLoadFirmwareFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        :return:
        """

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
            restore_action.restore_path(url.get(url_path))
            restore_action.restore_start(timeout)
            restore_action.reload(timeout)
