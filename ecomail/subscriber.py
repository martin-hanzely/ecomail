from dataclasses import dataclass, asdict

from ecomail.exceptions import SubscriberError
from ecomail.utils import is_empty_or_whitespace


# Require keyword arguments and make objects frozen.
@dataclass(kw_only=True, frozen=True)
class Subscriber:
    """
    Subscriber contact data. Requires keyword arguments. Frozen class (values cannot be reassigned).
    """
    name: str
    surname: str
    email: str
    phone: str | None = None
    country: str | None = None  # ISO 3166-1 two letter country code.

    def __post_init__(self) -> None:
        """
        Post-init processing. Raises SubscriberError if email address is empty string.
        """
        # Country validation.
        if country := self.country:
            if (not isinstance(country, str)) or (len(country) != 2):
                raise SubscriberError("Country must be ISO 3166-1 two letter country code.")
        # TODO: Improve email validation.
        if is_empty_or_whitespace(self.email):
            raise SubscriberError("Email address cannot be empty string.")

    def as_dict(self) -> dict[str, str]:
        """
        Returns object as dict. Skips empty attributes.
        """
        return {k: str(v) for k, v in asdict(self).items() if v}
