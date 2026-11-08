import os
import socket, pytest, requests

WANIKANI_API_HOST = "https://api.wanikani.com/v2"
HTTPS_PORT = 443
TIMEOUT = 5

@pytest.fixture(scope="session")
def network_fixture():
    """Verify network access to the Wanikani API before running tests."""
    host = WANIKANI_API_HOST.split("//")[-1].split("/")[0]
    try:
        with socket.create_connection((host, HTTPS_PORT), timeout=TIMEOUT):
            pass
    except OSError as e:
        pytest.fail(f"Cannot reach {host}:{HTTPS_PORT} - {e}")

@pytest.fixture(scope="session")
def wanikani_service(network_fixture):
    token = os.environ["WANIKANI_TOKEN"]
    headers = {
        "Wanikani-Revision": "20170710",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.get(f"{WANIKANI_API_HOST}/user", headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        pytest.fail(f"Request to Wanikani API failed: {e}")

    if response.status_code == 200:
        return
    if response.status_code == 401:
        error_msg = "token rejected"
    elif response.status_code >= 500:
        error_msg = "WaniKani is down"
    else:
        error_msg = "unexpected status"

    pytest.fail(f"{error_msg}: {response.status_code}")