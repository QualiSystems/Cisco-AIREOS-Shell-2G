#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.cli.session.telnet_session import TelnetSession

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.devices.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.cisco.aireos.cli.aireos_command_modes import DefaultCommandMode, ConfigCommandMode
from cloudshell.networking.cisco.aireos.cli.sessions.aireos_ssh_session import AireOSSSHSession


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

    def _ssh_session(self):
        return AireOSSSHSession(self.resource_address, self.username, self.password, self.port, self.on_session_start)

    def _new_sessions(self):
        if self.cli_type.lower() == AireOSSSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        else:
            new_sessions = [self._ssh_session(), self._telnet_session()]
        return new_sessions

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        session.hardware_expect("config paging disable", DefaultCommandMode.PROMPT, logger)
