from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.cisco.aireos.command_templates import aireos_general_templates


class AireosGeneralActions(object):
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

    def run_command(self, command, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                       aireos_general_templates.RUN_COMMAND,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(command=command)
