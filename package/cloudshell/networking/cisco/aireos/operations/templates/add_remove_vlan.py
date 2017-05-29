from cloudshell.cli.command_template.command_template import CommandTemplate

CREATE_VLAN_INTERFACE = CommandTemplate('config interface create {0} {1}', [r'.+', r'.+'],
                                        ['Wrong interface name', 'Wrong vlan id'])
CONFIGURE_INTERFACE_PORT = CommandTemplate('config interface port {0} {1}', [r'.+', r'.+'],
                                           ['Wrong interface name', 'Wrong port name'])
DELETE_INTERFACE = CommandTemplate('config interface delete {0}', [r'.+'], ['Wrong interface name'])
INTERFACE_SUMMARY = CommandTemplate('show interface summary')
