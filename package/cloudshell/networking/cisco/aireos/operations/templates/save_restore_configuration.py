from cloudshell.cli.command_template.command_template import CommandTemplate

SAVE_CONFIGURATION_DATATYPE = CommandTemplate('transfer upload datatype {0}', [r'.+'],
                                              ['Wrong configuration type'])
SAVE_CONFIGURATION_MODE = CommandTemplate('transfer upload mode {0}', [r'.+'],
                                          ['Wrong upload mode'])
SAVE_CONFIGURATION_SERVERIP = CommandTemplate('transfer upload serverip {0}', [r'.+'],
                                              ['Wrong upload serverip'])
SAVE_CONFIGURATION_PORT = CommandTemplate('transfer upload port {0}', [r'.+'],
                                          ['Wrong upload port'])
SAVE_CONFIGURATION_USER = CommandTemplate('transfer upload username {0}', [r'.+'], ['Wrong upload username'])
SAVE_CONFIGURATION_PASSWORD = CommandTemplate('transfer upload password {0}', [r'.+'], ['Wrong upload password'])
SAVE_CONFIGURATION_PATH = CommandTemplate('transfer upload path {0}', [r'.+'],
                                          ['Wrong upload path'])
SAVE_CONFIGURATION_FILENAME = CommandTemplate('transfer upload filename {0}', [r'.+'],
                                              ['Wrong upload filename'])
SAVE_CONFIGURATION_START = CommandTemplate('transfer upload start')

RESTORE_CONFIGURATION_DATATYPE = CommandTemplate('transfer download datatype {0}', [r'.+'], ['Wrong download datatype'])
RESTORE_CONFIGURATION_MODE = CommandTemplate('transfer download mode {0}', [r'.+'], ['Wrong download mode'])
RESTORE_CONFIGURATION_SERVERIP = CommandTemplate('transfer download serverip {0}', [r'.+'],
                                                 ['Wrong download server address'])
RESTORE_CONFIGURATION_PORT = CommandTemplate('transfer download port {0}', [r'.+'], ['Wrong download server port'])
RESTORE_CONFIGURATION_USER = CommandTemplate('transfer download username {0}', [r'.+'], ['Wrong download username'])
RESTORE_CONFIGURATION_PASSWORD = CommandTemplate('transfer download password {0}', [r'.+'], ['Wrong download password'])

RESTORE_CONFIGURATION_PATH = CommandTemplate('transfer download path {0}', [r'.+'], ['Wrong download path'])
RESTORE_CONFIGURATION_FILENAME = CommandTemplate('transfer download filename {0}', [r'.+'], ['Wrong download filename'])
RESTORE_CONFIGURATION_START = CommandTemplate('transfer download start')
RESTORE_CONFIGURATION_SAVE_TO_NVRAM = CommandTemplate('save config')
