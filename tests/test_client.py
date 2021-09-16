from pprint import pprint

import pytest

from cscli.api_client import CloudSigmaClient


@pytest.fixture()
def api():
    return CloudSigmaClient()


def test_client_init(api):
    assert api


all_keys = ["servers", "drives", "ips", "vlans", "capabilities", "subscriptions"]


def _verify(ret, keys):
    pprint(ret)
    assert ret
    assert isinstance(ret, dict)
    for key, value in ret.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        assert key in keys
        for resource in value:
            assert isinstance(resource, dict)


@pytest.mark.vcr()
def test_client_list_servers_none(api):
    _verify(api.list_servers(None), ["servers"])


@pytest.mark.vcr()
def test_client_list_drives_none(api):
    _verify(api.list_drives(None), ["drives"])


@pytest.mark.vcr()
def test_client_list_ips_none(api):
    _verify(api.list_ips(None), ["ips"])


@pytest.mark.vcr()
def test_client_list_vlans_none(api):
    _verify(api.list_vlans(None), ["vlans"])


@pytest.mark.vcr()
def test_client_list_capabilities_none(api):
    _verify(api.list_capabilities(None), ["capabilities"])


@pytest.mark.vcr()
def test_client_list_subscriptions_none(api):
    _verify(api.list_subscriptions(None), ["subscriptions"])


@pytest.mark.vcr()
def test_client_list_all_none(api):
    _verify(api.list_all(None), all_keys)


@pytest.mark.vcr()
def test_client_list_servers_detail(api):
    _verify(api.list_servers("detail"), ["servers"])


@pytest.mark.vcr()
def test_client_list_drives_detail(api):
    _verify(api.list_drives("detail"), ["drives"])


@pytest.mark.vcr()
def test_client_list_ips_detail(api):
    _verify(api.list_ips("detail"), ["ips"])


@pytest.mark.vcr()
def test_client_list_vlans_detail(api):
    _verify(api.list_vlans("detail"), ["vlans"])


@pytest.mark.vcr()
def test_client_list_capabilities_detail(api):
    _verify(api.list_capabilities("detail"), ["capabilities"])


@pytest.mark.vcr()
def test_client_list_subscriptions_detail(api):
    _verify(api.list_subscriptions("detail"), ["subscriptions"])


@pytest.mark.vcr()
def test_client_list_all_detail(api):
    _verify(api.list_all("detail"), all_keys)


@pytest.mark.vcr()
def test_client_list_servers_brief(api):
    _verify(api.list_servers("brief"), ["servers"])


@pytest.mark.vcr()
def test_client_list_drives_brief(api):
    _verify(api.list_drives("brief"), ["drives"])


@pytest.mark.vcr()
def test_client_list_ips_brief(api):
    _verify(api.list_ips("brief"), ["ips"])


@pytest.mark.vcr()
def test_client_list_vlans_brief(api):
    _verify(api.list_vlans("brief"), ["vlans"])


@pytest.mark.vcr()
def test_client_list_capabilities_brief(api):
    _verify(api.list_capabilities("brief"), ["capabilities"])


@pytest.mark.vcr()
def test_client_list_subscriptions_brief(api):
    _verify(api.list_subscriptions("brief"), ["subscriptions"])


@pytest.mark.vcr()
def test_client_list_all_brief(api):
    _verify(api.list_all("brief"), all_keys)


@pytest.mark.vcr()
def test_client_list_servers_uuid(api):
    _verify(api.list_servers("uuid"), ["servers"])


@pytest.mark.vcr()
def test_client_list_drives_uuid(api):
    _verify(api.list_drives("uuid"), ["drives"])


@pytest.mark.vcr()
def test_client_list_ips_uuid(api):
    _verify(api.list_ips("uuid"), ["ips"])


@pytest.mark.vcr()
def test_client_list_vlans_uuid(api):
    _verify(api.list_vlans("uuid"), ["vlans"])


@pytest.mark.vcr()
def test_client_list_capabilities_uuid(api):
    _verify(api.list_capabilities("uuid"), ["capabilities"])


@pytest.mark.vcr()
def test_client_list_subscriptions_uuid(api):
    _verify(api.list_subscriptions("uuid"), ["subscriptions"])


@pytest.mark.vcr()
def test_client_list_all_uuid(api):
    _verify(api.list_all("uuid"), all_keys)


@pytest.mark.vcr()
def test_client_list_servers_text(api):
    _verify(api.list_servers("text"), ["servers"])


@pytest.mark.vcr()
def test_client_list_drives_text(api):
    _verify(api.list_drives("text"), ["drives"])


@pytest.mark.vcr()
def test_client_list_ips_text(api):
    _verify(api.list_ips("text"), ["ips"])


@pytest.mark.vcr()
def test_client_list_vlans_text(api):
    _verify(api.list_vlans("text"), ["vlans"])


@pytest.mark.vcr()
def test_client_list_capabilities_text(api):
    _verify(api.list_capabilities("text"), ["capabilities"])


@pytest.mark.vcr()
def test_client_list_subscriptions_text(api):
    _verify(api.list_subscriptions("text"), ["subscriptions"])


@pytest.mark.vcr()
def test_client_list_all_text(api):
    _verify(api.list_all("text"), all_keys)
