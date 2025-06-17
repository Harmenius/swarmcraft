"""
Test for the updated SessionConfig with AlgorithmType enum.
Add this to your tests/test_core.py file.
"""

import pytest
from datetime import datetime
from swarmcraft.models.session import (
    SessionConfig,
    GameSession,
    SessionStatus,
    AlgorithmType,
)


class TestSessionConfig:
    """Test suite for SessionConfig with algorithm selection."""

    def test_default_session_config(self):
        """Test that default session config still works (backwards compatibility)."""
        config = SessionConfig()

        # Check all defaults
        assert config.landscape_type == "rastrigin"
        assert config.grid_size == 25
        assert config.max_participants == 30
        assert config.exploration_probability == 0.15
        assert config.max_iterations == 10

        # NEW: Check algorithm defaults
        assert config.algorithm_type == AlgorithmType.PSO
        assert config.abc_limit == 10
        assert config.abc_employed_ratio == 0.5

    def test_pso_session_config(self):
        """Test creating a PSO session config."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.PSO,
            exploration_probability=0.2,
            min_exploration_probability=0.05,
            max_iterations=20,
        )

        assert config.algorithm_type == AlgorithmType.PSO
        assert config.exploration_probability == 0.2
        assert config.min_exploration_probability == 0.05
        # ABC parameters should still have defaults
        assert config.abc_limit == 10

    def test_abc_session_config(self):
        """Test creating an ABC session config."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_limit=15,
            abc_employed_ratio=0.6,
            max_iterations=25,
        )

        assert config.algorithm_type == AlgorithmType.ABC
        assert config.abc_limit == 15
        assert config.abc_employed_ratio == 0.6
        assert config.max_iterations == 25
        # PSO parameters should still be available
        assert config.exploration_probability == 0.15  # Default

    def test_session_config_json_serialization(self):
        """Test that session config can be serialized to JSON (important for API)."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            landscape_type="ecological",
            abc_limit=12,
            abc_employed_ratio=0.4,
        )

        # Standard model_dump keeps enum objects
        config_dict = config.model_dump()
        assert config_dict["algorithm_type"] == AlgorithmType.ABC  # Enum object
        assert config_dict["abc_limit"] == 12
        assert config_dict["abc_employed_ratio"] == 0.4

        # For JSON/API use, serialize with mode="json" to get string values
        config_json = config.model_dump(mode="json")
        assert config_json["algorithm_type"] == "abc"  # String value for JSON
        assert config_json["abc_limit"] == 12
        assert config_json["abc_employed_ratio"] == 0.4

    def test_algorithm_type_enum_values(self):
        """Test that AlgorithmType enum has correct values."""
        assert AlgorithmType.PSO.value == "pso"
        assert AlgorithmType.ABC.value == "abc"

        # Test creating configs with each enum value
        pso_config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        abc_config = SessionConfig(algorithm_type=AlgorithmType.ABC)

        assert pso_config.algorithm_type == AlgorithmType.PSO
        assert abc_config.algorithm_type == AlgorithmType.ABC

    def test_game_session_with_abc_config(self):
        """Test creating a full game session with ABC configuration."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            landscape_type="rastrigin",
            abc_limit=8,
            abc_employed_ratio=0.7,
            max_participants=20,
        )

        session = GameSession(
            id="test_session",
            code="TEST123",
            admin_id="admin_1",
            config=config,
            created_at=datetime.now(),
        )

        assert session.config.algorithm_type == AlgorithmType.ABC
        assert session.config.abc_limit == 8
        assert session.config.abc_employed_ratio == 0.7
        assert session.status == SessionStatus.WAITING

    def test_backwards_compatibility_with_string_input(self):
        """Test that string inputs are converted to enum (API compatibility)."""
        # Pydantic should convert string to enum automatically
        config_data = {
            "landscape_type": "rastrigin",
            "algorithm_type": "abc",  # String input
            "abc_limit": 12,
        }

        config = SessionConfig(**config_data)
        assert config.algorithm_type == AlgorithmType.ABC
        assert config.abc_limit == 12

    def test_invalid_algorithm_type_raises_error(self):
        """Test that invalid algorithm types raise validation errors."""
        with pytest.raises(ValueError):
            SessionConfig(algorithm_type="invalid_algorithm")

    def test_abc_parameter_ranges(self):
        """Test ABC parameters with different valid ranges."""
        # Test different employed ratios
        for ratio in [0.3, 0.5, 0.7, 0.9]:
            config = SessionConfig(
                algorithm_type=AlgorithmType.ABC, abc_employed_ratio=ratio
            )
            assert config.abc_employed_ratio == ratio

        # Test different limits
        for limit in [5, 10, 20, 50]:
            config = SessionConfig(algorithm_type=AlgorithmType.ABC, abc_limit=limit)
            assert config.abc_limit == limit

    def test_enum_comparison_safety(self):
        """Test that enum comparison prevents typos."""
        config = SessionConfig(algorithm_type=AlgorithmType.ABC)

        # This should work
        assert config.algorithm_type == AlgorithmType.ABC

        # This should NOT work (would catch typos)
        assert config.algorithm_type != "abc"  # String comparison

        # But you can check the value if needed
        assert config.algorithm_type.value == "abc"

    def test_algorithm_type_in_conditional_logic(self):
        """Test using enum in conditional logic (how it will be used in API)."""
        pso_config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        abc_config = SessionConfig(algorithm_type=AlgorithmType.ABC)

        # This is how we'll use it in the API
        if pso_config.algorithm_type == AlgorithmType.PSO:
            algorithm_name = "Particle Swarm Optimization"
        elif pso_config.algorithm_type == AlgorithmType.ABC:
            algorithm_name = "Artificial Bee Colony"
        else:
            algorithm_name = "Unknown"

        assert algorithm_name == "Particle Swarm Optimization"

        if abc_config.algorithm_type == AlgorithmType.ABC:
            algorithm_name = "Artificial Bee Colony"
        elif abc_config.algorithm_type == AlgorithmType.PSO:
            algorithm_name = "Particle Swarm Optimization"
        else:
            algorithm_name = "Unknown"

        assert algorithm_name == "Artificial Bee Colony"
