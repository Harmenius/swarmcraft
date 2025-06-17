"""
Algorithm factory for creating swarm optimizers based on session configuration.

Add this as: src/swarmcraft/core/algorithm_factory.py
"""

from swarmcraft.models.session import SessionConfig, AlgorithmType
from swarmcraft.core.pso import PSO
from swarmcraft.core.abc import ABC
from swarmcraft.core.swarm_base import SwarmOptimizer


def create_optimizer(
    config: SessionConfig, participants_count: int, landscape
) -> SwarmOptimizer:
    """
    Create the appropriate swarm optimizer based on session configuration.

    Args:
        config: Session configuration containing algorithm type and parameters
        participants_count: Number of participants in the session
        landscape: The optimization landscape

    Returns:
        Configured swarm optimizer instance (PSO or ABC)

    Raises:
        ValueError: If algorithm type is not supported
    """

    # Common parameters for all algorithms
    common_params = {
        "dimensions": 2,
        "bounds": landscape.metadata.recommended_bounds,
        "loss_function": landscape.evaluate,
        "population_size": participants_count,
        "max_iterations": config.max_iterations,
    }

    if config.algorithm_type == AlgorithmType.PSO:
        return _create_pso(config, common_params)
    elif config.algorithm_type == AlgorithmType.ABC:
        return _create_abc(config, common_params)
    else:
        raise ValueError(f"Unsupported algorithm type: {config.algorithm_type}")


def _create_pso(config: SessionConfig, common_params: dict) -> PSO:
    """Create PSO optimizer with session-specific parameters."""
    pso_params = {
        **common_params,
        "exploration_probability": config.exploration_probability,
        "min_exploration_probability": config.min_exploration_probability,
    }

    return PSO(**pso_params)


def _create_abc(config: SessionConfig, common_params: dict) -> ABC:
    """Create ABC optimizer with session-specific parameters."""
    abc_params = {
        **common_params,
        "limit": config.abc_limit or 10,
        "employed_ratio": config.abc_employed_ratio or 0.5,
    }

    return ABC(**abc_params)


def get_algorithm_display_name(algorithm_type: AlgorithmType) -> str:
    """Get human-readable algorithm name for display purposes."""
    display_names = {
        AlgorithmType.PSO: "Particle Swarm Optimization",
        AlgorithmType.ABC: "Artificial Bee Colony",
    }
    return display_names.get(algorithm_type, "Unknown Algorithm")


def get_algorithm_description(algorithm_type: AlgorithmType) -> str:
    """Get algorithm description for educational purposes."""
    descriptions = {
        AlgorithmType.PSO: "Particles follow personal and global best solutions, with some exploring randomly.",
        AlgorithmType.ABC: "Bees work as employed foragers, onlookers choosing good sources, and scouts exploring new areas.",
    }
    return descriptions.get(
        algorithm_type, "Swarm intelligence optimization algorithm."
    )


def get_algorithm_config_info(config: SessionConfig) -> dict:
    """Get algorithm-specific configuration information for display."""
    if config.algorithm_type == AlgorithmType.PSO:
        return {
            "algorithm": "PSO",
            "exploration_probability": config.exploration_probability,
            "min_exploration_probability": config.min_exploration_probability,
            "parameters": {
                "exploration_starts_at": f"{config.exploration_probability:.1%}",
                "exploration_ends_at": f"{(config.min_exploration_probability or config.exploration_probability):.1%}",
            },
        }
    elif config.algorithm_type == AlgorithmType.ABC:
        return {
            "algorithm": "ABC",
            "abc_limit": config.abc_limit,
            "abc_employed_ratio": config.abc_employed_ratio,
            "parameters": {
                "employed_bees": f"{(config.abc_employed_ratio or 0.5):.1%}",
                "abandonment_limit": config.abc_limit or 10,
            },
        }
    else:
        return {"algorithm": "Unknown", "parameters": {}}
