from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

RESTORE_ACTION_MAP = OrderedDict({r'[yY]/[nN]': lambda session, logger: session.send_line('y', logger)})

RESTORE_ERROR_MAP = OrderedDict(
    {r'[Ee]rror:|[Ii]ncorrect\s+([Ii]nput|[Uu]sage)': 'Restore configuration error, see logs for details'})

RESTORE_CONFIGURATION_DATA_TYPE = CommandTemplate('transfer download datatype {data_type}',
                                                  action_map=RESTORE_ACTION_MAP,
                                                  error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_MODE = CommandTemplate('transfer download mode {mode}', action_map=RESTORE_ACTION_MAP,
                                             error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_SERVER_IP = CommandTemplate('transfer download serverip {server_ip}',
                                                  action_map=RESTORE_ACTION_MAP,
                                                  error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_PORT = CommandTemplate('transfer download serverport {port}', action_map=RESTORE_ACTION_MAP,
                                             error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_USER = CommandTemplate('transfer download username {user}', action_map=RESTORE_ACTION_MAP,
                                             error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_PASSWORD = CommandTemplate('transfer download password {password}', action_map=RESTORE_ACTION_MAP,
                                                 error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_PATH = CommandTemplate('transfer download path {path}', action_map=RESTORE_ACTION_MAP,
                                             error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_FILENAME = CommandTemplate('transfer download filename {filename}', action_map=RESTORE_ACTION_MAP,
                                                 error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_START = CommandTemplate('transfer download start', action_map=RESTORE_ACTION_MAP,
                                              error_map=RESTORE_ERROR_MAP)

RESTORE_CONFIGURATION_SAVE_TO_NVRAM = CommandTemplate('save config', action_map=RESTORE_ACTION_MAP,
                                                      error_map=RESTORE_ERROR_MAP)

RELOAD = CommandTemplate('reset system', action_map=RESTORE_ACTION_MAP, error_map=RESTORE_ERROR_MAP)
