"""Projects mixin for Bitbucket client."""

import logging
from typing import TYPE_CHECKING

from mcp_atlassian.models.bitbucket import BitbucketProject

if TYPE_CHECKING:
    from .client import BitbucketClient

logger = logging.getLogger("mcp-bitbucket.projects")


class ProjectsMixin:
    """Mixin providing project-related operations for BitbucketClient."""

    def get_projects(
        self: "BitbucketClient",
        limit: int | None = None,
        start: int = 0,
    ) -> list[BitbucketProject]:
        """Get all accessible projects.

        Args:
            limit: Maximum number of projects to return
            start: Starting index for pagination

        Returns:
            List of BitbucketProject objects
        """
        projects = []

        try:
            for project_data in self.bitbucket.project_list(start=start, limit=limit):
                project = BitbucketProject.from_api_response(project_data)
                projects.append(project)

                # Apply project filter if configured
                if self.config.projects_filter:
                    allowed_keys = {
                        k.strip().upper()
                        for k in self.config.projects_filter.split(",")
                    }
                    if project.key.upper() not in allowed_keys:
                        projects.pop()
                        continue

                if limit and len(projects) >= limit:
                    break
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            raise

        return projects

    def get_project(self: "BitbucketClient", project_key: str) -> BitbucketProject:
        """Get a specific project by key.

        Args:
            project_key: The project key

        Returns:
            BitbucketProject object

        Raises:
            ValueError: If project not found
        """
        try:
            project_data = self.bitbucket.project(project_key)
            if not project_data:
                raise ValueError(f"Project '{project_key}' not found")
            return BitbucketProject.from_api_response(project_data)
        except Exception as e:
            logger.error(f"Error fetching project {project_key}: {e}")
            raise

    def project_exists(self: "BitbucketClient", project_key: str) -> bool:
        """Check if a project exists.

        Args:
            project_key: The project key

        Returns:
            True if project exists, False otherwise
        """
        return self.bitbucket.project_exists(project_key)
