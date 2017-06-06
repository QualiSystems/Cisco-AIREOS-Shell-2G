#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.cisco.aireos.command_templates import aireos_enbl_disbl_snmp


class AireosEnableDisableSnmpActions(object):
    READ_ONLY = "ro"
    READ_WRITE = "rw"

    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    @staticmethod
    def get_current_snmp_communities(cli_service, action_map=None, error_map=None):
        """Retrieve current snmp communities

        :param cli_service: session
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        return CommandTemplateExecutor(cli_service=cli_service,
                                       command_template=aireos_enbl_disbl_snmp.SHOW_SNMP_COMMUNITY,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def create_snmp(self, snmp_community, action_map=None, error_map=None):
        """Enable SNMP on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=aireos_enbl_disbl_snmp.CREATE_SNMP,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_community=snmp_community)

    def set_snmp_access(self, snmp_community, is_read_only_community=True, action_map=None, error_map=None):
        """Enable SNMP on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        access_mode = self.READ_WRITE
        if is_read_only_community:
            access_mode = self.READ_ONLY
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=aireos_enbl_disbl_snmp.SET_SNMP_ACCESS,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_community=snmp_community,
                                                                            access_mode=access_mode)

    def enable_snmp(self, snmp_community, action_map=None, error_map=None):
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=aireos_enbl_disbl_snmp.ENABLE_SNMP,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_community=snmp_community)

    def disable_snmp(self, snmp_community, action_map=None, error_map=None):
        """Disable SNMP on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=aireos_enbl_disbl_snmp.DISABLE_SNMP,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_community=snmp_community)
