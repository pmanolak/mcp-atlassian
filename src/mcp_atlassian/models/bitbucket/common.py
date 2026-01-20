"""Common Bitbucket models shared across different modules."""

from typing import Any

from ..base import ApiModel
from ..constants import EMPTY_STRING, UNKNOWN


class BitbucketUser(ApiModel):
    """Model representing a Bitbucket user."""

    name: str = UNKNOWN
    email_address: str | None = None
    display_name: str = UNKNOWN
    active: bool = True
    slug: str = EMPTY_STRING
    id: int | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "BitbucketUser":
        """Convert an API response to a BitbucketUser instance.

        Args:
            data: The API response data
            **kwargs: Additional context parameters

        Returns:
            A BitbucketUser instance
        """
        if not data:
            return cls()

        return cls(
            name=data.get("name", UNKNOWN),
            email_address=data.get("emailAddress"),
            display_name=data.get("displayName", data.get("name", UNKNOWN)),
            active=data.get("active", True),
            slug=data.get("slug", data.get("name", EMPTY_STRING)),
            id=data.get("id"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "name": self.name,
            "display_name": self.display_name,
            "active": self.active,
        }
        if self.email_address:
            result["email"] = self.email_address
        if self.slug:
            result["slug"] = self.slug
        if self.id:
            result["id"] = self.id
        return result


class BitbucketLink(ApiModel):
    """Model representing a Bitbucket link."""

    href: str = EMPTY_STRING
    name: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "BitbucketLink":
        """Convert an API response to a BitbucketLink instance."""
        if not data:
            return cls()

        return cls(
            href=data.get("href", EMPTY_STRING),
            name=data.get("name"),
        )
