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


class AireosFirmwareActions(object):
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

    def save_mode(self, save_mode, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_save_templates.SAVE_CONFIGURATION_MODE,
                                       action_map=action_map,
                                       error_map=error_map,
                                       check_action_loop_detector=False).execute_command(save_mode=save_mode)

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

    def restore_configuration(self, timeout, source_file, config_type, restore_method='override', vrf=None):

        if not source_file:
            raise Exception('AireOSOperations', 'Configuration URL cannot be empty')

        if not restore_method or restore_method.lower() != 'override':
            raise Exception(self.__class__.__name__, 'Device does not support restoring in \"{}\" method, '
                                                     '"override" is only supported'.format(restore_method or 'None'))

        if not config_type or config_type.lower() != 'running':
            raise Exception(self.__class__.__name__, 'Device does not support restoring in \"{}\" configuration type, '
                                                     '"running" is only supported'.format(config_type or 'None'))

        connection_dict = UrlParser.parse_url(source_file)
        self._logger.debug('Connection dict: ' + str(connection_dict))

        restore_flow = OrderedDict()
        datatype = 'config'
        restore_flow[save_restore.RESTORE_CONFIGURATION_DATATYPE] = datatype

        template_flow = OrderedDict()
        template_flow[save_restore.RESTORE_CONFIGURATION_MODE] = UrlParser.SCHEME
        template_flow[save_restore.RESTORE_CONFIGURATION_USER] = UrlParser.USERNAME
        template_flow[save_restore.RESTORE_CONFIGURATION_PASSWORD] = UrlParser.PASSWORD
        template_flow[save_restore.RESTORE_CONFIGURATION_SERVERIP] = UrlParser.HOSTNAME
        template_flow[save_restore.RESTORE_CONFIGURATION_PORT] = UrlParser.PORT
        template_flow[save_restore.RESTORE_CONFIGURATION_PATH] = UrlParser.PATH
        template_flow[save_restore.RESTORE_CONFIGURATION_FILENAME] = UrlParser.FILENAME

        generated_flow = self._generate_flow(template_flow, connection_dict)
        restore_flow.update(generated_flow)

        execute_command_map(restore_flow, self.cli_service.send_command)

        expected_map = OrderedDict({r'[yY]/[nN]': lambda session: session.send_line('y')})
        error_map = OrderedDict({r'[Ee]rror:': 'Restore configuration error, see logs for details'})

        self.cli_service.send_command(save_restore.RESTORE_CONFIGURATION_START.get_command(),
                                      expected_str=r'System being reset.',
                                      expected_map=expected_map, error_map=error_map)
        session = self.session
        if not session.session_type.lower() == 'console':
            self._cli_service.reconnect(timeout)

    def override_running(self, path, action_map=None, error_map=None, timeout=300, reconnect_timeout=1600):
        """Override running-config

        :param path: relative path to the file on the remote host tftp://server/sourcefile
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :raise Exception:
        """

        try:
            output = CommandTemplateExecutor(self._cli_service,
                                             configuration.CONFIGURE_REPLACE,
                                             action_map=action_map,
                                             error_map=error_map,
                                             timeout=timeout,
                                             check_action_loop_detector=False).execute_command(path=path)
            match_error = re.search(r'[Ee]rror.*$', output)
            if match_error:
                error_str = match_error.group()
                raise CommandExecutionException('Override_Running',
                                                'Configure replace completed with error: ' + error_str)
        except ExpectedSessionException as e:
            self._logger.warning(e.args)
            if isinstance(e, CommandExecutionException):
                raise
            self._cli_service.reconnect(reconnect_timeout)

    def write_erase(self, action_map=None, error_map=None):
        """Erase startup configuration

        :param action_map:
        :param error_map:
        """

        CommandTemplateExecutor(self._cli_service,
                                configuration.WRITE_ERASE,
                                action_map=action_map,
                                error_map=error_map).execute_command()

    def reload_device(self, timeout, action_map=None, error_map=None):
        """Reload device

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        try:
            redundancy_reload = CommandTemplateExecutor(self._cli_service,
                                                        configuration.REDUNDANCY_PEER_SHELF,
                                                        action_map=action_map,
                                                        error_map=error_map
                                                        ).execute_command()
            if re.search("[Ii]nvalid\s*([Ii]nput|[Cc]ommand)", redundancy_reload, re.IGNORECASE):
                CommandTemplateExecutor(self._cli_service,
                                        configuration.RELOAD,
                                        action_map=action_map,
                                        error_map=error_map).execute_command()

        except Exception as e:
            self._logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def get_flash_folders_list(self):
        output = CommandTemplateExecutor(self._cli_service, configuration.SHOW_FILE_SYSTEMS
                                         ).execute_command()

        match_dir = re.findall(r"(bootflash:|bootdisk:|flash-\d+\S+)", output, re.MULTILINE)
        if match_dir:
            return match_dir

    def reload_device_via_console(self, timeout=500, action_map=None, error_map=None):
        """Reload device

        :param session: current session
        :param logger:  logger
        :param timeout: session reconnect timeout
        """

        CommandTemplateExecutor(self._cli_service,
                                configuration.CONSOLE_RELOAD,
                                action_map=action_map,
                                error_map=error_map,
                                timeout=timeout).execute_command()
        self._cli_service.on_session_start(self._cli_service, self._logger)

    def get_current_boot_config(self, action_map=None, error_map=None):
        """Retrieve current boot configuration

        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        return CommandTemplateExecutor(self._cli_service,
                                       firmware.SHOW_RUNNING,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def get_current_os_version(self, action_map=None, error_map=None):
        """Retrieve os version

        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        return CommandTemplateExecutor(self._cli_service,
                                       firmware.SHOW_VERSION,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def get_current_boot_image(self):
        current_firmware = []
        for line in self.get_current_boot_config().splitlines():
            if ".bin" in line:
                current_firmware.append(line.strip(" "))

        return current_firmware

    def shutdown(self):
        """
        Shutdown the system
        :return:
        """

        pass


class FirmwareActions(object):
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

    def add_boot_config_file(self, firmware_file_name):
        """Set boot firmware file.

        :param firmware_file_name: firmware file nameSet boot firmware file.

        :param firmware_file_name: firmware file name
        """

        CommandTemplateExecutor(self._cli_service, firmware.BOOT_SYSTEM_FILE).execute_command(
            firmware_file_name=firmware_file_name)
        current_reg_config = CommandTemplateExecutor(self._cli_service,
                                                     configuration.SHOW_VERSION_WITH_FILTERS
                                                     ).execute_command(do='', filter="0x")
        if "0x2102" not in current_reg_config:
            CommandTemplateExecutor(self._cli_service, firmware.CONFIG_REG).execute_command()

    def add_boot_config(self, boot_config_line):
        """Set boot firmware file.

        :param boot_config_line: firmware file name
        """

        self._cli_service.send_command(boot_config_line)

    def clean_boot_config(self, config_line_to_remove, action_map=None, error_map=None):
        """Remove current boot from device

        :param config_line_to_remove: current boot configuration
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        self._logger.debug("Start cleaning boot configuration")

        self._logger.info("Removing '{}' boot config line".format(config_line_to_remove))
        CommandTemplateExecutor(self._cli_service,
                                configuration.NO, action_map=action_map,
                                error_map=error_map).execute_command(command=config_line_to_remove.strip(' '))

        self._logger.debug("Completed cleaning boot configuration")
