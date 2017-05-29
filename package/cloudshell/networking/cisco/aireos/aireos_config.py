from collections import OrderedDict

from cloudshell.cli.session.session_creator import SessionCreator
from cloudshell.cli.session.session_proxy import ReturnToPoolProxy
from cloudshell.configuration.cloudshell_cli_configuration import CONNECTION_TYPE_SSH
from cloudshell.networking.cisco.aireos.cli.aireos_ssh_session import AireOSSSHSession
from cloudshell.shell.core.context_utils import get_attribute_by_name_wrapper, \
    get_resource_address, get_attribute_by_name, get_decrypted_password_by_attribute_name_wrapper
from cloudshell.shell.core.dependency_injection.context_based_logger import get_logger_with_thread_id
from cloudshell.configuration.cloudshell_cli_configuration import CONNECTION_MAP

"""Definition for SSH session"""
ssh_session = SessionCreator(AireOSSSHSession)
ssh_session.proxy = ReturnToPoolProxy
ssh_session.kwargs = {'username': get_attribute_by_name_wrapper('User'),
                      'password': get_decrypted_password_by_attribute_name_wrapper('Password'),
                      'host': get_resource_address}
CONNECTION_MAP[CONNECTION_TYPE_SSH] = ssh_session

CONNECTION_EXPECTED_MAP = OrderedDict({r'[Uu]ser:': lambda session: session.send_line(get_attribute_by_name('User')),
                                       r'[Pp]assword:': lambda session: session.send_line(
                                           get_decrypted_password_by_attribute_name_wrapper('Password')())})

GET_LOGGER_FUNCTION = get_logger_with_thread_id

DEFAULT_PROMPT = r'[>$#]\s*$'
CONFIG_MODE_PROMPT = DEFAULT_PROMPT

ENTER_CONFIG_MODE_PROMPT_COMMAND = ''
EXIT_CONFIG_MODE_PROMPT_COMMAND = ''

COMMIT_COMMAND = ''
ROLLBACK_COMMAND = ''

HE_MAX_READ_RETRIES = 10

ERROR_MAP = OrderedDict({r'[Ee]rror:': 'Command error, see logs for details'})

POOL_TIMEOUT = 600

SUPPORTED_OS = [r'[Cc]ontroller']
