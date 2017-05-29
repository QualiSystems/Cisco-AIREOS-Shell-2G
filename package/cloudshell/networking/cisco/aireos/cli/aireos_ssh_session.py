import inject

from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER, CONFIG
from cloudshell.shell.core.config_utils import get_config_attribute_or_none


class AireOSSSHSession(SSHSession):

    @inject.params(logger=LOGGER, config=CONFIG)
    def connect(self, re_string='', logger=None, config=None):
        """
            Connect to device through ssh
            :param re_string: regular expression of end of output
            :return: str
        """

        # logger.debug("Host: {0}, port: {1}, username: {2}, password: {3}, timeout: {4}".
        #              format(self._host, self._port, self._username, self._password, self._timeout))
        # try:
        self._handler.connect(self._host, self._port, self._username, self._password, timeout=self._timeout,
                                  banner_timeout=30, allow_agent=False, look_for_keys=False)
        # except Exception as e:
        #     logger.error(traceback.format_exc())
        #     raise Exception('SSHSession', 'Failed to open connection to device: {0}'.format(e.message))

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        connection_expected_map = get_config_attribute_or_none('CONNECTION_EXPECTED_MAP', config)
        output = self.hardware_expect(re_string=re_string, expect_map=connection_expected_map, timeout=self._timeout)
        logger.info(output)
        self._default_actions()

        return output