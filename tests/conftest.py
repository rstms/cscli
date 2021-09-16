#!/usr/bin/env python

"""conftest.py"""

import os
from pprint import pprint

import pytest
from click.testing import CliRunner

from cscli import cli

# tests use pytest-vcr to record/replay API interaction
# to perform live tests against the API, valid credentials are required
# use --vcr-record=all to create new recordings
# use --vcr-record=none to use stored recordings
# when using recordings, these environment vars are set
DUMMY_API_AUTH = {
    "CLOUDSIGMA_USERNAME": "user@example.org",
    "CLOUDSIGMA_PASSWORD": "$uper$ecret",
    "CLOUDSIGMA_REGION": "sjc",
}


@pytest.fixture(scope="session", autouse=True)
def api_config_vars():
    for var, value in DUMMY_API_AUTH.items():
        if var not in os.environ:
            os.environ[var] = value


# don't save password in pytest-vcr recordings
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "DUMMY")],
    }


class FixtureRunner:
    def __init__(self):
        self.runner = None

    def invoke(self, *args, **kwargs):
        expected_exit_code = kwargs.get("expected_exit_code", 0)
        expected_exception = kwargs.get("raises", None)

        assert isinstance(args, (list, tuple))
        print(f"invoking: {repr(args)}")
        args = list(args)
        args.insert(0, "--debug")
        ret = self.runner.invoke(cli.cli, args)
        pprint(ret)
        if expected_exception:
            assert ret.exception
            assert isinstance(ret.exception, expected_exception)
        else:
            assert ret.exit_code == expected_exit_code
        return ret

    def __enter__(self):
        self.runner = CliRunner()
        print(f"\nstartup {self.runner}")
        return self.invoke

    def __exit__(self, *args, **kwargs):
        print(f"\nteardown {self.runner}")
        self.runner = None
        return False


@pytest.fixture
def runner():
    with FixtureRunner() as _runner:
        yield _runner
