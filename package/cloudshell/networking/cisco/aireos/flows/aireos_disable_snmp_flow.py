#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.networking.cisco.aireos.command_actions.aireos_enbl_disbl_snmp_actions import \
    AireosEnableDisableSnmpActions
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters


class CiscoAireosDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
          Enable snmp flow
          :param cli_handler:
          :type cli_handler: JuniperCliHandler
          :param logger:
          :return:
          """
        super(CiscoAireosDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters=None):
        if isinstance(snmp_parameters, SNMPV3Parameters):
            self._logger.debug("Unsupported SNMP version. Disable SNMP skipped")
        else:
            with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
                with session.enter_mode(self._cli_handler.config_mode) as config_session:
                    snmp_actions = AireosEnableDisableSnmpActions(config_session, self._logger)
                    self._logger.debug("Start Disable SNMP")
                    snmp_actions.disable_snmp(snmp_parameters.snmp_community)
