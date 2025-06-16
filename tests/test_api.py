import pytest
from httpx import AsyncClient, ASGITransport
import os
from fastapi import status
from fastapi.testclient import TestClient

from swarmcraft.main import app
from swarmcraft.database.redis_client import redis_client

# Use a consistent test key for all tests
TEST_ADMIN_KEY = "test_admin_key_for_ci_12345"


@pytest.fixture(scope="session")
def anyio_backend():
    # Required configuration for using async fixtures with pytest
    return "asyncio"


@pytest.fixture(scope="module")
async def async_client():
    """
    Creates a single test client for the entire test module.
    It sets up the necessary environment variables and flushes the test
    database before and after all tests in the module run.
    """
    os.environ["SWARM_API_KEY"] = TEST_ADMIN_KEY
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        db = await redis_client.get_redis()
        await db.flushdb()
        yield client
        await db.flushdb()


@pytest.fixture
def admin_headers():
    """Provides the authorization header for admin-only endpoints."""
    return {"X-Admin-Key": TEST_ADMIN_KEY}


@pytest.mark.anyio
async def test_health_check(async_client: AsyncClient):
    """Tests that the health check endpoint is responsive and reports a healthy status."""
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


@pytest.mark.anyio
class TestSessionLifecycle:
    """
    A comprehensive test class that simulates the entire lifecycle of a session,
    from creation to deletion, ensuring all endpoints and state transitions work correctly.
    """

    async def test_full_lifecycle(self, async_client: AsyncClient, admin_headers):
        # Steps 1-8: Use the async_client for all standard HTTP requests
        # 1. ADMIN: Create a new session
        session_config = {"landscape_type": "ecological", "grid_size": 15}
        create_response = await async_client.post(
            "/api/admin/create-session", json=session_config, headers=admin_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        session_data = create_response.json()
        session_id = session_data["session_id"]
        session_code = session_data["session_code"]

        # 2. ADMIN: List sessions to verify it was created
        list_response = await async_client.get(
            "/api/admin/sessions", headers=admin_headers
        )
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["session_id"] == session_id
        assert list_response.json()[0]["status"] == "waiting"

        # 3. PARTICIPANTS: Have two participants join the session
        join_res_1 = await async_client.post(f"/api/join/{session_code}")
        assert join_res_1.status_code == status.HTTP_200_OK
        p1_data = join_res_1.json()
        p1_id = p1_data["participant_id"]

        join_res_2 = await async_client.post(f"/api/join/{session_code}")
        assert join_res_2.status_code == status.HTTP_200_OK
        p2_data = join_res_2.json()
        p2_id = p2_data["participant_id"]

        # 4. ADMIN: Start the session, which initializes the swarm state
        start_response = await async_client.post(
            f"/api/admin/session/{session_id}/start", headers=admin_headers
        )
        assert start_response.status_code == status.HTTP_200_OK
        assert "swarm state initialized" in start_response.json()["message"]

        # 5. Check status to confirm it's active and participants have positions
        status_response = await async_client.get(f"/api/session/{session_id}/status")
        assert status_response.json()["status"] == "active"
        assert status_response.json()["participants"] == 2

        # 6. PARTICIPANT: Trigger an individual, asynchronous move for p1
        move_response = await async_client.post(
            f"/api/session/{session_id}/move", json={"participant_id": p1_id}
        )
        assert move_response.status_code == status.HTTP_200_OK
        assert "position" in move_response.json()
        assert "velocity_magnitude" in move_response.json()

        # 7. ADMIN: Trigger a global, synchronous step for all participants
        step_response = await async_client.post(
            f"/api/admin/session/{session_id}/step", headers=admin_headers
        )
        assert step_response.status_code == status.HTTP_200_OK
        assert "step 1 executed" in step_response.json()["message"]

        # 8. Check status again to see the iteration count has updated
        status_after_step = await async_client.get(f"/api/session/{session_id}/status")
        assert status_after_step.json()["iteration"] == 1

        # 9. Test WebSocket broadcast after a step
        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/{session_id}/{p2_id}") as websocket:
                # First message is always the 'connected' confirmation
                data = websocket.receive_json()
                assert data["type"] == "connected"

                # The server then sends the current state
                data = websocket.receive_json()
                assert data["type"] == "session_state"
                assert data["session"]["iteration"] == 1  # Check current iteration

                # Now, trigger another step using the SYNCHRONOUS client
                client.post(
                    f"/api/admin/session/{session_id}/step", headers=admin_headers
                )

                # Check that the WebSocket received a broadcast with the new state
                data = websocket.receive_json()
                assert data["type"] == "session_state"
                assert (
                    data["session"]["iteration"] == 2
                )  # Verify iteration was incremented
                assert len(data["session"]["participants"]) == 2
                assert "velocity_magnitude" in data["session"]["participants"][0]

        # 10. ADMIN: Delete the session (switch back to async_client for consistency)
        delete_response = await async_client.delete(
            f"/api/admin/session/{session_id}", headers=admin_headers
        )
        assert delete_response.status_code == status.HTTP_200_OK
        assert "closed and all data deleted" in delete_response.json()["message"]

        # 11. Verify the session is gone by listing again
        final_list_response = await async_client.get(
            "/api/admin/sessions", headers=admin_headers
        )
        assert len(final_list_response.json()) == 0
