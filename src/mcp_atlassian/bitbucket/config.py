"""Configuration module for Bitbucket Server/Data Center API interactions."""

import logging
import os
from dataclasses import dataclass
from typing import Literal

from ..utils.env import get_custom_headers, is_env_ssl_verify


@dataclass
class BitbucketConfig:
    """Bitbucket Server/Data Center API configuration.

    Handles authentication for Bitbucket Server/Data Center:
    - Personal access token (PAT) - preferred for Server/DC
    - Basic auth with username/password
    """

    url: str  # Base URL for Bitbucket Server
    auth_type: Literal["basic", "pat"]  # Authentication type
    username: str | None = None  # Username for basic auth
    api_token: str | None = None  # Password/API token for basic auth
    personal_token: str | None = None  # Personal access token (Server/DC)
    ssl_verify: bool = True  # Whether to verify SSL certificates
    projects_filter: str | None = None  # Comma-separated list of project keys to filter
    http_proxy: str | None = None  # HTTP proxy URL
    https_proxy: str | None = None  # HTTPS proxy URL
    no_proxy: str | None = None  # Comma-separated list of hosts to bypass proxy
    socks_proxy: str | None = None  # SOCKS proxy URL (optional)
    custom_headers: dict[str, str] | None = None  # Custom HTTP headers

    @classmethod
    def from_env(cls) -> "BitbucketConfig":
        """Create configuration from environment variables.

        Returns:
            BitbucketConfig with values from environment variables

        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        url = os.getenv("BITBUCKET_URL")
        if not url:
            error_msg = "Missing required BITBUCKET_URL environment variable"
            raise ValueError(error_msg)

        # Determine authentication type based on available environment variables
        username = os.getenv("BITBUCKET_USERNAME")
        api_token = os.getenv("BITBUCKET_API_TOKEN")
        personal_token = os.getenv("BITBUCKET_PERSONAL_TOKEN")

        auth_type = None

        # Bitbucket Server/Data Center authentication
        if personal_token:
            auth_type = "pat"
        elif username and api_token:
            auth_type = "basic"
        else:
            error_msg = (
                "Bitbucket Server/Data Center authentication requires "
                "BITBUCKET_PERSONAL_TOKEN or BITBUCKET_USERNAME and BITBUCKET_API_TOKEN"
            )
            raise ValueError(error_msg)

        # SSL verification
        ssl_verify = is_env_ssl_verify("BITBUCKET_SSL_VERIFY")

        # Get the projects filter if provided
        projects_filter = os.getenv("BITBUCKET_PROJECTS_FILTER")

        # Proxy settings
        http_proxy = os.getenv("BITBUCKET_HTTP_PROXY", os.getenv("HTTP_PROXY"))
        https_proxy = os.getenv("BITBUCKET_HTTPS_PROXY", os.getenv("HTTPS_PROXY"))
        no_proxy = os.getenv("BITBUCKET_NO_PROXY", os.getenv("NO_PROXY"))
        socks_proxy = os.getenv("BITBUCKET_SOCKS_PROXY", os.getenv("SOCKS_PROXY"))

        # Custom headers - service-specific only
        custom_headers = get_custom_headers("BITBUCKET_CUSTOM_HEADERS")

        return cls(
            url=url,
            auth_type=auth_type,
            username=username,
            api_token=api_token,
            personal_token=personal_token,
            ssl_verify=ssl_verify,
            projects_filter=projects_filter,
            http_proxy=http_proxy,
            https_proxy=https_proxy,
            no_proxy=no_proxy,
            socks_proxy=socks_proxy,
            custom_headers=custom_headers,
        )

    def is_auth_configured(self) -> bool:
        """Check if the current authentication configuration is complete and valid.

        Returns:
            bool: True if authentication is fully configured, False otherwise.
        """
        logger = logging.getLogger("mcp-atlassian.bitbucket.config")
        if self.auth_type == "pat":
            return bool(self.personal_token)
        elif self.auth_type == "basic":
            return bool(self.username and self.api_token)
        logger.warning(
            f"Unknown or unsupported auth_type: {self.auth_type} in BitbucketConfig"
        )
        return False
