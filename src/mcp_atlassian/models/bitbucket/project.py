"""Bitbucket project models."""

from typing import Any

from ..base import ApiModel
from ..constants import EMPTY_STRING, UNKNOWN


class BitbucketProject(ApiModel):
    """Model representing a Bitbucket project."""

    id: int | None = None
    key: str = EMPTY_STRING
    name: str = UNKNOWN
    description: str | None = None
    public: bool = False
    type: str = "NORMAL"
    links: dict[str, list[dict[str, str]]] | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketProject":
        """Convert an API response to a BitbucketProject instance.

        Args:
            data: The API response data
            **kwargs: Additional context parameters

        Returns:
            A BitbucketProject instance
        """
        if not data:
            return cls()

        return cls(
            id=data.get("id"),
            key=data.get("key", EMPTY_STRING),
            name=data.get("name", UNKNOWN),
            description=data.get("description"),
            public=data.get("public", False),
            type=data.get("type", "NORMAL"),
            links=data.get("links"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "key": self.key,
            "name": self.name,
            "public": self.public,
            "type": self.type,
        }
        if self.id:
            result["id"] = self.id
        if self.description:
            result["description"] = self.description
        if self.links and "self" in self.links:
            result["url"] = (
                self.links["self"][0].get("href") if self.links["self"] else None
            )
        return result
