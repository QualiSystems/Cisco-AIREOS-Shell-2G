from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

DEFAULT_ACTION_MAP = OrderedDict({r'[yY]/[nN]': lambda session, logger: session.send_line('y', logger),
                                  r"[Pp]ress\s+[Ee]nter\s+to\s+continue": lambda session,
                                                                                 logger: session.send_line('', logger)})

DEFAULT_ERROR_MAP = OrderedDict(
    {r'[Ee]rror:|[Ii]ncorrect\s+([Ii]nput|[Uu]sage)': 'Command error, see logs for details'})

RUN_COMMAND = CommandTemplate('{command}', action_map=DEFAULT_ACTION_MAP, error_map=DEFAULT_ERROR_MAP)
