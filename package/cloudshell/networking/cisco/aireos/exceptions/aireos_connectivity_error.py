

class AireosConnectivityError(Exception):
    def __init__(self, raiser, message, *args, **kwargs):
        super(Exception, self).__init__(raiser, message, *args, **kwargs)
        self.message = message
