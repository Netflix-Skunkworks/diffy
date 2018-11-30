import pytest
from diffy_api.analysis.views import *  # noqa


@pytest.mark.parametrize("token,status", [("", 200)])
def test_analysis_list_get(client, token, status):
    assert client.get(api.url_for(AnalysisList), headers=token).status_code == status


@pytest.mark.parametrize("token,status", [("", 400)])
def test_analysis_list_post(client, token, status, sts):
    assert (
        client.post(api.url_for(AnalysisList), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_list_put(client, token, status):
    assert (
        client.put(api.url_for(AnalysisList), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_list_delete(client, token, status):
    assert client.delete(api.url_for(AnalysisList), headers=token).status_code == status


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_list_patch(client, token, status):
    assert (
        client.patch(api.url_for(AnalysisList), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 200)])
def test_analysis_get(client, token, status):
    assert (
        client.get(api.url_for(Analysis, key="foo"), headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_post(client, token, status):
    assert (
        client.post(
            api.url_for(Analysis, key="foo"), data={}, headers=token
        ).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_put(client, token, status):
    assert (
        client.put(api.url_for(Analysis, key="foo"), data={}, headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_delete(client, token, status):
    assert (
        client.delete(api.url_for(Analysis, key="foo"), headers=token).status_code
        == status
    )


@pytest.mark.parametrize("token,status", [("", 405)])
def test_analysis_patch(client, token, status):
    assert (
        client.patch(
            api.url_for(Analysis, key="foo"), data={}, headers=token
        ).status_code
        == status
    )
