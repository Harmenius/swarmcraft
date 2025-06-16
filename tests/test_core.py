"""
Test suite for SwarmCraft optimization framework.

This module contains comprehensive tests for all core functionality
including swarm optimization, loss functions, and visualization.
"""

import pytest
import numpy as np
import tempfile
import os

from swarmcraft.core.swarm_base import (
    Particle,
    SwarmState,
    ParticleState,
)
from swarmcraft.core.pso import PSO
from swarmcraft.core.loss_functions import (
    RastriginLandscape,
    EcologicalLandscape,
    QuadraticLandscape,  # Import the new landscape
    LandscapeType,
    create_landscape,
)
from swarmcraft.core.landscape_visualizer import LandscapeVisualizer, quick_visualize


class TestOptimizationLandscapes:
    """Test suite for optimization landscapes."""

    def test_rastrigin_landscape_creation(self):
        """Test Rastrigin landscape creation and basic properties."""
        landscape = RastriginLandscape(A=10.0, dimensions=2)

        assert landscape.metadata.name == "Rastrigin Function"
        assert landscape.metadata.dimensions == 2
        assert landscape.metadata.landscape_type == LandscapeType.MATHEMATICAL
        assert landscape.metadata.global_minimum == [0.0, 0.0]
        assert landscape.metadata.global_minimum_value == 0.0

    def test_rastrigin_global_minimum(self):
        """Test that Rastrigin function evaluates correctly at global minimum."""
        landscape = RastriginLandscape(A=10.0, dimensions=2)

        # Global minimum should be exactly 0 at origin
        result = landscape.evaluate(np.array([0.0, 0.0]))
        assert abs(result) < 1e-10

        # Should be positive elsewhere
        result = landscape.evaluate(np.array([1.0, 1.0]))
        assert result > 0

    # --- NEW TEST ---
    def test_quadratic_landscape_creation_and_evaluation(self):
        """Test Quadratic landscape creation and evaluation."""
        landscape = QuadraticLandscape(dimensions=3)
        assert landscape.metadata.name == "Quadratic Bowl"
        assert landscape.metadata.dimensions == 3
        assert landscape.metadata.difficulty_level == 1

        # Test evaluation at global minimum (origin)
        assert landscape.evaluate([0.0, 0.0, 0.0]) == 0.0

        # Test evaluation at another point
        assert landscape.evaluate([1.0, 2.0, 3.0]) == 1**2 + 2**2 + 3**2

    def test_rastrigin_different_dimensions(self):
        """Test Rastrigin with different dimensions."""
        for dim in [1, 2, 3, 5]:
            landscape = RastriginLandscape(A=10.0, dimensions=dim)

            assert landscape.metadata.dimensions == dim
            assert len(landscape.metadata.global_minimum) == dim

            # Test evaluation
            test_point = np.zeros(dim)
            result = landscape.evaluate(test_point)
            assert abs(result) < 1e-10

    def test_ecological_landscape_creation(self):
        """Test ecological landscape creation and properties."""
        landscape = EcologicalLandscape()

        assert landscape.metadata.name == "Sustainable Development Challenge"
        assert landscape.metadata.dimensions == 2
        assert landscape.metadata.landscape_type == LandscapeType.ECOLOGICAL
        assert len(landscape.metadata.global_minimum) == 2
        assert landscape.metadata.axis_labels is not None

    def test_ecological_landscape_evaluation(self):
        """Test ecological landscape evaluation at key points."""
        landscape = EcologicalLandscape()

        # Test global minimum area (should be relatively low cost)
        gm = landscape.metadata.global_minimum
        gm_value = landscape.evaluate(np.array(gm))
        assert gm_value >= 0  # Should be non-negative

        # Test extreme positions (should have higher costs)
        high_dev_low_reg = landscape.evaluate(np.array([9.0, 1.0]))  # Pollution trap
        low_dev_high_reg = landscape.evaluate(np.array([1.0, 9.0]))  # Stagnation trap

        assert high_dev_low_reg > gm_value
        assert low_dev_high_reg > gm_value

    def test_landscape_factory(self):
        """Test landscape creation through factory function."""
        # Test Rastrigin creation
        rastrigin = create_landscape("rastrigin", A=5.0, dimensions=3)
        assert isinstance(rastrigin, RastriginLandscape)
        assert rastrigin.A == 5.0
        assert rastrigin.dimensions == 3

        # Test Quadratic creation
        quadratic = create_landscape("quadratic", dimensions=2)
        assert isinstance(quadratic, QuadraticLandscape)

        # Test ecological creation
        ecological = create_landscape("ecological")
        assert isinstance(ecological, EcologicalLandscape)

        # Test invalid landscape name
        with pytest.raises(ValueError):
            create_landscape("nonexistent_landscape")

    def test_landscape_color_generation(self):
        """Test color generation for fitness values."""
        landscape = RastriginLandscape()

        # Test color generation
        color1 = landscape.get_fitness_color(0.0)  # Good fitness
        color2 = landscape.get_fitness_color(50.0)  # Bad fitness

        assert color1.startswith("#")
        assert color2.startswith("#")
        assert len(color1) == 7  # Hex color format
        assert len(color2) == 7

    def test_landscape_audio_frequency(self):
        """Test audio frequency generation for fitness values."""
        landscape = RastriginLandscape()

        freq1 = landscape.get_fitness_audio_frequency(0.0)  # Good fitness
        freq2 = landscape.get_fitness_audio_frequency(50.0)  # Bad fitness

        assert 200 <= freq1 <= 800
        assert 200 <= freq2 <= 800
        assert freq2 > freq1  # Higher fitness should mean higher frequency


class TestSwarmBase:
    """Test suite for base swarm optimization functionality."""

    def test_particle_creation(self):
        """Test Particle model creation and validation."""
        particle = Particle(
            id="test_particle",
            position=[1.0, 2.0],
            velocity=[0.1, 0.2],
            fitness=5.0,
            personal_best_position=[1.0, 2.0],
            personal_best_fitness=5.0,
        )

        assert particle.id == "test_particle"
        assert particle.position == [1.0, 2.0]
        assert np.array_equal(particle.position_array, np.array([1.0, 2.0]))
        assert particle.state == ParticleState.EXPLOITING

    def test_particle_array_conversion(self):
        """Test conversion between lists and numpy arrays."""
        particle = Particle(
            id="test",
            position=[1.0, 2.0],
            velocity=[0.1, 0.2],
            fitness=5.0,
            personal_best_position=[1.0, 2.0],
            personal_best_fitness=5.0,
        )

        # Test array properties
        assert isinstance(particle.position_array, np.ndarray)
        assert isinstance(particle.velocity_array, np.ndarray)
        assert isinstance(particle.personal_best_array, np.ndarray)

        # Test update methods
        new_pos = np.array([3.0, 4.0])
        particle.update_position(new_pos)
        assert particle.position == [3.0, 4.0]

    def test_swarm_state_creation(self):
        """Test SwarmState model creation and validation."""
        particles = [
            Particle(
                id=f"particle_{i}",
                position=[float(i), float(i)],
                velocity=[0.0, 0.0],
                fitness=float(i),
                personal_best_position=[float(i), float(i)],
                personal_best_fitness=float(i),
            )
            for i in range(3)
        ]

        swarm_state = SwarmState(
            particles=particles,
            global_best_position=[0.0, 0.0],
            global_best_fitness=0.0,
            global_best_particle_id="particle_0",
            iteration=1,
            phase="optimization",
        )

        assert len(swarm_state.particles) == 3
        assert swarm_state.global_best_fitness == 0.0
        assert swarm_state.phase == "optimization"

    def test_invalid_phase_validation(self):
        """Test that invalid phases are rejected."""
        particles = [
            Particle(
                id="particle_0",
                position=[0.0, 0.0],
                velocity=[0.0, 0.0],
                fitness=0.0,
                personal_best_position=[0.0, 0.0],
                personal_best_fitness=0.0,
            )
        ]

        with pytest.raises(ValueError):
            SwarmState(
                particles=particles,
                global_best_position=[0.0, 0.0],
                global_best_fitness=0.0,
                global_best_particle_id="particle_0",
                iteration=1,
                phase="invalid_phase",
            )


class TestPSO:
    """Test suite for PSO implementation."""

    def test_pso_initialization(self):
        """Test PSO initialization with automatic swarm creation."""

        def simple_loss(x):
            return np.sum(x**2)

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=10,
            random_seed=42,
        )

        # Should be automatically initialized
        assert pso.swarm_state is not None
        assert len(pso.swarm_state.particles) == 10
        assert pso.swarm_state.iteration == 0
        assert pso.swarm_state.phase == "initialization"

    def test_pso_exploration_annealing(self):
        """Test that the exploration probability correctly anneals over time."""
        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=lambda x: np.sum(x**2),
            population_size=5,
            max_iterations=20,
            exploration_probability=0.5,
            min_exploration_probability=0.1,  # Anneal from 0.5 down to 0.1
            random_seed=42,
        )

        # Before any steps, it should be at the initial value
        assert pso.current_exploration_probability == 0.5

        # After 1 step (iteration 1)
        pso.step()
        expected_prob_1 = 0.5 - (0.4 * (1 / 20))
        assert abs(pso.current_exploration_probability - expected_prob_1) < 1e-9

        # After 10 steps (halfway)
        for _ in range(9):
            pso.step()
        # expected_prob_10 = 0.5 - (0.4 * (10/20))  # Should be 0.3 # Ruff F841 Fix
        assert abs(pso.current_exploration_probability - 0.3) < 1e-9

        # After 20 steps (end)
        for _ in range(10):
            pso.step()
        assert abs(pso.current_exploration_probability - 0.1) < 1e-9

        # After more than max_iterations, it should clamp to the minimum
        pso.step()
        assert abs(pso.current_exploration_probability - 0.1) < 1e-9

    def test_pso_step_execution(self):
        """Test PSO step execution."""

        def simple_loss(x):
            return np.sum(x**2)

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=5,
            random_seed=42,
        )

        initial_iteration = pso.swarm_state.iteration
        # initial_fitness = pso.swarm_state.global_best_fitness # Ruff F841 Fix

        # Execute step
        new_state = pso.step()

        assert new_state.iteration == initial_iteration + 1
        assert len(pso.history) > 1  # History should be recorded

    def test_pso_optimization_progress(self):
        """Test that PSO makes optimization progress."""

        def simple_loss(x):
            return np.sum(x**2)  # Simple quadratic with minimum at origin

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=20,
            max_iterations=50,
            random_seed=42,
        )

        initial_fitness = pso.swarm_state.global_best_fitness

        # Run optimization
        for _ in range(20):
            pso.step()

        final_fitness = pso.swarm_state.global_best_fitness

        # Should improve (lower fitness is better)
        assert final_fitness < initial_fitness

    def test_pso_with_rastrigin(self):
        """Test PSO on Rastrigin landscape."""
        landscape = RastriginLandscape(A=10.0, dimensions=2)

        pso = PSO(
            dimensions=2,
            bounds=landscape.metadata.recommended_bounds,
            loss_function=landscape.evaluate,
            population_size=20,
            random_seed=42,
        )

        # Run optimization
        for _ in range(30):
            pso.step()

        # Should find reasonably good solution
        final_fitness = pso.swarm_state.global_best_fitness
        assert final_fitness < 50  # Should find something better than random

    def test_pso_statistics(self):
        """Test PSO statistics generation."""

        def simple_loss(x):
            return np.sum(x**2)

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=10,
            random_seed=42,
        )
        pso.step()  # Run one step to populate stats
        stats = pso.get_pso_statistics()

        # Check required fields
        assert "current_inertia" in stats
        assert "current_exploration_probability" in stats
        assert "velocity_stats" in stats
        assert "exploration_stats" in stats
        assert "global_best_fitness" in stats
        assert "diversity" in stats

        # Check velocity stats structure
        vel_stats = stats["velocity_stats"]
        assert "mean_speed" in vel_stats
        assert "max_speed" in vel_stats
        assert "min_speed" in vel_stats

    def test_particle_info_retrieval(self):
        """Test particle information retrieval."""

        def simple_loss(x):
            return np.sum(x**2)

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=5,
            random_seed=42,
        )

        # Get info for first particle
        particle_id = pso.swarm_state.particles[0].id
        info = pso.get_particle_info(particle_id)

        assert info is not None
        assert info["id"] == particle_id
        assert "position" in info
        assert "fitness" in info
        assert "state" in info
        assert "distance_to_global_best" in info

        # Test non-existent particle
        assert pso.get_particle_info("nonexistent") is None

    def test_position_suggestion(self):
        """Test position suggestion functionality."""

        def simple_loss(x):
            return np.sum(x**2)

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=5,
            random_seed=42,
        )

        particle_id = pso.swarm_state.particles[0].id
        suggestion = pso.suggest_next_position(particle_id)

        assert suggestion is not None
        assert len(suggestion) == 2
        assert isinstance(suggestion, list)

        # Should be within bounds
        assert -5 <= suggestion[0] <= 5
        assert -5 <= suggestion[1] <= 5

    def test_exploration_phase_forcing(self):
        """Test forced exploration and exploitation phases."""

        def simple_loss(x):
            return np.sum(x**2)

        pso = PSO(
            dimensions=2,
            bounds=[(-5, 5), (-5, 5)],
            loss_function=simple_loss,
            population_size=10,
            random_seed=42,
        )

        # Force exploration
        pso.force_exploration_phase()
        exploring_count = sum(
            1 for p in pso.swarm_state.particles if p.state == ParticleState.EXPLORING
        )
        assert exploring_count == 10

        # Force exploitation
        pso.force_exploitation_phase()
        exploiting_count = sum(
            1 for p in pso.swarm_state.particles if p.state == ParticleState.EXPLOITING
        )
        assert exploiting_count == 10


class TestLandscapeVisualizer:
    """Test suite for landscape visualization."""

    def test_visualizer_creation(self):
        """Test visualizer creation with different themes."""
        visualizer = LandscapeVisualizer()
        assert visualizer.theme == "plotly_dark"

        visualizer_light = LandscapeVisualizer(theme="plotly_white")
        assert visualizer_light.theme == "plotly_white"

    def test_2d_landscape_visualization(self):
        """Test 2D landscape visualization."""
        landscape = RastriginLandscape(A=5.0, dimensions=2)
        visualizer = LandscapeVisualizer()

        fig = visualizer.plot_2d_landscape(
            landscape, resolution=20
        )  # Low res for speed

        assert fig is not None
        assert len(fig.data) > 0  # Should have traces

    def test_3d_landscape_visualization(self):
        """Test 3D landscape visualization."""
        landscape = RastriginLandscape(A=5.0, dimensions=2)
        visualizer = LandscapeVisualizer()

        fig = visualizer.plot_3d_landscape(
            landscape, resolution=10
        )  # Very low res for speed

        assert fig is not None
        assert len(fig.data) > 0

    def test_cross_section_visualization(self):
        """Test cross-section visualization."""
        landscape = RastriginLandscape(A=5.0, dimensions=2)
        visualizer = LandscapeVisualizer()

        fig = visualizer.plot_cross_sections(landscape, resolution=50, num_sections=3)

        assert fig is not None
        assert len(fig.data) > 0

    def test_landscape_statistics_analysis(self):
        """Test landscape statistical analysis."""
        landscape = RastriginLandscape(A=10.0, dimensions=2)
        visualizer = LandscapeVisualizer()

        stats = visualizer.analyze_landscape_statistics(landscape, resolution=50)

        assert "min_value" in stats
        assert "max_value" in stats
        assert "mean_value" in stats
        assert "std_value" in stats
        assert stats["min_value"] < stats["max_value"]

    def test_swarm_visualization(self):
        """Test swarm particle visualization on landscape."""
        landscape = RastriginLandscape(A=5.0, dimensions=2)
        visualizer = LandscapeVisualizer()

        # Create fake particle positions
        particle_positions = [[0.0, 0.0], [1.0, 1.0], [-1.0, 1.0]]
        particle_fitnesses = [0.1, 5.2, 3.8]
        particle_ids = ["p1", "p2", "p3"]

        fig = visualizer.plot_swarm_on_landscape(
            landscape,
            particle_positions,
            particle_fitnesses,
            particle_ids,
            resolution=20,
        )

        assert fig is not None
        assert len(fig.data) > 2  # Should have landscape + particles

    def test_dashboard_creation(self):
        """Test comprehensive dashboard creation."""
        landscape = EcologicalLandscape()
        visualizer = LandscapeVisualizer()

        fig = visualizer.create_dashboard(landscape)

        assert fig is not None
        assert len(fig.data) > 0

    def test_quick_visualize_function(self):
        """Test quick visualization function."""
        fig = quick_visualize("rastrigin", plot_type="2d", A=5.0, dimensions=2)
        assert fig is not None

        fig = quick_visualize("ecological", plot_type="3d")
        assert fig is not None

        # Test invalid plot type
        with pytest.raises(ValueError):
            quick_visualize("rastrigin", plot_type="invalid")

        # Test invalid landscape
        with pytest.raises(ValueError):
            quick_visualize("nonexistent")

    def test_file_saving(self):
        """Test saving visualizations to files."""
        landscape = RastriginLandscape(A=5.0, dimensions=2)
        visualizer = LandscapeVisualizer()

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "test_plot.html")

            # The function is called for its side-effect of saving the file
            # so the returned figure object does not need to be used.
            visualizer.plot_2d_landscape(  # Ruff F841 Fix
                landscape, save_path=save_path, resolution=20
            )

            assert os.path.exists(save_path)
            assert os.path.getsize(save_path) > 0


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_optimization_workflow(self):
        """Test complete optimization workflow."""
        # Create landscape
        landscape = RastriginLandscape(A=10.0, dimensions=2)

        # Create optimizer
        pso = PSO(
            dimensions=2,
            bounds=landscape.metadata.recommended_bounds,
            loss_function=landscape.evaluate,
            population_size=15,
            max_iterations=50,
            random_seed=42,
        )

        # Record initial state
        initial_fitness = pso.swarm_state.global_best_fitness
        # initial_positions = [p.position for p in pso.swarm_state.particles] # Ruff F841 Fix

        # Run optimization
        for i in range(20):
            pso.step()

            # Occasionally force exploration to test functionality
            if i == 10:
                pso.force_exploration_phase()

        # Check results
        final_fitness = pso.swarm_state.global_best_fitness
        final_positions = [p.position for p in pso.swarm_state.particles]

        assert final_fitness < initial_fitness  # Should improve
        assert len(pso.history) == 21  # Initial + 20 steps
        assert pso.swarm_state.iteration == 20

        # Test visualization of results
        visualizer = LandscapeVisualizer()
        fig = visualizer.plot_swarm_on_landscape(
            landscape,
            final_positions,
            [landscape.evaluate(np.array(pos)) for pos in final_positions],
            resolution=30,
        )

        assert fig is not None

    def test_ecological_optimization_workflow(self):
        """Test optimization on ecological landscape."""
        landscape = EcologicalLandscape()

        pso = PSO(
            dimensions=2,
            bounds=landscape.metadata.recommended_bounds,
            loss_function=landscape.evaluate,
            population_size=20,
            max_iterations=100,
            random_seed=42,
        )

        # Run optimization
        for _ in range(30):
            pso.step()

        # Should find reasonable solution
        final_fitness = pso.swarm_state.global_best_fitness
        final_position = pso.swarm_state.global_best_position

        # Should be better than random
        assert final_fitness < 50

        # Position should be within bounds
        assert 0 <= final_position[0] <= 10
        assert 0 <= final_position[1] <= 10

        # Test position description
        description = landscape.describe_position(np.array(final_position))
        assert isinstance(description, str)
        assert len(description) > 10  # Should be meaningful

    def test_multiple_landscapes_comparison(self):
        """Test comparing different landscapes."""
        landscapes = {
            "rastrigin": create_landscape("rastrigin", A=10.0, dimensions=2),
            "ecological": create_landscape("ecological"),
        }

        visualizer = LandscapeVisualizer()
        results = {}

        for name, landscape in landscapes.items():
            # Analyze each landscape
            stats = visualizer.analyze_landscape_statistics(landscape, resolution=50)
            results[name] = stats

            # Test that analysis works
            assert "min_value" in stats
            assert "landscape_type" in stats

        # Results should be different
        assert (
            results["rastrigin"]["landscape_type"]
            != results["ecological"]["landscape_type"]
        )
        assert results["rastrigin"]["min_value"] != results["ecological"]["min_value"]


# Pytest fixtures for common test objects
@pytest.fixture
def simple_loss_function():
    """Simple quadratic loss function for testing."""

    def loss(x):
        return np.sum(x**2)

    return loss


@pytest.fixture
def test_pso(simple_loss_function):
    """PSO instance for testing."""
    return PSO(
        dimensions=2,
        bounds=[(-5, 5), (-5, 5)],
        loss_function=simple_loss_function,
        population_size=10,
        random_seed=42,
    )


@pytest.fixture
def test_landscapes():
    """Dictionary of test landscapes."""
    return {
        "rastrigin": RastriginLandscape(A=10.0, dimensions=2),
        "ecological": EcologicalLandscape(),
        "quadratic": QuadraticLandscape(dimensions=2),
    }


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
