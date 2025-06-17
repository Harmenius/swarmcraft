"""
Tests for algorithm factory.
Add this class to your tests/test_core.py file.
"""

import pytest
from swarmcraft.core.algorithm_factory import (
    create_optimizer,
    get_algorithm_display_name,
    get_algorithm_description,
    get_algorithm_config_info,
)
from swarmcraft.models.session import SessionConfig, AlgorithmType
from swarmcraft.core.pso import PSO
from swarmcraft.core.abc import ABC
from swarmcraft.core.loss_functions import create_landscape


class TestAlgorithmFactory:
    """Test suite for algorithm factory functionality."""

    def test_create_pso_optimizer(self):
        """Test creating PSO optimizer through factory."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.PSO,
            exploration_probability=0.2,
            min_exploration_probability=0.05,
            max_iterations=25,
        )
        landscape = create_landscape("rastrigin", A=10.0, dimensions=2)

        optimizer = create_optimizer(config, participants_count=10, landscape=landscape)

        assert isinstance(optimizer, PSO)
        assert optimizer.population_size == 10
        assert optimizer.max_iterations == 25
        assert optimizer.initial_exploration_probability == 0.2
        assert optimizer.min_exploration_probability == 0.05

    def test_create_abc_optimizer(self):
        """Test creating ABC optimizer through factory."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_limit=15,
            abc_employed_ratio=0.6,
            max_iterations=30,
        )
        landscape = create_landscape("ecological")

        optimizer = create_optimizer(config, participants_count=12, landscape=landscape)

        assert isinstance(optimizer, ABC)
        assert optimizer.population_size == 12
        assert optimizer.max_iterations == 30
        assert optimizer.limit == 15
        assert optimizer.employed_ratio == 0.6

    def test_create_optimizer_with_defaults(self):
        """Test creating optimizers with default parameters."""
        # PSO with defaults
        pso_config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        landscape = create_landscape("quadratic", dimensions=2)

        pso_optimizer = create_optimizer(
            pso_config, participants_count=8, landscape=landscape
        )
        assert isinstance(pso_optimizer, PSO)
        assert pso_optimizer.initial_exploration_probability == 0.15  # Default

        # ABC with defaults
        abc_config = SessionConfig(algorithm_type=AlgorithmType.ABC)
        abc_optimizer = create_optimizer(
            abc_config, participants_count=8, landscape=landscape
        )
        assert isinstance(abc_optimizer, ABC)
        assert abc_optimizer.limit == 10  # Default
        assert abc_optimizer.employed_ratio == 0.5  # Default

    def test_unsupported_algorithm_validation(self):
        """Test that invalid algorithm types are caught during config creation."""
        # Test that Pydantic properly validates algorithm types
        with pytest.raises(ValueError):
            # This should fail because "invalid_algorithm" is not a valid AlgorithmType
            SessionConfig(algorithm_type="invalid_algorithm")

        # Test that the factory properly handles the enum types it expects
        config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        landscape = create_landscape("rastrigin")
        optimizer = create_optimizer(config, participants_count=5, landscape=landscape)
        assert isinstance(optimizer, PSO)

    def test_algorithm_display_names(self):
        """Test algorithm display name functionality."""
        assert (
            get_algorithm_display_name(AlgorithmType.PSO)
            == "Particle Swarm Optimization"
        )
        assert get_algorithm_display_name(AlgorithmType.ABC) == "Artificial Bee Colony"

        # The function is designed to work with valid enum values only
        # In practice, invalid values would be caught by enum validation before reaching this function

    def test_algorithm_descriptions(self):
        """Test algorithm description functionality."""
        pso_desc = get_algorithm_description(AlgorithmType.PSO)
        abc_desc = get_algorithm_description(AlgorithmType.ABC)

        assert "particles" in pso_desc.lower()
        assert "personal and global best" in pso_desc.lower()

        assert "bees" in abc_desc.lower()
        assert "employed" in abc_desc.lower()
        assert "onlookers" in abc_desc.lower()
        assert "scouts" in abc_desc.lower()

    def test_algorithm_config_info_pso(self):
        """Test PSO configuration information display."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.PSO,
            exploration_probability=0.3,
            min_exploration_probability=0.1,
        )

        config_info = get_algorithm_config_info(config)

        assert config_info["algorithm"] == "PSO"
        assert config_info["exploration_probability"] == 0.3
        assert config_info["min_exploration_probability"] == 0.1
        assert "exploration_starts_at" in config_info["parameters"]
        assert "30.0%" in config_info["parameters"]["exploration_starts_at"]

    def test_algorithm_config_info_abc(self):
        """Test ABC configuration information display."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.ABC, abc_limit=20, abc_employed_ratio=0.7
        )

        config_info = get_algorithm_config_info(config)

        assert config_info["algorithm"] == "ABC"
        assert config_info["abc_limit"] == 20
        assert config_info["abc_employed_ratio"] == 0.7
        assert "employed_bees" in config_info["parameters"]
        assert "70.0%" in config_info["parameters"]["employed_bees"]
        assert config_info["parameters"]["abandonment_limit"] == 20

    def test_optimizer_initialization_with_different_landscapes(self):
        """Test that optimizer works with different landscape types."""
        config = SessionConfig(algorithm_type=AlgorithmType.ABC)

        # Test with different landscapes
        landscapes = [
            create_landscape("rastrigin", A=5.0),
            create_landscape("ecological"),
            create_landscape("quadratic", dimensions=2),
        ]

        for landscape in landscapes:
            optimizer = create_optimizer(
                config, participants_count=6, landscape=landscape
            )
            assert isinstance(optimizer, ABC)
            assert optimizer.population_size == 6
            assert len(optimizer.swarm_state.particles) == 6

            # Test that optimizer can perform a step
            optimizer.step()
            assert optimizer.swarm_state.iteration == 1
            # Fitness should be a number (might be same or different)
            assert isinstance(optimizer.swarm_state.global_best_fitness, float)

    def test_factory_preserves_landscape_bounds(self):
        """Test that factory correctly uses landscape bounds."""
        config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        landscape = create_landscape("rastrigin", A=10.0, dimensions=2)

        optimizer = create_optimizer(config, participants_count=5, landscape=landscape)

        # Check that bounds are correctly set
        expected_bounds = landscape.metadata.recommended_bounds
        # Convert numpy array bounds to list of tuples for comparison
        actual_bounds = [tuple(bound) for bound in optimizer.bounds.tolist()]
        assert actual_bounds == expected_bounds

        # Check that particles are within bounds
        for particle in optimizer.swarm_state.particles:
            pos = particle.position_array
            for i, (min_bound, max_bound) in enumerate(expected_bounds):
                assert min_bound <= pos[i] <= max_bound

    def test_factory_with_edge_case_participant_counts(self):
        """Test factory with edge case participant counts."""
        config = SessionConfig(algorithm_type=AlgorithmType.ABC, abc_employed_ratio=0.5)
        landscape = create_landscape("quadratic")

        # Test with small participant count
        small_optimizer = create_optimizer(
            config, participants_count=2, landscape=landscape
        )
        assert small_optimizer.population_size == 2
        # Cast to ABC to access ABC-specific attributes
        assert isinstance(small_optimizer, ABC)
        small_abc = small_optimizer  # Type checker now knows this is ABC
        assert small_abc.employed_count == 1  # 50% of 2
        assert small_abc.onlooker_count == 1

        # Test with larger participant count
        large_optimizer = create_optimizer(
            config, participants_count=100, landscape=landscape
        )
        assert large_optimizer.population_size == 100
        assert isinstance(large_optimizer, ABC)
        large_abc = large_optimizer  # Type checker now knows this is ABC
        assert large_abc.employed_count == 50  # 50% of 100
        assert large_abc.onlooker_count == 50

    def test_config_info_with_none_values(self):
        """Test configuration info when optional values are None."""
        config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_limit=None,  # Test None handling
            abc_employed_ratio=None,
        )

        config_info = get_algorithm_config_info(config)

        assert config_info["algorithm"] == "ABC"
        assert config_info["abc_limit"] is None
        assert config_info["abc_employed_ratio"] is None
        # Should use defaults in parameters
        assert config_info["parameters"]["abandonment_limit"] == 10  # Default
        assert "50.0%" in config_info["parameters"]["employed_bees"]  # Default 0.5
