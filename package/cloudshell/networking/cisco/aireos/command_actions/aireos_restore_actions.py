#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.cisco.aireos.command_templates import aireos_restore_templates


class AireosRestoreActions(object):
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

    def restore_config_name(self, filename, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_FILENAME,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(filename=filename)

    def restore_data_type(self, data_type, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_DATA_TYPE,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(data_type=data_type)

    def restore_mode(self, mode, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_MODE,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(mode=mode)

    def restore_server_ip(self, server_ip, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_SERVER_IP,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(server_ip=server_ip)

    def restore_path(self, path, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_PATH,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(path=path)

    def restore_user(self, user, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_USER,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(user=user)

    def restore_password(self, password, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_PASSWORD,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(password=password)

    def restore_server_port(self, port, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_restore_templates.RESTORE_CONFIGURATION_PORT,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(port=port)

    def restore_start(self, timeout=300, reconnect_timeout=600, action_map=None, error_map=None):
        output = ""
        try:
            output = CommandTemplateExecutor(self._cli_service,
                                             aireos_restore_templates.RESTORE_CONFIGURATION_START,
                                             action_map=action_map,
                                             error_map=error_map,
                                             timeout=timeout,
                                             check_action_loop_detector=False).execute_command()

        except Exception as e:
            self._logger.debug(e, exc_info=True)
            self._logger.info("Session closed, starting reconnect")
            self._cli_service.reconnect(reconnect_timeout)

        return output

    def reload(self, timeout=600, action_map=None, error_map=None):
        try:
            CommandTemplateExecutor(self._cli_service,
                                    aireos_restore_templates.RELOAD,
                                    action_map=action_map,
                                    error_map=error_map,
                                    check_action_loop_detector=False).execute_command()
        except Exception as e:
            self._logger.debug(e, exc_info=True)
            self._logger.info("Session closed, starting reconnect")
            self._cli_service.reconnect(timeout)
