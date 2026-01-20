"""Bitbucket FastMCP server instance and tool definitions."""

import json
import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from mcp_atlassian.servers.dependencies import get_bitbucket_fetcher
from mcp_atlassian.utils.decorators import check_write_access

logger = logging.getLogger(__name__)

bitbucket_mcp = FastMCP(
    name="Bitbucket MCP Service",
    instructions="Provides tools for interacting with Bitbucket Server/Data Center.",
)


# ============================================================================
# Project Tools
# ============================================================================


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def list_projects(
    ctx: Context,
    limit: Annotated[
        int | None,
        Field(description="Maximum number of projects to return", default=None),
    ] = None,
) -> str:
    """List all accessible Bitbucket projects.

    Args:
        ctx: The FastMCP context.
        limit: Maximum number of projects to return.

    Returns:
        JSON string representing the list of projects.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        projects = bitbucket.get_projects(limit=limit)
        result = {
            "success": True,
            "count": len(projects),
            "projects": [p.to_simplified_dict() for p in projects],
        }
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        result = {"success": False, "error": str(e)}
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def get_project(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
) -> str:
    """Get details of a specific Bitbucket project.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.

    Returns:
        JSON string representing the project details.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        project = bitbucket.get_project(project_key)
        result = {"success": True, "project": project.to_simplified_dict()}
    except Exception as e:
        logger.error(f"Error getting project {project_key}: {e}")
        result = {"success": False, "error": str(e), "project_key": project_key}
    return json.dumps(result, indent=2, ensure_ascii=False)


# ============================================================================
# Repository Tools
# ============================================================================


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def list_repositories(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    limit: Annotated[
        int | None,
        Field(description="Maximum number of repositories to return", default=None),
    ] = None,
) -> str:
    """List all repositories in a Bitbucket project.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        limit: Maximum number of repositories to return.

    Returns:
        JSON string representing the list of repositories.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        repos = bitbucket.get_repositories(project_key, limit=limit)
        result = {
            "success": True,
            "project_key": project_key,
            "count": len(repos),
            "repositories": [r.to_simplified_dict() for r in repos],
        }
    except Exception as e:
        logger.error(f"Error listing repositories for {project_key}: {e}")
        result = {"success": False, "error": str(e), "project_key": project_key}
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def get_repository(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
) -> str:
    """Get details of a specific Bitbucket repository.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.

    Returns:
        JSON string representing the repository details.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        repo = bitbucket.get_repository(project_key, repository_slug)
        result = {"success": True, "repository": repo.to_simplified_dict()}
    except Exception as e:
        logger.error(f"Error getting repository {project_key}/{repository_slug}: {e}")
        result = {
            "success": False,
            "error": str(e),
            "project_key": project_key,
            "repository_slug": repository_slug,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def get_file_content(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    file_path: Annotated[
        str,
        Field(description="Path to the file in the repository (e.g., 'src/main.py')"),
    ],
    at: Annotated[
        str | None,
        Field(
            description=(
                "Optional ref (branch, tag, or commit) to get the file at. "
                "Defaults to the default branch."
            ),
            default=None,
        ),
    ] = None,
) -> str:
    """Get the content of a file from a Bitbucket repository.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        file_path: Path to the file.
        at: Optional ref to get the file at.

    Returns:
        JSON string with the file content.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        content = bitbucket.get_file_content(
            project_key, repository_slug, file_path, at=at
        )
        result = {
            "success": True,
            "file_path": file_path,
            "ref": at or "default",
            "content": content,
        }
    except Exception as e:
        logger.error(
            f"Error getting file {file_path} from {project_key}/{repository_slug}: {e}"
        )
        result = {
            "success": False,
            "error": str(e),
            "file_path": file_path,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def list_branches(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    filter_text: Annotated[
        str | None,
        Field(description="Optional text to filter branches by name", default=None),
    ] = None,
    limit: Annotated[
        int | None,
        Field(description="Maximum number of branches to return", default=None),
    ] = None,
) -> str:
    """List branches in a Bitbucket repository.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        filter_text: Optional text to filter branches.
        limit: Maximum number of branches to return.

    Returns:
        JSON string representing the list of branches.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        branches = bitbucket.get_branches(
            project_key, repository_slug, filter_text=filter_text, limit=limit
        )
        result = {
            "success": True,
            "project_key": project_key,
            "repository_slug": repository_slug,
            "count": len(branches),
            "branches": [b.to_simplified_dict() for b in branches],
        }
    except Exception as e:
        logger.error(f"Error listing branches for {project_key}/{repository_slug}: {e}")
        result = {
            "success": False,
            "error": str(e),
            "project_key": project_key,
            "repository_slug": repository_slug,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


# ============================================================================
# Pull Request Tools
# ============================================================================


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def list_pull_requests(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    state: Annotated[
        str,
        Field(
            description="Filter by state: OPEN, MERGED, DECLINED, or ALL",
            default="OPEN",
        ),
    ] = "OPEN",
    limit: Annotated[
        int | None,
        Field(description="Maximum number of pull requests to return", default=None),
    ] = None,
) -> str:
    """List pull requests in a Bitbucket repository.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        state: Filter by PR state.
        limit: Maximum number of PRs to return.

    Returns:
        JSON string representing the list of pull requests.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        prs = bitbucket.get_pull_requests(
            project_key, repository_slug, state=state, limit=limit
        )
        result = {
            "success": True,
            "project_key": project_key,
            "repository_slug": repository_slug,
            "state": state,
            "count": len(prs),
            "pull_requests": [pr.to_simplified_dict() for pr in prs],
        }
    except Exception as e:
        logger.error(
            f"Error listing pull requests for {project_key}/{repository_slug}: {e}"
        )
        result = {
            "success": False,
            "error": str(e),
            "project_key": project_key,
            "repository_slug": repository_slug,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def get_pull_request(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    pull_request_id: Annotated[int, Field(description="The pull request ID")],
) -> str:
    """Get details of a specific pull request.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        pull_request_id: The PR ID.

    Returns:
        JSON string representing the pull request details.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        pr = bitbucket.get_pull_request(project_key, repository_slug, pull_request_id)
        result = {"success": True, "pull_request": pr.to_simplified_dict()}
    except Exception as e:
        repo = f"{project_key}/{repository_slug}"
        logger.error(f"Error getting PR {pull_request_id} from {repo}: {e}")
        result = {
            "success": False,
            "error": str(e),
            "pull_request_id": pull_request_id,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def get_pull_request_diff(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    pull_request_id: Annotated[int, Field(description="The pull request ID")],
) -> str:
    """Get the diff/changes for a pull request.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        pull_request_id: The PR ID.

    Returns:
        JSON string with the diff summary and changed files.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        diff = bitbucket.get_pull_request_diff(
            project_key, repository_slug, pull_request_id
        )
        changes = bitbucket.get_pull_request_changes(
            project_key, repository_slug, pull_request_id
        )
        result = {
            "success": True,
            "pull_request_id": pull_request_id,
            "diff_summary": diff,
            "changes": changes,
        }
    except Exception as e:
        repo = f"{project_key}/{repository_slug}"
        logger.error(f"Error getting diff for PR {pull_request_id} from {repo}: {e}")
        result = {
            "success": False,
            "error": str(e),
            "pull_request_id": pull_request_id,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "read"})
async def get_pull_request_comments(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    pull_request_id: Annotated[int, Field(description="The pull request ID")],
    limit: Annotated[
        int | None,
        Field(description="Maximum number of comments to return", default=None),
    ] = None,
) -> str:
    """Get comments on a pull request.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        pull_request_id: The PR ID.
        limit: Maximum number of comments to return.

    Returns:
        JSON string representing the list of comments.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        comments = bitbucket.get_pull_request_comments(
            project_key, repository_slug, pull_request_id, limit=limit
        )
        result = {
            "success": True,
            "pull_request_id": pull_request_id,
            "count": len(comments),
            "comments": [c.to_simplified_dict() for c in comments],
        }
    except Exception as e:
        repo = f"{project_key}/{repository_slug}"
        logger.error(f"Error getting comments for PR #{pull_request_id} in {repo}: {e}")
        result = {
            "success": False,
            "error": str(e),
            "pull_request_id": pull_request_id,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)


@bitbucket_mcp.tool(tags={"bitbucket", "write"})
@check_write_access
async def add_pull_request_comment(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'PROJ')")],
    repository_slug: Annotated[
        str, Field(description="The repository slug (e.g., 'my-repo')")
    ],
    pull_request_id: Annotated[int, Field(description="The pull request ID")],
    text: Annotated[str, Field(description="The comment text")],
    parent_id: Annotated[
        int | None,
        Field(
            description="Optional parent comment ID for replies",
            default=None,
        ),
    ] = None,
) -> str:
    """Add a comment to a pull request.

    Args:
        ctx: The FastMCP context.
        project_key: The project key.
        repository_slug: The repository slug.
        pull_request_id: The PR ID.
        text: The comment text.
        parent_id: Optional parent comment ID for replies.

    Returns:
        JSON string representing the created comment.
    """
    bitbucket = await get_bitbucket_fetcher(ctx)
    try:
        comment = bitbucket.add_pull_request_comment(
            project_key, repository_slug, pull_request_id, text, parent_id=parent_id
        )
        result = {"success": True, "comment": comment.to_simplified_dict()}
    except Exception as e:
        repo = f"{project_key}/{repository_slug}"
        logger.error(f"Error adding comment to PR {pull_request_id} in {repo}: {e}")
        result = {
            "success": False,
            "error": str(e),
            "pull_request_id": pull_request_id,
        }
    return json.dumps(result, indent=2, ensure_ascii=False)
