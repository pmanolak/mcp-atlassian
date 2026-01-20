"""Repositories mixin for Bitbucket client."""

import logging
from typing import TYPE_CHECKING

from mcp_atlassian.models.bitbucket import BitbucketBranch, BitbucketRepository

if TYPE_CHECKING:
    from .client import BitbucketClient

logger = logging.getLogger("mcp-bitbucket.repositories")


class RepositoriesMixin:
    """Mixin providing repository-related operations for BitbucketClient."""

    def get_repositories(
        self: "BitbucketClient",
        project_key: str,
        limit: int | None = None,
        start: int = 0,
    ) -> list[BitbucketRepository]:
        """Get all repositories in a project.

        Args:
            project_key: The project key
            limit: Maximum number of repositories to return
            start: Starting index for pagination

        Returns:
            List of BitbucketRepository objects
        """
        repositories = []

        try:
            for repo_data in self.bitbucket.repo_list(
                project_key, start=start, limit=limit or 25
            ):
                repo = BitbucketRepository.from_api_response(repo_data)
                repositories.append(repo)

                if limit and len(repositories) >= limit:
                    break
        except Exception as e:
            logger.error(f"Error fetching repositories for project {project_key}: {e}")
            raise

        return repositories

    def get_repository(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
    ) -> BitbucketRepository:
        """Get a specific repository.

        Args:
            project_key: The project key
            repository_slug: The repository slug

        Returns:
            BitbucketRepository object

        Raises:
            ValueError: If repository not found
        """
        try:
            repo_data = self.bitbucket.get_repo(project_key, repository_slug)
            if not repo_data:
                msg = f"Repository '{repository_slug}' not found in '{project_key}'"
                raise ValueError(msg)
            return BitbucketRepository.from_api_response(repo_data)
        except Exception as e:
            logger.error(
                f"Error fetching repository {project_key}/{repository_slug}: {e}"
            )
            raise

    def repository_exists(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
    ) -> bool:
        """Check if a repository exists.

        Args:
            project_key: The project key
            repository_slug: The repository slug

        Returns:
            True if repository exists, False otherwise
        """
        return self.bitbucket.repo_exists(project_key, repository_slug)

    def get_file_content(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        file_path: str,
        at: str | None = None,
    ) -> str:
        """Get the content of a file from a repository.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            file_path: Path to the file in the repository
            at: Optional ref (branch, tag, or commit) to get the file at

        Returns:
            File content as string

        Raises:
            ValueError: If file not found
        """
        try:
            content = self.bitbucket.get_content_of_file(
                project_key, repository_slug, file_path, at=at
            )
            if content is None:
                raise ValueError(
                    f"File '{file_path}' not found in {project_key}/{repository_slug}"
                )
            # Content is returned as bytes, decode to string
            if isinstance(content, bytes):
                return content.decode("utf-8")
            return str(content)
        except Exception as e:
            repo_path = f"{project_key}/{repository_slug}"
            logger.error(f"Error fetching file {file_path} from {repo_path}: {e}")
            raise

    def get_branches(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        filter_text: str | None = None,
        limit: int | None = None,
        start: int = 0,
        order_by: str = "MODIFICATION",
    ) -> list[BitbucketBranch]:
        """Get branches in a repository.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            filter_text: Optional text to filter branches by
            limit: Maximum number of branches to return
            start: Starting index for pagination
            order_by: Order by MODIFICATION or ALPHABETICAL

        Returns:
            List of BitbucketBranch objects
        """
        branches = []

        try:
            for branch_data in self.bitbucket.get_branches(
                project_key,
                repository_slug,
                filter=filter_text,
                start=start,
                limit=limit,
                order_by=order_by,
            ):
                branch = BitbucketBranch.from_api_response(branch_data)
                branches.append(branch)

                if limit and len(branches) >= limit:
                    break
        except Exception as e:
            logger.error(
                f"Error fetching branches for {project_key}/{repository_slug}: {e}"
            )
            raise

        return branches

    def get_default_branch(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
    ) -> BitbucketBranch | None:
        """Get the default branch of a repository.

        Args:
            project_key: The project key
            repository_slug: The repository slug

        Returns:
            BitbucketBranch object or None if not found
        """
        try:
            branch_data = self.bitbucket.get_default_branch(
                project_key, repository_slug
            )
            if not branch_data:
                return None
            return BitbucketBranch.from_api_response(branch_data)
        except Exception as e:
            repo_path = f"{project_key}/{repository_slug}"
            logger.error(f"Error fetching default branch for {repo_path}: {e}")
            raise

    def get_file_list(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        path: str | None = None,
        at: str | None = None,
        limit: int | None = None,
        start: int = 0,
    ) -> list[str]:
        """Get list of files in a repository directory.

        Args:
            project_key: The project key
            repository_slug: The repository slug
            path: Optional subdirectory path
            at: Optional ref (branch, tag, or commit)
            limit: Maximum number of files to return
            start: Starting index for pagination

        Returns:
            List of file paths
        """
        files = []

        try:
            for file_path in self.bitbucket.get_file_list(
                project_key,
                repository_slug,
                sub_folder=path,
                query=at,
                start=start,
                limit=limit,
            ):
                files.append(file_path)

                if limit and len(files) >= limit:
                    break
        except Exception as e:
            logger.error(
                f"Error fetching file list for {project_key}/{repository_slug}: {e}"
            )
            raise

        return files

    def create_repository(
        self: "BitbucketClient",
        project_key: str,
        repository_slug: str,
        description: str | None = None,
        forkable: bool = True,
        public: bool = False,
    ) -> BitbucketRepository:
        """Create a new repository in a project.

        Args:
            project_key: The project key (e.g., 'PROJ' or '~username' for personal)
            repository_slug: The repository slug/name
            description: Optional repository description
            forkable: Whether the repository can be forked (default: True)
            public: Whether the repository is public (default: False)

        Returns:
            BitbucketRepository object representing the created repository

        Raises:
            ValueError: If repository creation fails
        """
        try:
            repo_data = self.bitbucket.create_repo(
                project_key,
                repository_slug,
                forkable=forkable,
                is_private=not public,
            )
            if not repo_data:
                raise ValueError(
                    f"Failed to create repository '{repository_slug}' in '{project_key}'"
                )

            # If description is provided, update the repository
            if description:
                repo_data = self.bitbucket.update_repo(
                    project_key,
                    repository_slug,
                    description=description,
                )

            return BitbucketRepository.from_api_response(repo_data)
        except Exception as e:
            logger.error(
                f"Error creating repository {project_key}/{repository_slug}: {e}"
            )
            raise
