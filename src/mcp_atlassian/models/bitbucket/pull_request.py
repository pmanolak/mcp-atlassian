"""Bitbucket pull request models."""

from typing import Any

from ..base import ApiModel, TimestampMixin
from ..constants import EMPTY_STRING, UNKNOWN
from .common import BitbucketUser
from .repository import BitbucketRepository


class BitbucketPullRequestRef(ApiModel):
    """Model representing a pull request source or target reference."""

    id: str = EMPTY_STRING
    display_id: str = EMPTY_STRING
    latest_commit: str | None = None
    repository: BitbucketRepository | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketPullRequestRef":
        """Convert an API response to a BitbucketPullRequestRef instance."""
        if not data:
            return cls()

        repo_data = data.get("repository")
        repository = (
            BitbucketRepository.from_api_response(repo_data) if repo_data else None
        )

        return cls(
            id=data.get("id", EMPTY_STRING),
            display_id=data.get("displayId", EMPTY_STRING),
            latest_commit=data.get("latestCommit"),
            repository=repository,
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "branch": self.display_id,
            "ref": self.id,
        }
        if self.latest_commit:
            result["commit"] = self.latest_commit
        if self.repository:
            result["repository"] = {
                "slug": self.repository.slug,
                "project": self.repository.project.key
                if self.repository.project
                else None,
            }
        return result


class BitbucketPullRequestParticipant(ApiModel):
    """Model representing a pull request participant (reviewer/approver)."""

    user: BitbucketUser | None = None
    role: str = "PARTICIPANT"
    approved: bool = False
    status: str = "UNAPPROVED"

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketPullRequestParticipant":
        """Convert an API response to a BitbucketPullRequestParticipant instance."""
        if not data:
            return cls()

        user_data = data.get("user")
        user = BitbucketUser.from_api_response(user_data) if user_data else None

        return cls(
            user=user,
            role=data.get("role", "PARTICIPANT"),
            approved=data.get("approved", False),
            status=data.get("status", "UNAPPROVED"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "role": self.role,
            "approved": self.approved,
            "status": self.status,
        }
        if self.user:
            result["user"] = self.user.to_simplified_dict()
        return result


class BitbucketPullRequest(ApiModel, TimestampMixin):
    """Model representing a Bitbucket pull request."""

    id: int | None = None
    version: int = 0
    title: str = UNKNOWN
    description: str | None = None
    state: str = "OPEN"
    open: bool = True
    closed: bool = False
    created_date: str | None = None
    updated_date: str | None = None
    closed_date: str | None = None
    from_ref: BitbucketPullRequestRef | None = None
    to_ref: BitbucketPullRequestRef | None = None
    locked: bool = False
    author: BitbucketPullRequestParticipant | None = None
    reviewers: list[BitbucketPullRequestParticipant] = []
    participants: list[BitbucketPullRequestParticipant] = []
    links: dict[str, list[dict[str, str]]] | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketPullRequest":
        """Convert an API response to a BitbucketPullRequest instance.

        Args:
            data: The API response data
            **kwargs: Additional context parameters

        Returns:
            A BitbucketPullRequest instance
        """
        if not data:
            return cls()

        from_ref_data = data.get("fromRef")
        from_ref = (
            BitbucketPullRequestRef.from_api_response(from_ref_data)
            if from_ref_data
            else None
        )

        to_ref_data = data.get("toRef")
        to_ref = (
            BitbucketPullRequestRef.from_api_response(to_ref_data)
            if to_ref_data
            else None
        )

        author_data = data.get("author")
        author = (
            BitbucketPullRequestParticipant.from_api_response(author_data)
            if author_data
            else None
        )

        reviewers = [
            BitbucketPullRequestParticipant.from_api_response(r)
            for r in data.get("reviewers", [])
        ]

        participants = [
            BitbucketPullRequestParticipant.from_api_response(p)
            for p in data.get("participants", [])
        ]

        # Convert timestamps from milliseconds to ISO format
        created_date = None
        if data.get("createdDate"):
            from datetime import datetime, timezone

            created_date = datetime.fromtimestamp(
                data["createdDate"] / 1000, tz=timezone.utc
            ).isoformat()

        updated_date = None
        if data.get("updatedDate"):
            from datetime import datetime, timezone

            updated_date = datetime.fromtimestamp(
                data["updatedDate"] / 1000, tz=timezone.utc
            ).isoformat()

        closed_date = None
        if data.get("closedDate"):
            from datetime import datetime, timezone

            closed_date = datetime.fromtimestamp(
                data["closedDate"] / 1000, tz=timezone.utc
            ).isoformat()

        return cls(
            id=data.get("id"),
            version=data.get("version", 0),
            title=data.get("title", UNKNOWN),
            description=data.get("description"),
            state=data.get("state", "OPEN"),
            open=data.get("open", True),
            closed=data.get("closed", False),
            created_date=created_date,
            updated_date=updated_date,
            closed_date=closed_date,
            from_ref=from_ref,
            to_ref=to_ref,
            locked=data.get("locked", False),
            author=author,
            reviewers=reviewers,
            participants=participants,
            links=data.get("links"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "id": self.id,
            "title": self.title,
            "state": self.state,
            "version": self.version,
        }
        if self.description:
            result["description"] = self.description
        if self.created_date:
            result["created_date"] = self.format_timestamp(self.created_date)
        if self.updated_date:
            result["updated_date"] = self.format_timestamp(self.updated_date)
        if self.closed_date:
            result["closed_date"] = self.format_timestamp(self.closed_date)
        if self.from_ref:
            result["source"] = self.from_ref.to_simplified_dict()
        if self.to_ref:
            result["target"] = self.to_ref.to_simplified_dict()
        if self.author:
            result["author"] = self.author.to_simplified_dict()
        if self.reviewers:
            result["reviewers"] = [r.to_simplified_dict() for r in self.reviewers]
        if self.links and "self" in self.links and self.links["self"]:
            result["url"] = self.links["self"][0].get("href")
        return result


class BitbucketComment(ApiModel, TimestampMixin):
    """Model representing a Bitbucket comment."""

    id: int | None = None
    version: int = 0
    text: str = EMPTY_STRING
    author: BitbucketUser | None = None
    created_date: str | None = None
    updated_date: str | None = None
    severity: str = "NORMAL"
    state: str = "OPEN"
    parent: "BitbucketComment | None" = None
    comments: list["BitbucketComment"] = []

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketComment":
        """Convert an API response to a BitbucketComment instance.

        Args:
            data: The API response data
            **kwargs: Additional context parameters

        Returns:
            A BitbucketComment instance
        """
        if not data:
            return cls()

        author_data = data.get("author")
        author = BitbucketUser.from_api_response(author_data) if author_data else None

        # Convert timestamps from milliseconds to ISO format
        created_date = None
        if data.get("createdDate"):
            from datetime import datetime, timezone

            created_date = datetime.fromtimestamp(
                data["createdDate"] / 1000, tz=timezone.utc
            ).isoformat()

        updated_date = None
        if data.get("updatedDate"):
            from datetime import datetime, timezone

            updated_date = datetime.fromtimestamp(
                data["updatedDate"] / 1000, tz=timezone.utc
            ).isoformat()

        # Handle nested comments
        nested_comments = [cls.from_api_response(c) for c in data.get("comments", [])]

        return cls(
            id=data.get("id"),
            version=data.get("version", 0),
            text=data.get("text", EMPTY_STRING),
            author=author,
            created_date=created_date,
            updated_date=updated_date,
            severity=data.get("severity", "NORMAL"),
            state=data.get("state", "OPEN"),
            comments=nested_comments,
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to a simplified dictionary for API responses."""
        result = {
            "id": self.id,
            "text": self.text,
            "version": self.version,
        }
        if self.author:
            result["author"] = self.author.to_simplified_dict()
        if self.created_date:
            result["created_date"] = self.format_timestamp(self.created_date)
        if self.updated_date:
            result["updated_date"] = self.format_timestamp(self.updated_date)
        if self.severity != "NORMAL":
            result["severity"] = self.severity
        if self.state != "OPEN":
            result["state"] = self.state
        if self.comments:
            result["replies"] = [c.to_simplified_dict() for c in self.comments]
        return result
