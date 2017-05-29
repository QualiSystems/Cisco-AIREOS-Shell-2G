from cloudshell.networking.cisco.aireos.aireos_bootstrap import AireOSBootstrap
from cloudshell.networking.cisco.aireos.operations.aireos_operations import AireOSOperations
from cloudshell.networking.networking_resource_driver_interface import NetworkingResourceDriverInterface
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context_utils import ContextFromArgsMeta
import cloudshell.networking.cisco.aireos.aireos_config as driver_config
from cloudshell.networking.cisco.aireos.operations.aireos_autoload import AireOSAutoload


class AireOSResourceDriver(ResourceDriverInterface, NetworkingResourceDriverInterface, GlobalLock):
    __metaclass__ = ContextFromArgsMeta

    def __init__(self, config=None):
        super(AireOSResourceDriver, self).__init__()
        self._autoload = None
        self._connectivity = None
        self._operations = None
        bootstrap = AireOSBootstrap()
        bootstrap.add_config(driver_config)
        if config:
            bootstrap.add_config(config)
        bootstrap.initialize()

    @property
    def autoload(self):
        return AireOSAutoload()

    @property
    def operations(self):
        if self._operations is None:
            self._operations = AireOSOperations()
        return self._operations

    def get_inventory(self, context):
        return self.autoload.discover()

    def send_custom_command(self, context, command):
        return self.operations.send_command(command)

    @GlobalLock.lock
    def update_firmware(self, context, remote_host, file_path):
        return self.operations.update_firmware(remote_host, file_path, None)

    def shutdown(self, context):
        pass

    def ApplyConnectivityChanges(self, context, request):
        pass

    def send_custom_config_command(self, context, command):
        return self._operations.send_config_command(command)

    @GlobalLock.lock
    def restore(self, context, path, config_type, restore_method):
        return self.operations.restore_configuration(path, config_type, restore_method)

    def save(self, context, folder_path, configuration_type):
        return self.operations.save_configuration(folder_path, configuration_type)

    def initialize(self, context):
        pass

    def cleanup(self):
        pass
