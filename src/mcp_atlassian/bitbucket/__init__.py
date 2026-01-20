"""Bitbucket Server/Data Center API client module.

This module provides a complete client for interacting with Bitbucket Server/DC APIs,
including projects, repositories, branches, and pull requests.
"""

from .client import BitbucketClient
from .config import BitbucketConfig
from .projects import ProjectsMixin
from .pull_requests import PullRequestsMixin
from .repositories import RepositoriesMixin


class BitbucketFetcher(
    ProjectsMixin,
    RepositoriesMixin,
    PullRequestsMixin,
    BitbucketClient,
):
    """Complete Bitbucket client combining all operation mixins.

    Provides methods for:
    - Project operations (list, get)
    - Repository operations (list, get, file content, branches)
    - Pull request operations (list, get, diff, comments)
    """

    pass


__all__ = [
    "BitbucketClient",
    "BitbucketConfig",
    "BitbucketFetcher",
    "ProjectsMixin",
    "PullRequestsMixin",
    "RepositoriesMixin",
]
