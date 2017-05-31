from collections import OrderedDict
from cloudshell.cli.session.ssh_session import SSHSession, paramiko, SSHSessionException


class AireOSSSHSession(SSHSession):
    def connect(self, prompt, logger):
        """Connect to device through ssh
        :param prompt: expected string in output
        :param logger: logger
        """

        if not self._handler:
            self._handler = paramiko.SSHClient()
            self._handler.load_system_host_keys()
            self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self._handler.connect(self.host, self.port, self.username, self.password, timeout=self._timeout,
                                  banner_timeout=30, allow_agent=False, look_for_keys=False, pkey=self.pkey)
        except Exception as e:
            logger.exception(e)
            raise SSHSessionException(self.__class__.__name__,
                                      'Failed to open connection to device: {0}'.format(e.message))

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        connect_action_map = OrderedDict(
            {r'[Uu]ser:': lambda session, s_logger: session.send_line(self.username, s_logger),
             r'[Pp]assword:': lambda session, s_logger: session.send_line(self.password, s_logger)})
        self.hardware_expect(None, expected_string=prompt, action_map=connect_action_map, timeout=self._timeout,
                             logger=logger)
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True
