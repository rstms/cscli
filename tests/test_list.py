#!/usr/bin/env python

"""Tests for command/cmd_list.py module"""

from cscli.error import ParameterError


def test_list_help(runner):
    """Test cscli list --help"""
    result = runner("--debug", "list", "--help")
    assert "Usage: cscli list" in result.output


def test_list_all_default(runner):
    runner("list")


def test_list_all_detail(runner):
    runner("list", "--detail")


def test_list_all_uuid(runner):
    runner("list", "--uuid")


def test_list_all_brief(runner):
    runner("list", "--brief")


def test_list_all_text(runner):
    runner("list", "--text")


def test_list_servers_default(runner):
    runner("list", "servers")


def test_list_servers_detail(runner):
    runner("list", "--detail", "servers")


def test_list_servers_uuid(runner):
    runner("list", "--uuid", "servers")


def test_list_servers_brief(runner):
    runner("list", "--brief", "servers")


def test_list_servers_text(runner):
    runner("list", "--text", "servers")


def test_list_drives_default(runner):
    runner("list", "drives")


def test_list_drives_detail(runner):
    runner("list", "--detail", "drives")


def test_list_drives_uuid(runner):
    runner("list", "--uuid", "drives")


def test_list_drives_brief(runner):
    runner("list", "--brief", "drives")


def test_list_drives_text(runner):
    runner("list", "--text", "drives")


def test_list_ips_default(runner):
    runner("list", "ips")


def test_list_ips_detail(runner):
    runner("list", "--detail", "ips")


def test_list_ips_uuid(runner):
    runner("list", "--uuid", "ips")


def test_list_ips_brief(runner):
    runner("list", "--brief", "ips")


def test_list_ips_text(runner):
    runner("list", "--text", "ips")


def test_list_vlans_default(runner):
    runner("list", "vlans")


def test_list_vlans_detail(runner):
    runner("list", "--detail", "vlans")


def test_list_vlans_uuid(runner):
    runner("list", "--uuid", "vlans")


def test_list_vlans_brief(runner):
    runner("list", "--brief", "vlans")


def test_list_vlans_text(runner):
    runner("list", "--text", "vlans")


def test_list_subscriptions_default(runner):
    runner("list", "subscriptions")


def test_list_subscriptions_detail(runner):
    runner("list", "--detail", "subscriptions")


def test_list_subscriptions_uuid(runner):
    runner("list", "--uuid", "subscriptions")


def test_list_subscriptions_brief(runner):
    runner("list", "--brief", "subscriptions", raises=ParameterError)


def test_list_subscriptions_text(runner):
    runner("list", "--text", "subscriptions", raises=ParameterError)


def test_list_capabilities_default(runner):
    runner("list", "capabilities")


def test_list_capabilities_detail(runner):
    runner("list", "--detail", "capabilities")


def test_list_capabilities_uuid(runner):
    runner("list", "--uuid", "capabilities", raises=ParameterError)


def test_list_capabilities_brief(runner):
    runner("list", "--brief", "capabilities", raises=ParameterError)


def test_list_capabilities_text(runner):
    runner("list", "--text", "capabilities", raises=ParameterError)
