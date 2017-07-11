from collections import OrderedDict
from cloudshell.cli.session.ssh_session import SSHSession


class AireOSSSHSession(SSHSession):
    def _connect_actions(self, prompt, logger):
        """Connect to device through ssh
        :param prompt: expected string in output
        :param logger: logger
        """

        connect_action_map = OrderedDict(
            {r'[Uu]ser:': lambda session, s_logger: session.send_line(self.username, s_logger),
             r'[Pp]assword:': lambda session, s_logger: session.send_line(self.password, s_logger)})
        self.hardware_expect(None, expected_string=prompt, action_map=connect_action_map, timeout=self._timeout,
                             logger=logger)
        self._on_session_start(logger)
