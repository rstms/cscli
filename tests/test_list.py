#!/usr/bin/env python

"""Tests for command/cmd_list.py module"""
import pytest

from cscli.error import ParameterError


@pytest.mark.vcr()
def test_list_help(runner):
    """Test cscli list --help"""
    result = runner("--debug", "list", "--help")
    assert "Usage: cscli list" in result.output


@pytest.mark.vcr()
def test_list_all_default(runner):
    runner("list")


@pytest.mark.vcr()
def test_list_all_detail(runner):
    runner("list", "--detail")


@pytest.mark.vcr()
def test_list_all_uuid(runner):
    runner("list", "--uuid")


@pytest.mark.vcr()
def test_list_all_brief(runner):
    runner("list", "--brief")


@pytest.mark.vcr()
def test_list_all_text(runner):
    runner("list", "--text")


@pytest.mark.vcr()
def test_list_servers_default(runner):
    runner("list", "servers")


@pytest.mark.vcr()
def test_list_servers_detail(runner):
    runner("list", "--detail", "servers")


@pytest.mark.vcr()
def test_list_servers_uuid(runner):
    runner("list", "--uuid", "servers")


@pytest.mark.vcr()
def test_list_servers_brief(runner):
    runner("list", "--brief", "servers")


@pytest.mark.vcr()
def test_list_servers_text(runner):
    runner("list", "--text", "servers")


@pytest.mark.vcr()
def test_list_drives_default(runner):
    runner("list", "drives")


@pytest.mark.vcr()
def test_list_drives_detail(runner):
    runner("list", "--detail", "drives")


@pytest.mark.vcr()
def test_list_drives_uuid(runner):
    runner("list", "--uuid", "drives")


@pytest.mark.vcr()
def test_list_drives_brief(runner):
    runner("list", "--brief", "drives")


@pytest.mark.vcr()
def test_list_drives_text(runner):
    runner("list", "--text", "drives")


@pytest.mark.vcr()
def test_list_ips_default(runner):
    runner("list", "ips")


@pytest.mark.vcr()
def test_list_ips_detail(runner):
    runner("list", "--detail", "ips")


@pytest.mark.vcr()
def test_list_ips_uuid(runner):
    runner("list", "--uuid", "ips")


@pytest.mark.vcr()
def test_list_ips_brief(runner):
    runner("list", "--brief", "ips")


@pytest.mark.vcr()
def test_list_ips_text(runner):
    runner("list", "--text", "ips")


@pytest.mark.vcr()
def test_list_vlans_default(runner):
    runner("list", "vlans")


@pytest.mark.vcr()
def test_list_vlans_detail(runner):
    runner("list", "--detail", "vlans")


@pytest.mark.vcr()
def test_list_vlans_uuid(runner):
    runner("list", "--uuid", "vlans")


@pytest.mark.vcr()
def test_list_vlans_brief(runner):
    runner("list", "--brief", "vlans")


@pytest.mark.vcr()
def test_list_vlans_text(runner):
    runner("list", "--text", "vlans")


@pytest.mark.vcr()
def test_list_subscriptions_default(runner):
    runner("list", "subscriptions")


@pytest.mark.vcr()
def test_list_subscriptions_detail(runner):
    runner("list", "--detail", "subscriptions")


@pytest.mark.vcr()
def test_list_subscriptions_uuid(runner):
    runner("list", "--uuid", "subscriptions")


@pytest.mark.vcr()
def test_list_subscriptions_brief(runner):
    runner("list", "--brief", "subscriptions", raises=ParameterError)


@pytest.mark.vcr()
def test_list_subscriptions_text(runner):
    runner("list", "--text", "subscriptions", raises=ParameterError)


@pytest.mark.vcr()
def test_list_capabilities_default(runner):
    runner("list", "capabilities")


@pytest.mark.vcr()
def test_list_capabilities_detail(runner):
    runner("list", "--detail", "capabilities")


@pytest.mark.vcr()
def test_list_capabilities_uuid(runner):
    runner("list", "--uuid", "capabilities", raises=ParameterError)


@pytest.mark.vcr()
def test_list_capabilities_brief(runner):
    runner("list", "--brief", "capabilities", raises=ParameterError)


@pytest.mark.vcr()
def test_list_capabilities_text(runner):
    runner("list", "--text", "capabilities", raises=ParameterError)
