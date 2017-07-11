#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.devices.flows.cli_action_flows import BaseCliFlow
from cloudshell.networking.cisco.aireos.command_actions.aireos_general_actions import AireosGeneralActions


class AireosRunCommandFlow(BaseCliFlow):
    def __init__(self, cli_handler, logger):
        super(AireosRunCommandFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, custom_command="", is_config=False):
        """ Execute flow which run custom command on device

        :param custom_command: the command to execute on device
        :param is_config: if True then run command in configuration mode
        :return: command execution output
        """

        responses = []
        if isinstance(custom_command, str):
            commands = [custom_command]
        elif isinstance(custom_command, tuple):
            commands = list(custom_command)
        else:
            commands = custom_command

        if is_config:
            mode = self._cli_handler.config_mode
            if not mode:
                raise Exception(self.__class__.__name__,
                                "CliHandler configuration is missing. Config Mode has to be defined")
        else:
            mode = self._cli_handler.enable_mode
            if not mode:
                raise Exception(self.__class__.__name__,
                                "CliHandler configuration is missing. Enable Mode has to be defined")

        with self._cli_handler.get_cli_service(mode) as session:
            general_actions = AireosGeneralActions(session, self._logger)
            for cmd in commands:
                responses.append(general_actions.run_command(cmd))
        return '\n'.join(responses)
