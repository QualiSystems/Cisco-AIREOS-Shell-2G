from collections import OrderedDict
import time
from urlparse import urlsplit

from cloudshell.networking.operations.interfaces.configuration_operations_interface import \
    ConfigurationOperationsInterface
from cloudshell.networking.operations.interfaces.send_command_interface import SendCommandInterface
from cloudshell.networking.operations.interfaces.firmware_operations_interface import FirmwareOperationsInterface
from cloudshell.networking.operations.interfaces.power_operations_interface import PowerOperationsInterface
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER, CONTEXT, API
from cloudshell.configuration.cloudshell_cli_binding_keys import CLI_SERVICE, SESSION
from cloudshell.shell.core.config_utils import override_attributes_from_config
from cloudshell.shell.core.context_utils import get_attribute_by_name
import cloudshell.networking.cisco.aireos.operations.templates.save_restore_configuration as save_restore
from cloudshell.cli.command_template.command_template_service import execute_command_map
import inject
import os
import re


class AireOSOperations(ConfigurationOperationsInterface, SendCommandInterface, FirmwareOperationsInterface,
                       PowerOperationsInterface):
    SESSION_WAIT_TIMEOUT = 600
    DEFAULT_PROMPT = r'[>$#]\s*$'

    def __init__(self, cli_service=None, logger=None):
        self._cli_service = cli_service
        self._logger = logger
        overridden_config = override_attributes_from_config(AireOSOperations)
        self._session_wait_timeout = overridden_config.SESSION_WAIT_TIMEOUT
        self._default_prompt = overridden_config.DEFAULT_PROMPT

    @property
    def logger(self):
        if self._logger:
            logger = self._logger
        else:
            logger = inject.instance(LOGGER)
        return logger

    @property
    def cli_service(self):
        if not self._cli_service:
            self._cli_service = inject.instance(CLI_SERVICE)
        return self._cli_service

    @property
    def context(self):
        return inject.instance(CONTEXT)

    @property
    def api(self):
        return inject.instance(API)

    @property
    def session(self):
        return inject.instance(SESSION)

    def save_configuration(self, destination_host, source_filename, vrf=None):
        system_name = self.context.resource.fullname
        system_name = re.sub(r'[\.\s]', '_', system_name)

        if source_filename and source_filename.lower() == 'running':
            config_type = 'config'
        else:
            raise Exception(self.__class__.__name__,
                            'Device does not support saving \"{}\" configuration type, \"running\" '
                            'is only supported'.format(source_filename or 'None'))

        file_name = "{0}-{1}-{2}".format(system_name, source_filename, time.strftime("%d%m%y-%H%M%S", time.localtime()))
        if not destination_host:
            backup_location = get_attribute_by_name('Backup Location')
            if not backup_location:
                raise Exception('AireOSOperations', "Backup location or path is empty")
        else:
            backup_location = destination_host

        if not backup_location.endswith('/'):
            backup_location += '/'
        destination_dict = UrlParser.parse_url(backup_location)
        if not destination_dict:
            raise Exception('AireOSOperations', 'Incorrect Backup location')
        self.logger.debug('Connection dict: ' + str(destination_dict))

        save_flow = OrderedDict()
        save_flow[save_restore.SAVE_CONFIGURATION_DATATYPE] = config_type
        save_flow[save_restore.SAVE_CONFIGURATION_FILENAME] = file_name

        template_flow = OrderedDict()
        template_flow[save_restore.SAVE_CONFIGURATION_MODE] = UrlParser.SCHEME
        template_flow[save_restore.SAVE_CONFIGURATION_SERVERIP] = UrlParser.HOSTNAME
        template_flow[save_restore.SAVE_CONFIGURATION_PATH] = UrlParser.PATH
        template_flow[save_restore.SAVE_CONFIGURATION_USER] = UrlParser.USERNAME
        template_flow[save_restore.SAVE_CONFIGURATION_PASSWORD] = UrlParser.PASSWORD
        template_flow[save_restore.SAVE_CONFIGURATION_PORT] = UrlParser.PORT
        generated_flow = self._generate_flow(template_flow, destination_dict)
        if save_restore.SAVE_CONFIGURATION_PATH not in generated_flow:
            generated_flow[save_restore.SAVE_CONFIGURATION_PATH] = '/'

        save_flow.update(generated_flow)
        execute_command_map(save_flow, self.cli_service.send_command)

        expected_map = OrderedDict({r'[yY]/[nN]': lambda session: session.send_line('y')})
        error_map = OrderedDict({r'[Ee]rror:': 'Save configuration error, see logs for details'})

        self.cli_service.send_command(save_restore.SAVE_CONFIGURATION_START.get_command(), expected_map=expected_map,
                                      error_map=error_map)

        return file_name

    def restore_configuration(self, source_file, config_type, restore_method='override', vrf=None):

        if not source_file:
            raise Exception('AireOSOperations', 'Configuration URL cannot be empty')

        if not restore_method or restore_method.lower() != 'override':
            raise Exception(self.__class__.__name__, 'Device does not support restoring in \"{}\" method, '
                                                     '"override" is only supported'.format(restore_method or 'None'))

        if not config_type or config_type.lower() != 'running':
            raise Exception(self.__class__.__name__, 'Device does not support restoring in \"{}\" configuration type, '
                                                     '"running" is only supported'.format(config_type or 'None'))

        connection_dict = UrlParser.parse_url(source_file)
        self.logger.debug('Connection dict: ' + str(connection_dict))

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
            self._wait_session_up(self.session)

    def _wait_session_up(self, session):
        self.logger.debug('Waiting session up')
        waiting_reboot_time = time.time()
        while True:
            try:
                if time.time() - waiting_reboot_time > self._session_wait_timeout:
                    raise Exception(self.__class__.__name__,
                                    'Session cannot start reboot after {} sec.'.format(self._session_wait_timeout))
                session.send_line('')
                time.sleep(1)
            except:
                self.logger.debug('Session disconnected')
                break
        reboot_time = time.time()
        while True:
            if time.time() - reboot_time > self._session_wait_timeout:
                self.cli_service.destroy_threaded_session(session=session)
                raise Exception(self.__class__.__name__,
                                'Session cannot connect after {} sec.'.format(self._session_wait_timeout))
            try:
                self.logger.debug('Reconnect retry')
                session.connect(re_string=self._default_prompt)
                self.logger.debug('Session connected')
                break
            except:
                time.sleep(5)

    def send_config_command(self, command):
        return self.cli_service.send_config_command(command)

    def send_command(self, command):
        return self.cli_service.send_command(command)

    def update_firmware(self, remote_host, file_path, size_of_firmware):
        if not remote_host and not file_path:
            raise Exception('AireOSOperations', 'Configuration URL cannot be empty')
        if remote_host.endswith('/'):
            remote_host = remote_host[:-1]
        if str(file_path).startswith('/'):
            file_path = file_path[1:]

        url = '{0}/{1}'.format(remote_host, file_path)

        flow_template = OrderedDict()
        flow_template[save_restore.RESTORE_CONFIGURATION_MODE] = UrlParser.SCHEME
        flow_template[save_restore.RESTORE_CONFIGURATION_SERVERIP] = UrlParser.HOSTNAME
        flow_template[save_restore.RESTORE_CONFIGURATION_PORT] = UrlParser.PORT
        flow_template[save_restore.RESTORE_CONFIGURATION_PATH] = UrlParser.PATH
        flow_template[save_restore.RESTORE_CONFIGURATION_FILENAME] = UrlParser.FILENAME
        flow_template[save_restore.RESTORE_CONFIGURATION_USER] = UrlParser.USERNAME
        flow_template[save_restore.RESTORE_CONFIGURATION_PASSWORD] = UrlParser.PASSWORD


        # connection_dict = self._parse_url(url)
        #
        restore_flow = OrderedDict()
        datatype = 'code'
        restore_flow[save_restore.RESTORE_CONFIGURATION_DATATYPE] = datatype
        connection_dict = UrlParser.parse_url(url)
        self.logger.debug('Connection dict: ' + str(connection_dict))
        restore_flow.update(self._generate_flow(flow_template, connection_dict))
        self.logger.debug(restore_flow)
        execute_command_map(restore_flow, self.cli_service.send_command)

        expected_map = OrderedDict({r'[yY]/[nN]': lambda session: session.send_line('y')})
        error_map = OrderedDict({r'[Ee]rror:': 'Restore configuration error, see logs for details'})

        self.cli_service.send_command(save_restore.RESTORE_CONFIGURATION_START.get_command(), expected_map=expected_map,
                                      error_map=error_map)

    def _generate_flow(self, flow_dict, result_dict):
        flow = OrderedDict()
        for template, key in flow_dict.iteritems():
            if key in result_dict and result_dict[key]:
                flow[template] = str(result_dict[key])
        return flow

    def shutdown(self):
        pass


class UrlParser(object):
    SCHEME = 'scheme'
    NETLOC = 'netloc'
    PATH = 'path'
    FILENAME = 'filename'
    QUERY = 'query'
    FRAGMENT = 'fragment'
    USERNAME = 'username'
    PASSWORD = 'password'
    HOSTNAME = 'hostname'
    PORT = 'port'

    @staticmethod
    def parse_url(url):
        parsed = urlsplit(url)
        result = {}
        for attr in dir(UrlParser):
            if attr.isupper() and not attr.startswith('_'):
                attr_value = getattr(UrlParser, attr)
                if hasattr(parsed, attr_value):
                    value = getattr(parsed, attr_value)
                    if attr_value == UrlParser.PATH:
                        path, filename = os.path.split(value)
                        result[UrlParser.PATH] = path
                        result[UrlParser.FILENAME] = filename
                    else:
                        result[attr_value] = value
        return result
