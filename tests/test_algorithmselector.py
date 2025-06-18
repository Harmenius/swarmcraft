"""
Tests for algorithm selector API endpoints and functionality.
Add this to your existing test suite.
"""

from swarmcraft.models.session import AlgorithmType, SessionConfig
from swarmcraft.core.algorithm_factory import (
    get_algorithm_display_name,
    get_algorithm_description,
)


class TestAlgorithmSelectorAPI:
    """Test suite for algorithm selector API functionality."""

    def test_algorithm_parameter_schema_consistency(self):
        """Test that parameter schemas are consistent with factory expectations."""
        from swarmcraft.api.routes import _get_algorithm_parameter_schema

        # Test PSO schema
        pso_schema = _get_algorithm_parameter_schema(AlgorithmType.PSO)
        assert "exploration_probability" in pso_schema
        assert "min_exploration_probability" in pso_schema

        # Verify schema structure
        for param_name, param_info in pso_schema.items():
            assert "type" in param_info
            assert "default" in param_info
            assert "description" in param_info

            if param_info["type"] in ["number", "integer"]:
                assert "min" in param_info
                assert "max" in param_info
                assert "step" in param_info

        # Test ABC schema
        abc_schema = _get_algorithm_parameter_schema(AlgorithmType.ABC)
        assert "abc_limit" in abc_schema
        assert "abc_employed_ratio" in abc_schema

        # Verify ABC parameter types
        assert abc_schema["abc_limit"]["type"] == "integer"
        assert abc_schema["abc_employed_ratio"]["type"] == "number"

    def test_session_config_with_algorithm_parameters(self):
        """Test SessionConfig creation with algorithm-specific parameters."""
        # Test PSO config
        pso_config = SessionConfig(
            algorithm_type=AlgorithmType.PSO,
            exploration_probability=0.25,
            min_exploration_probability=0.08,
            landscape_type="rastrigin",
        )

        assert pso_config.algorithm_type == AlgorithmType.PSO
        assert pso_config.exploration_probability == 0.25
        assert pso_config.min_exploration_probability == 0.08

        # Test ABC config
        abc_config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_limit=12,
            abc_employed_ratio=0.65,
            landscape_type="ecological",
        )

        assert abc_config.algorithm_type == AlgorithmType.ABC
        assert abc_config.abc_limit == 12
        assert abc_config.abc_employed_ratio == 0.65

    def test_algorithm_factory_integration_with_parameters(self):
        """Test that factory correctly uses custom parameters."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape

        # Test PSO with custom parameters
        pso_config = SessionConfig(
            algorithm_type=AlgorithmType.PSO,
            exploration_probability=0.35,
            min_exploration_probability=0.05,
        )

        landscape = create_landscape("quadratic")
        pso_optimizer = create_optimizer(pso_config, 8, landscape)

        assert pso_optimizer.initial_exploration_probability == 0.35
        assert pso_optimizer.min_exploration_probability == 0.05

        # Test ABC with custom parameters
        abc_config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_limit=20,
            abc_employed_ratio=0.75,
        )

        abc_optimizer = create_optimizer(abc_config, 12, landscape)

        assert abc_optimizer.limit == 20
        assert abc_optimizer.employed_ratio == 0.75
        assert abc_optimizer.employed_count == 9  # 75% of 12
        assert abc_optimizer.onlooker_count == 3  # Remaining 25%

    def test_algorithm_display_names_and_descriptions(self):
        """Test algorithm display name and description functionality."""
        assert (
            get_algorithm_display_name(AlgorithmType.PSO)
            == "Particle Swarm Optimization"
        )
        assert get_algorithm_display_name(AlgorithmType.ABC) == "Artificial Bee Colony"

        pso_desc = get_algorithm_description(AlgorithmType.PSO)
        abc_desc = get_algorithm_description(AlgorithmType.ABC)

        assert "particles" in pso_desc.lower()
        assert "personal and global best" in pso_desc.lower()

        assert "bees" in abc_desc.lower()
        assert "employed" in abc_desc.lower()
        assert "onlookers" in abc_desc.lower()
        assert "scouts" in abc_desc.lower()


class TestAlgorithmSelectorIntegration:
    """Integration tests for algorithm selector with actual algorithm functionality."""

    def test_abc_algorithm_step_execution(self):
        """Test that ABC algorithm can execute steps without errors."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape

        # Create ABC config
        abc_config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_limit=5,
            abc_employed_ratio=0.6,
            max_iterations=20,
        )

        landscape = create_landscape("quadratic")
        abc_optimizer = create_optimizer(abc_config, 10, landscape)

        # Should be ABC instance
        from swarmcraft.core.abc import ABC

        assert isinstance(abc_optimizer, ABC)

        # Test initial state
        assert abc_optimizer.swarm_state.iteration == 0
        assert len(abc_optimizer.swarm_state.particles) == 10
        assert abc_optimizer.employed_count == 6  # 60% of 10
        assert abc_optimizer.onlooker_count == 4  # 40% of 10

        # Execute step
        _ = abc_optimizer.swarm_state.global_best_fitness
        result = abc_optimizer.step()

        # Should advance iteration
        assert result.iteration == 1
        assert abc_optimizer.swarm_state.iteration == 1

        # Should have valid fitness
        assert isinstance(result.global_best_fitness, float)

        # Test suggest_next_position functionality
        particle_id = abc_optimizer.swarm_state.particles[0].id
        suggestion = abc_optimizer.suggest_next_position(particle_id)

        assert suggestion is not None
        assert len(suggestion) == 2
        assert all(isinstance(x, float) for x in suggestion)

    def test_pso_algorithm_step_execution(self):
        """Test that PSO algorithm still works with new infrastructure."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape

        # Create PSO config
        pso_config = SessionConfig(
            algorithm_type=AlgorithmType.PSO,
            exploration_probability=0.3,
            min_exploration_probability=0.1,
            max_iterations=20,
        )

        landscape = create_landscape("quadratic")
        pso_optimizer = create_optimizer(pso_config, 8, landscape)

        # Should be PSO instance
        from swarmcraft.core.pso import PSO

        assert isinstance(pso_optimizer, PSO)

        # Test initial state
        assert pso_optimizer.swarm_state.iteration == 0
        assert len(pso_optimizer.swarm_state.particles) == 8

        # Execute step
        result = pso_optimizer.step()

        # Should advance iteration
        assert result.iteration == 1
        assert isinstance(result.global_best_fitness, float)

        # Test suggest_next_position functionality
        particle_id = pso_optimizer.swarm_state.particles[0].id
        suggestion = pso_optimizer.suggest_next_position(particle_id)

        assert suggestion is not None
        assert len(suggestion) == 2

    def test_algorithm_statistics_compatibility(self):
        """Test that both algorithms provide compatible statistics."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape

        landscape = create_landscape("rastrigin")

        # Test ABC stats
        abc_config = SessionConfig(algorithm_type=AlgorithmType.ABC)
        abc_optimizer = create_optimizer(abc_config, 6, landscape)
        abc_optimizer.step()

        abc_stats = abc_optimizer.get_abc_statistics()
        assert "global_best_fitness" in abc_stats
        assert "bee_distribution" in abc_stats
        assert "abandoned_sources" in abc_stats

        # Should also work with PSO compatibility method
        pso_compat_stats = abc_optimizer.get_pso_statistics()
        assert pso_compat_stats == abc_stats

        # Test PSO stats
        pso_config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        pso_optimizer = create_optimizer(pso_config, 6, landscape)
        pso_optimizer.step()

        pso_stats = pso_optimizer.get_pso_statistics()
        assert "global_best_fitness" in pso_stats
        assert "exploration_stats" in pso_stats

    def test_algorithm_parameter_defaults(self):
        """Test that algorithms work with default parameters when none provided."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape

        landscape = create_landscape("ecological")

        # ABC with defaults
        abc_config = SessionConfig(algorithm_type=AlgorithmType.ABC)
        abc_optimizer = create_optimizer(abc_config, 10, landscape)

        # Should use factory defaults
        assert abc_optimizer.limit == 10  # Default from factory
        assert abc_optimizer.employed_ratio == 0.5  # Default from factory

        # Should work
        abc_optimizer.step()
        assert abc_optimizer.swarm_state.iteration == 1

        # PSO with defaults
        pso_config = SessionConfig(algorithm_type=AlgorithmType.PSO)
        pso_optimizer = create_optimizer(pso_config, 8, landscape)

        # Should use SessionConfig defaults
        assert (
            pso_optimizer.initial_exploration_probability == 0.15
        )  # Default from SessionConfig

        # Should work
        pso_optimizer.step()
        assert pso_optimizer.swarm_state.iteration == 1

    def test_abc_bee_role_assignment(self):
        """Test that ABC correctly assigns bee roles."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape
        from swarmcraft.core.swarm_base import ParticleState

        abc_config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_employed_ratio=0.7,  # 70% employed
        )

        landscape = create_landscape("quadratic")
        abc_optimizer = create_optimizer(abc_config, 10, landscape)

        # Check role assignment
        employed_count = sum(
            1
            for p in abc_optimizer.swarm_state.particles
            if p.state == ParticleState.EXPLOITING
        )
        onlooker_count = sum(
            1
            for p in abc_optimizer.swarm_state.particles
            if p.state == ParticleState.SHARING
        )

        assert employed_count == 7  # 70% of 10
        assert onlooker_count == 3  # 30% of 10
        assert employed_count + onlooker_count == 10

    def test_edge_case_small_populations(self):
        """Test algorithms with very small populations."""
        from swarmcraft.core.algorithm_factory import create_optimizer
        from swarmcraft.core.loss_functions import create_landscape

        landscape = create_landscape("quadratic")

        # Test ABC with 1 participant
        abc_config = SessionConfig(
            algorithm_type=AlgorithmType.ABC,
            abc_employed_ratio=0.8,  # Would be 0 employed without minimum constraint
        )

        abc_optimizer = create_optimizer(abc_config, 1, landscape)
        assert abc_optimizer.employed_count >= 1  # Should enforce minimum
        assert abc_optimizer.employed_count + abc_optimizer.onlooker_count == 1

        # Should work without errors
        abc_optimizer.step()
        assert abc_optimizer.swarm_state.iteration == 1

        # Test ABC with 2 participants
        abc_optimizer_2 = create_optimizer(abc_config, 2, landscape)
        assert abc_optimizer_2.employed_count >= 1
        abc_optimizer_2.step()
        assert abc_optimizer_2.swarm_state.iteration == 1


# Remove the fixtures that require FastAPI TestClient since we don't have it set up
# Focus on unit tests that test the core functionality directly
