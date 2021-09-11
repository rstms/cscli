# cli tests

def test_cli(cli_runner):
    result = cli_runner.invoke(project, ["--help"])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
