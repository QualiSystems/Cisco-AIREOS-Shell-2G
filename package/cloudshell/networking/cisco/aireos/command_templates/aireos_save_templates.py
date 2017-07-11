from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

SAVE_ACTION_MAP = OrderedDict({r'[yY]/[nN]': lambda session, logger: session.send_line('y', logger)})

SAVE_ERROR_MAP = OrderedDict(
    {r'[Ee]rror:|[Ii]ncorrect\s+([Ii]nput|[Uu]sage)': 'Save configuration error, see logs for details'})

SAVE_CONFIGURATION_DATA_TYPE = CommandTemplate('transfer upload datatype {data_type}', action_map=SAVE_ACTION_MAP,
                                               error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_MODE = CommandTemplate('transfer upload mode {mode}', action_map=SAVE_ACTION_MAP,
                                          error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_SERVER_IP = CommandTemplate('transfer upload serverip {server_ip}', action_map=SAVE_ACTION_MAP,
                                               error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_PORT = CommandTemplate('transfer upload serverport {port}', action_map=SAVE_ACTION_MAP,
                                          error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_USER = CommandTemplate('transfer upload username {user}', action_map=SAVE_ACTION_MAP,
                                          error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_PASSWORD = CommandTemplate('transfer upload password {password}', action_map=SAVE_ACTION_MAP,
                                              error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_PATH = CommandTemplate('transfer upload path {path}', action_map=SAVE_ACTION_MAP,
                                          error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_FILENAME = CommandTemplate('transfer upload filename {filename}', action_map=SAVE_ACTION_MAP,
                                              error_map=SAVE_ERROR_MAP)

SAVE_CONFIGURATION_START = CommandTemplate('transfer upload start', action_map=SAVE_ACTION_MAP,
                                           error_map=SAVE_ERROR_MAP)
