#!/usr/bin/env python

"""conftest.py"""

from pprint import pprint

import pytest
from click.testing import CliRunner

from cscli import cli


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
