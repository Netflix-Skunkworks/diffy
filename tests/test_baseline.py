import pytest
import json
from diffy_api.baseline.views import *  # noqa


@pytest.mark.parametrize("token,status", [("", 200)])
def test_baseline_list_get(client, token, status):
    assert client.get(api.url_for(BaselineList), headers=token).status_code == status


@pytest.mark.parametrize("token,status", [("", 400)])
def test_baseline_list_post(client, token, status, sts):
    assert (
        client.post(api.url_for(BaselineList), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_list_put(client, token, status):
    assert (
        client.put(api.url_for(BaselineList), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_list_delete(client, token, status):
    assert client.delete(api.url_for(BaselineList), headers=token).status_code == status


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_list_patch(client, token, status):
    assert (
        client.patch(api.url_for(BaselineList), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 200)])
def test_baseline_get(client, token, status):
    assert (
        client.get(api.url_for(Baseline, key="foo"), headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_post(client, token, status):
    assert (
        client.post(
            api.url_for(Baseline, key="foo"), data={}, headers=token
        ).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_put(client, token, status):
    assert (
        client.put(api.url_for(Baseline, key="foo"), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_delete(client, token, status):
    assert (
        client.delete(api.url_for(Baseline, key="foo"), headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_baseline_patch(client, token, status):
    assert (
        client.patch(
            api.url_for(Baseline, key="foo"), data={}, headers=token
        ).status_code
        == status
    )
