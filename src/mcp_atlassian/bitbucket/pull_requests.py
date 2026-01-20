"""Pull requests mixin for Bitbucket client."""

import logging
from typing import TYPE_CHECKING, Any

from mcp_atlassian.models.bitbucket import BitbucketComment, BitbucketPullRequest

if TYPE_CHECKING:
    from .client import BitbucketClient

logger = logging.getLogger("mcp-bitbucket.pull_requests")


class PullRequestsMixin:
    """Mixin providing pull request-related operations for BitbucketClient."""

    def get_pull_requests(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        state: str = "OPEN",
        order: str = "newest",
        limit: int | None = None,
        start: int = 0,
    ) -> list[BitbucketPullRequest]:
        """Get pull requests for a repository.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            state: Filter by state (OPEN, MERGED, DECLINED, ALL)
            order: Order by (newest, oldest)
            limit: Maximum number of pull requests to return
            start: Starting index for pagination

        Returns:
            List of BitbucketPullRequest objects
        """
        pull_requests = []

        try:
            for pr_data in self.bitbucket.get_pull_requests(
                project_key,
                repository_slug,
                state=state,
                order=order,
                start=start,
                limit=limit or 100,
            ):
                pr = BitbucketPullRequest.from_api_response(pr_data)
                pull_requests.append(pr)

                if limit and len(pull_requests) >= limit:
                    break
        except Exception as e:
            logger.error(
                f"Error fetching pull requests for {project_key}/{repository_slug}: {e}"
            )
            raise

        return pull_requests

    def get_pull_request(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        pull_request_id: int,
    ) -> BitbucketPullRequest:
        """Get a specific pull request.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            pull_request_id: The pull request ID

        Returns:
            BitbucketPullRequest object

        Raises:
            ValueError: If pull request not found
        """
        try:
            pr_data = self.bitbucket.get_pull_request(
                project_key, repository_slug, pull_request_id
            )
            if not pr_data:
                raise ValueError(
                    f"Pull request {pull_request_id} not found in "
                    f"{project_key}/{repository_slug}"
                )
            return BitbucketPullRequest.from_api_response(pr_data)
        except Exception as e:
            logger.error(
                f"Error fetching pull request {pull_request_id} "
                f"from {project_key}/{repository_slug}: {e}"
            )
            raise

    def get_pull_request_changes(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        pull_request_id: int,
        limit: int | None = None,
        start: int = 0,
    ) -> list[dict[str, Any]]:
        """Get the file changes in a pull request.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            pull_request_id: The pull request ID
            limit: Maximum number of changes to return
            start: Starting index for pagination

        Returns:
            List of change objects with file paths and change types
        """
        changes = []

        try:
            for change_data in self.bitbucket.get_pull_requests_changes(
                project_key,
                repository_slug,
                pull_request_id,
                start=start,
                limit=limit,
            ):
                # Simplify the change data
                change = {
                    "path": change_data.get("path", {}).get("toString", ""),
                    "type": change_data.get("type", "UNKNOWN"),
                    "src_path": change_data.get("srcPath", {}).get("toString")
                    if change_data.get("srcPath")
                    else None,
                }
                changes.append(change)

                if limit and len(changes) >= limit:
                    break
        except Exception as e:
            logger.error(
                f"Error fetching changes for PR {pull_request_id} "
                f"in {project_key}/{repository_slug}: {e}"
            )
            raise

        return changes

    def get_pull_request_diff(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        pull_request_id: int,
    ) -> str:
        """Get the diff for a pull request.

        Note: This returns a textual diff if available, otherwise returns
        a summary of changes.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            pull_request_id: The pull request ID

        Returns:
            Diff content as string
        """
        try:
            # Get the PR details first to get source and target refs
            pr = self.get_pull_request(project_key, repository_slug, pull_request_id)

            if not pr.from_ref or not pr.to_ref:
                raise ValueError("Pull request refs not available")

            # Get the diff between the branches
            source_commit = pr.from_ref.latest_commit
            target_commit = pr.to_ref.latest_commit

            if not source_commit or not target_commit:
                # Fall back to getting changes list
                changes = self.get_pull_request_changes(
                    project_key, repository_slug, pull_request_id
                )
                return "\n".join(f"{c['type']}: {c['path']}" for c in changes)

            # Get changes between the commits
            changes = self.get_pull_request_changes(
                project_key, repository_slug, pull_request_id
            )

            # Format as a simple diff summary
            diff_lines = [
                f"Pull Request #{pull_request_id}: {pr.title}",
                f"Source: {pr.from_ref.display_id} ({source_commit[:8]})",
                f"Target: {pr.to_ref.display_id} ({target_commit[:8]})",
                "",
                "Changed files:",
            ]
            for change in changes:
                diff_lines.append(f"  {change['type']}: {change['path']}")

            return "\n".join(diff_lines)

        except Exception as e:
            logger.error(
                f"Error fetching diff for PR {pull_request_id} "
                f"in {project_key}/{repository_slug}: {e}"
            )
            raise

    def get_pull_request_comments(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        pull_request_id: int,
        limit: int | None = None,
        start: int = 0,
    ) -> list[BitbucketComment]:
        """Get comments on a pull request.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            pull_request_id: The pull request ID
            limit: Maximum number of comments to return
            start: Starting index for pagination

        Returns:
            List of BitbucketComment objects
        """
        comments = []

        try:
            # Get activities which include comments
            for activity in self.bitbucket.get_pull_requests_activities(
                project_key,
                repository_slug,
                pull_request_id,
                start=start,
                limit=limit,
            ):
                # Filter to only comment activities
                if activity.get("action") == "COMMENTED":
                    comment_data = activity.get("comment")
                    if comment_data:
                        comment = BitbucketComment.from_api_response(comment_data)
                        comments.append(comment)

                        if limit and len(comments) >= limit:
                            break
        except Exception as e:
            logger.error(
                f"Error fetching comments for PR {pull_request_id} "
                f"in {project_key}/{repository_slug}: {e}"
            )
            raise

        return comments

    def add_pull_request_comment(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        pull_request_id: int,
        text: str,
        parent_id: int | None = None,
    ) -> BitbucketComment:
        """Add a comment to a pull request.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            pull_request_id: The pull request ID
            text: The comment text
            parent_id: Optional parent comment ID for replies

        Returns:
            The created BitbucketComment object
        """
        try:
            comment_data = self.bitbucket.add_pull_request_comment(
                project_key,
                repository_slug,
                pull_request_id,
                text,
                parent_id=parent_id,
            )
            if not comment_data:
                raise ValueError("Failed to create comment")
            return BitbucketComment.from_api_response(comment_data)
        except Exception as e:
            logger.error(
                f"Error adding comment to PR {pull_request_id} "
                f"in {project_key}/{repository_slug}: {e}"
            )
            raise

    def get_pull_request_commits(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        pull_request_id: int,
        limit: int | None = None,
        start: int = 0,
    ) -> list[dict[str, Any]]:
        """Get commits in a pull request.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            pull_request_id: The pull request ID
            limit: Maximum number of commits to return
            start: Starting index for pagination

        Returns:
            List of commit objects
        """
        commits = []

        try:
            for commit_data in self.bitbucket.get_pull_requests_commits(
                project_key,
                repository_slug,
                pull_request_id,
                start=start,
                limit=limit,
            ):
                commit = {
                    "id": commit_data.get("id"),
                    "display_id": commit_data.get("displayId"),
                    "message": commit_data.get("message"),
                    "author": {
                        "name": commit_data.get("author", {}).get("name"),
                        "email": commit_data.get("author", {}).get("emailAddress"),
                    }
                    if commit_data.get("author")
                    else None,
                    "committer": {
                        "name": commit_data.get("committer", {}).get("name"),
                        "email": commit_data.get("committer", {}).get("emailAddress"),
                    }
                    if commit_data.get("committer")
                    else None,
                }
                commits.append(commit)

                if limit and len(commits) >= limit:
                    break
        except Exception as e:
            logger.error(
                f"Error fetching commits for PR {pull_request_id} "
                f"in {project_key}/{repository_slug}: {e}"
            )
            raise

        return commits
