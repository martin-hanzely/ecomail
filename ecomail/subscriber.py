from dataclasses import dataclass, asdict

from ecomail.exceptions import SubscriberError


def is_empty_or_whitespace(string: str) -> bool:
    """
    Checks if provided string is empty or whitespace.
    """
    return string.isspace() or (len(string) == 0)


# Require keyword arguments and make objects frozen.
@dataclass(kw_only=True, frozen=True)
class Subscriber:
    """
    Subscriber contact data.
    Requires keyword arguments.
    Frozen class (values cannot be reassigned).
    """
    name: str
    surname: str
    email: str
    phone: str | None = None

    def __post_init__(self) -> None:
        """
        Post-init processing. Raises SubscriberError if email adress is empty string.
        """
        if is_empty_or_whitespace(self.email):
            # TODO: Improve email validation.
            raise SubscriberError("Email address cannot be empty string.")

    def as_dict(self) -> dict[str, str]:
        """
        Returns object as dict. Skips empty attributes.
        """
        return {k: str(v) for k, v in asdict(self).items() if v}