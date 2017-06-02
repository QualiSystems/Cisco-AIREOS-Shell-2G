#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.networking.cisco.aireos.command_actions.aireos_enbl_disbl_snmp_actions import \
    AireosEnableDisableSnmpActions
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters


class CiscoAireosEnableSnmpFlow(EnableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
        Enable snmp flow
        :param cli_handler:
        :param logger:
        :return:
        """
        super(CiscoAireosEnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters):
        if isinstance(snmp_parameters, SNMPV3Parameters):
            message = 'Unsupported SNMP version'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        if not snmp_parameters.snmp_community:
            message = 'SNMP community cannot be empty'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        read_only_community = True

        if isinstance(snmp_parameters, SNMPV2WriteParameters):
            read_only_community = False

        snmp_community = snmp_parameters.snmp_community
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            current_snmp_config = AireosEnableDisableSnmpActions.get_current_snmp_communities(session)
            with session.enter_mode(self._cli_handler.config_mode) as config_session:

                snmp_actions = AireosEnableDisableSnmpActions(config_session, self._logger)

                current_snmp_config = re.sub("^.*-+|\s+\(.*", "", current_snmp_config, flags=(re.DOTALL))
                if snmp_community not in current_snmp_config:
                    snmp_actions.create_snmp(snmp_community)
                    snmp_actions.set_snmp_access(snmp_community, read_only_community)
                    snmp_actions.enable_snmp(snmp_community)
                else:
                    self._logger.debug("SNMP Community '{}' already configured".format(snmp_community))

