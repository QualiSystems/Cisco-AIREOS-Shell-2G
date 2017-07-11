#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template import CommandTemplate

SHOW_SNMP_COMMUNITY = CommandTemplate("show snmpcommunity")
CREATE_SNMP = CommandTemplate("snmp community create {snmp_community}")
ENABLE_SNMP = CommandTemplate("snmp community mode enable {snmp_community}")
SET_SNMP_ACCESS = CommandTemplate("snmp community accessmode {access_mode} {snmp_community}")
DISABLE_SNMP = CommandTemplate("snmp community delete {snmp_community}")
