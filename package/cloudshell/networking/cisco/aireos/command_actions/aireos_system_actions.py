#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import OrderedDict

from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.aireos.command_templates import aireos_save_templates
from cloudshell.networking.cisco.aireos.command_templates import aireos_restore_templates
# from cloudshell.networking.cisco.command_templates import configuration
from cloudshell.cli.session.session_exceptions import ExpectedSessionException, CommandExecutionException


class AireosSaveActions(object):
    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def save_config_name(self, filename, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_FILENAME,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(filename=filename)

    def save_data_type(self, data_type, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_DATA_TYPE,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(data_type=data_type)

    def save_mode(self, mode, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_MODE,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(mode=mode)

    def save_server_ip(self, server_ip, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_SERVER_IP,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(server_ip=server_ip)

    def save_path(self, path, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_PATH,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(path=path)

    def save_user(self, user, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_USER,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(user=user)

    def save_password(self, password, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_PASSWORD,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(password=password)

    def save_server_port(self, port, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_PORT,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(port=port)

    def save_start(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_START,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command()
