#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.devices.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.juniper.cli.junipr_command_modes import DefaultCommandMode, ConfigCommandMode


class CiscoAireosCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        super(CiscoAireosCliHandler, self).__init__(cli, resource_config, logger, api)
        self.modes = CommandModeHelper.create_command_mode(resource_config, api)

    @property
    def enable_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def config_mode(self):
        return self.modes[ConfigCommandMode]

    def default_mode_service(self):
        """
        Default mode session
        :return:
        """
        return self.get_cli_service(self.enable_mode)

    def config_mode_service(self):
        """
        Config mode session
        :return:
        """
        return self.get_cli_service(self.config_mode)

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """
ssh_session = SessionCreator(AireOSSSHSession)
ssh_session.proxy = ReturnToPoolProxy
ssh_session.kwargs = {'username': get_attribute_by_name_wrapper('User'),
                      'password': get_decrypted_password_by_attribute_name_wrapper('Password'),
                      'host': get_resource_address}
CONNECTION_MAP[CONNECTION_TYPE_SSH] = ssh_session

CONNECTION_EXPECTED_MAP = OrderedDict({r'[Uu]ser:': lambda session: session.send_line(get_attribute_by_name('User')),
                                       r'[Pp]assword:': lambda session: session.send_line(
                                           get_decrypted_password_by_attribute_name_wrapper('Password')())})