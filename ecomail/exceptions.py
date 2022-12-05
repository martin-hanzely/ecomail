class EcoMailError(Exception):
    """
    Generic EcoMail service exception.
    """


class ApiConnectionError(EcoMailError):
    """
    Service connection error.
    """


class SubscriberError(EcoMailError):
    """
    Subscriber error.
    """
