"""Bitbucket repository models."""

from typing import Any

from ..base import ApiModel
from ..constants import EMPTY_STRING, UNKNOWN
from .project import BitbucketProject


class BitbucketRepository(ApiModel):
    """Model representing a Bitbucket repository."""

    id: int | None = None
    slug: str = EMPTY_STRING
    name: str = UNKNOWN
    description: str | None = None
    scm_id: str = "git"
    state: str = "AVAILABLE"
    status_message: str | None = None
    forkable: bool = True
    public: bool = False
    project: BitbucketProject | None = None
    links: dict[str, list[dict[str, str]]] | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketRepository":
        """Convert an API response to a BitbucketRepository instance.

        Args:
            data: The API response data
            **kwargs: Additional context parameters

        Returns:
            A BitbucketRepository instance
        """
        if not data:
            return cls()

        project_data = data.get("project")
        project = (
            BitbucketProject.from_api_response(project_data) if project_data else None
        )

        return cls(
            id=data.get("id"),
            slug=data.get("slug", EMPTY_STRING),
            name=data.get("name", UNKNOWN),
            description=data.get("description"),
            scm_id=data.get("scmId", "git"),
            state=data.get("state", "AVAILABLE"),
            status_message=data.get("statusMessage"),
            forkable=data.get("forkable", True),
            public=data.get("public", False),
            project=project,
            links=data.get("links"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "slug": self.slug,
            "name": self.name,
            "scm": self.scm_id,
            "state": self.state,
            "forkable": self.forkable,
            "public": self.public,
        }
        if self.id:
            result["id"] = self.id
        if self.description:
            result["description"] = self.description
        if self.project:
            result["project"] = {
                "key": self.project.key,
                "name": self.project.name,
            }
        if self.links:
            if "clone" in self.links:
                result["clone_urls"] = {
                    link.get("name"): link.get("href")
                    for link in self.links["clone"]
                    if link.get("name")
                }
            if "self" in self.links and self.links["self"]:
                result["url"] = self.links["self"][0].get("href")
        return result


class BitbucketBranch(ApiModel):
    """Model representing a Bitbucket branch."""

    id: str = EMPTY_STRING
    display_id: str = EMPTY_STRING
    type: str = "BRANCH"
    latest_commit: str | None = None
    latest_changeset: str | None = None
    is_default: bool = False

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketBranch":
        """Convert an API response to a BitbucketBranch instance.

        Args:
            data: The API response data
            **kwargs: Additional context parameters

        Returns:
            A BitbucketBranch instance
        """
        if not data:
            return cls()

        return cls(
            id=data.get("id", EMPTY_STRING),
            display_id=data.get("displayId", EMPTY_STRING),
            type=data.get("type", "BRANCH"),
            latest_commit=data.get("latestCommit"),
            latest_changeset=data.get("latestChangeset"),
            is_default=data.get("isDefault", False),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "id": self.id,
            "name": self.display_id,
            "type": self.type,
            "is_default": self.is_default,
        }
        if self.latest_commit:
            result["latest_commit"] = self.latest_commit
        return result
