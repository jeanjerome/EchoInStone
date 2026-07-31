"""Tests for the log levels applied to third-party libraries.

The pipeline's own progress lines are what a run is read for, and they compete
with request-level chatter from the libraries underneath. The carve-out for
DEBUG is the part worth pinning: quieting those libraries unconditionally
would take the detail away from the level meant to expose it.
"""

import logging

import pytest

from EchoInStone.utils import configure_logging


@pytest.fixture(autouse=True)
def restore_httpx_level():
    """Log levels are process-wide, so put back whatever was there."""
    logger = logging.getLogger("httpx")
    previous = logger.level
    yield
    logger.setLevel(previous)


class TestExternalLoggers:
    """How much the libraries under the pipeline are allowed to say."""

    def test_quiets_httpx_at_info(self):
        """Resolving a model costs dozens of INFO lines before any audio is read."""
        logging.getLogger("httpx").setLevel(logging.NOTSET)

        configure_logging(logging.INFO)

        assert logging.getLogger("httpx").level == logging.WARNING

    def test_leaves_httpx_alone_in_debug(self):
        """DEBUG is chosen precisely to see the traffic underneath."""
        logging.getLogger("httpx").setLevel(logging.NOTSET)

        configure_logging(logging.DEBUG)

        assert logging.getLogger("httpx").level == logging.NOTSET
