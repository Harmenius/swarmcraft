import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from swarmcraft.api.websocket import ConnectionManager, handle_websocket_message
from swarmcraft.models.session import GameSession, SessionConfig, AlgorithmType

# Use anyio for async pytest fixtures
pytestmark = pytest.mark.anyio


@pytest.fixture
def manager():
    """Returns a fresh ConnectionManager instance for each test."""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Creates a mock WebSocket object with an async send_text method."""
    ws = MagicMock()
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.accept = AsyncMock()
    return ws


@pytest.fixture
def test_session_data_pso():
    """Provides a sample PSO session dictionary, as it would be stored in Redis."""
    config = SessionConfig(
        landscape_type="rastrigin",
        grid_size=25,
        algorithm_type=AlgorithmType.PSO,
        exploration_probability=0.3,
    )
    session = GameSession(
        id="test_session_pso",
        code="PSOSESSION",
        admin_id="admin",
        config=config,
        participants=[],
        created_at=datetime.now(),
    )
    return session.model_dump(mode="json")


@pytest.fixture
def test_session_data_abc():
    """Provides a sample ABC session dictionary, as it would be stored in Redis."""
    config = SessionConfig(
        landscape_type="quadratic",
        grid_size=25,
        algorithm_type=AlgorithmType.ABC,
        abc_limit=5,
        abc_employed_ratio=0.6,
    )
    session = GameSession(
        id="test_session_abc",
        code="ABCSESSION",
        admin_id="admin",
        config=config,
        participants=[],
        created_at=datetime.now(),
    )
    return session.model_dump(mode="json")


class TestConnectionManager:
    """Tests the ConnectionManager class methods."""

    async def test_connect(self, manager: ConnectionManager, mock_websocket: MagicMock):
        """Verify that a user can connect and is added to the active connections."""
        session_id = "s1"
        p_id = "p1"

        manager.broadcast_to_session = AsyncMock()
        manager.send_session_state = AsyncMock()

        await manager.connect(mock_websocket, session_id, p_id)

        assert session_id in manager.active_connections
        assert p_id in manager.active_connections[session_id]
        assert manager.active_connections[session_id][p_id] == mock_websocket

        mock_websocket.accept.assert_awaited_once()
        mock_websocket.send_text.assert_awaited_once()
        sent_data = json.loads(mock_websocket.send_text.await_args[0][0])
        assert sent_data["type"] == "connected"

        manager.send_session_state.assert_awaited_once_with(session_id, p_id)
        manager.broadcast_to_session.assert_awaited_once()

    async def test_disconnect(
        self, manager: ConnectionManager, mock_websocket: MagicMock
    ):
        """Verify that a user is removed upon disconnecting."""
        session_id = "s1"
        p_id = "p1"

        manager.active_connections[session_id] = {p_id: mock_websocket}
        manager.broadcast_to_session = AsyncMock()

        await manager.disconnect(session_id, p_id)

        assert p_id not in manager.active_connections.get(session_id, {})
        manager.broadcast_to_session.assert_awaited_once()

    async def test_broadcast_to_session(self, manager: ConnectionManager):
        """Test broadcasting a message to all participants in a session."""
        session_id = "s1"
        ws1, ws2, ws3 = (
            MagicMock(send_text=AsyncMock()),
            MagicMock(send_text=AsyncMock()),
            MagicMock(send_text=AsyncMock()),
        )
        manager.active_connections[session_id] = {"p1": ws1, "p2": ws2, "p3": ws3}

        message = {"type": "test_broadcast", "data": "hello"}
        await manager.broadcast_to_session(message, session_id)

        ws1.send_text.assert_awaited_once_with(json.dumps(message))
        ws2.send_text.assert_awaited_once_with(json.dumps(message))
        ws3.send_text.assert_awaited_once_with(json.dumps(message))

    async def test_broadcast_with_exclude(self, manager: ConnectionManager):
        """Test that broadcasting correctly excludes a specified participant."""
        session_id = "s1"
        ws1, ws2 = MagicMock(send_text=AsyncMock()), MagicMock(send_text=AsyncMock())
        manager.active_connections[session_id] = {"p1": ws1, "p2": ws2}

        message = {"type": "test_broadcast", "data": "hello"}
        await manager.broadcast_to_session(message, session_id, exclude="p1")

        ws1.send_text.assert_not_awaited()
        ws2.send_text.assert_awaited_once_with(json.dumps(message))

    @patch("swarmcraft.api.websocket.get_redis")
    @patch("swarmcraft.api.websocket.set_json")
    @patch("swarmcraft.api.websocket.get_json")
    async def test_handle_position_update_pso(
        self,
        mock_get_json: AsyncMock,
        mock_set_json: AsyncMock,
        mock_get_redis: AsyncMock,
        manager: ConnectionManager,
        test_session_data_pso,
    ):
        """Test position update with PSO session."""
        session_id = "test_session_pso"
        p_id = "p_test"

        test_session_data_pso["participants"].append(
            {
                "id": p_id,
                "name": "tester",
                "position": None,
                "fitness": None,
                "velocity_magnitude": None,
                "connected": True,
                "joined_at": datetime.now().isoformat(),
            }
        )
        mock_get_json.return_value = test_session_data_pso

        mock_redis_conn = AsyncMock()
        mock_get_redis.return_value = mock_redis_conn

        manager.send_to_participant = AsyncMock()
        manager.broadcast_to_session = AsyncMock()
        new_position = [10, 12]

        await manager.handle_position_update(session_id, p_id, new_position)

        mock_get_json.assert_awaited_once_with(f"session:{session_id}", mock_redis_conn)
        mock_set_json.assert_awaited_once()

        saved_data = mock_set_json.await_args[0][1]
        assert saved_data["participants"][0]["position"] == new_position
        assert "fitness" in saved_data["participants"][0]

        manager.send_to_participant.assert_awaited_once()
        manager.broadcast_to_session.assert_awaited_once()

    @patch("swarmcraft.api.websocket.get_redis")
    @patch("swarmcraft.api.websocket.set_json")
    @patch("swarmcraft.api.websocket.get_json")
    async def test_handle_position_update_abc(
        self,
        mock_get_json: AsyncMock,
        mock_set_json: AsyncMock,
        mock_get_redis: AsyncMock,
        manager: ConnectionManager,
        test_session_data_abc,
    ):
        """Test position update with ABC session."""
        session_id = "test_session_abc"
        p_id = "p_test"

        test_session_data_abc["participants"].append(
            {
                "id": p_id,
                "name": "tester",
                "position": None,
                "fitness": None,
                "velocity_magnitude": None,
                "connected": True,
                "joined_at": datetime.now().isoformat(),
            }
        )
        mock_get_json.return_value = test_session_data_abc

        mock_redis_conn = AsyncMock()
        mock_get_redis.return_value = mock_redis_conn

        manager.send_to_participant = AsyncMock()
        manager.broadcast_to_session = AsyncMock()
        new_position = [5, 8]

        await manager.handle_position_update(session_id, p_id, new_position)

        mock_get_json.assert_awaited_once_with(f"session:{session_id}", mock_redis_conn)
        mock_set_json.assert_awaited_once()

        saved_data = mock_set_json.await_args[0][1]
        assert saved_data["participants"][0]["position"] == new_position
        assert "fitness" in saved_data["participants"][0]

        manager.send_to_participant.assert_awaited_once()
        manager.broadcast_to_session.assert_awaited_once()


class TestHandleWebsocketMessage:
    """Tests the main message handling loop."""

    @patch("swarmcraft.api.websocket.websocket_manager.handle_position_update")
    async def test_handles_move_message(
        self, mock_handle_pos_update: AsyncMock, mock_websocket: MagicMock
    ):
        """Verify that an incoming 'move' message calls the correct handler."""
        move_message = json.dumps({"type": "move", "position": [5, 5]})
        mock_websocket.receive_text.side_effect = [move_message, asyncio.CancelledError]

        with pytest.raises(asyncio.CancelledError):
            await handle_websocket_message(mock_websocket, "s1", "p1")

        mock_handle_pos_update.assert_awaited_once_with("s1", "p1", [5, 5])

    @patch("swarmcraft.api.websocket.websocket_manager.send_personal_message")
    async def test_handles_ping_message(
        self, mock_send_personal: AsyncMock, mock_websocket: MagicMock
    ):
        """Verify that a 'ping' message receives a 'pong' response."""
        ping_message = json.dumps({"type": "ping"})
        mock_websocket.receive_text.side_effect = [ping_message, asyncio.CancelledError]

        with pytest.raises(asyncio.CancelledError):
            await handle_websocket_message(mock_websocket, "s1", "p1")

        mock_send_personal.assert_awaited_once()
        # The first argument is the dictionary itself, not a JSON string.
        sent_dict = mock_send_personal.await_args[0][0]
        assert sent_dict["type"] == "pong"

    @patch("swarmcraft.api.websocket.websocket_manager.send_session_state")
    async def test_handles_get_state_message(
        self, mock_send_state: AsyncMock, mock_websocket: MagicMock
    ):
        """Verify that a 'get_state' message triggers session state send."""
        state_message = json.dumps({"type": "get_state"})
        mock_websocket.receive_text.side_effect = [
            state_message,
            asyncio.CancelledError,
        ]

        with pytest.raises(asyncio.CancelledError):
            await handle_websocket_message(mock_websocket, "s1", "p1")

        mock_send_state.assert_awaited_once_with("s1", "p1")
