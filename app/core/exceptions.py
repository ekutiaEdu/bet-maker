class ClientException(Exception):
    pass


class BetServiceException(Exception):
    pass


class EventNotFound(BetServiceException):
    pass
