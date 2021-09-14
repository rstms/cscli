#!/usr/bin/env python

import pytest

"""Tests for `cscli` package."""


@pytest.mark.vcr()
def test_cli_init(runner):
    """Test the CLI."""
    result = runner(expected_exit_code=2)
    assert "Error: Missing command." in result.output


@pytest.mark.vcr()
def test_cli_help(runner):
    """Test top-level --help"""
    help_result = runner("--help")
    assert "Usage: cscli [OPTIONS] COMMAND [ARGS]..." in help_result.output
