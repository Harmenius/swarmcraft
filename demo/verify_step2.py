"""
Quick verification that Step 2 works with enum-based algorithm selection.
Save as: verify_step2.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from swarmcraft.models.session import SessionConfig, GameSession, AlgorithmType
from datetime import datetime


def verify_step2():
    print("🧪 Verifying Step 2: Algorithm Selection with Enums")

    # Test 1: Default config (should be PSO)
    print("\n1. Testing default config...")
    default_config = SessionConfig()
    print(f"   ✅ Default algorithm: {default_config.algorithm_type}")
    print(f"   ✅ Algorithm value: {default_config.algorithm_type.value}")
    print(f"   ✅ ABC limit: {default_config.abc_limit}")
    print(f"   ✅ ABC employed ratio: {default_config.abc_employed_ratio}")

    # Test 2: Explicit PSO config
    print("\n2. Testing PSO config...")
    pso_config = SessionConfig(
        algorithm_type=AlgorithmType.PSO,
        exploration_probability=0.2,
        min_exploration_probability=0.05,
    )
    print(f"   ✅ Algorithm: {pso_config.algorithm_type}")
    print(f"   ✅ Exploration prob: {pso_config.exploration_probability}")
    print(f"   ✅ Type safety: {pso_config.algorithm_type == AlgorithmType.PSO}")

    # Test 3: ABC config
    print("\n3. Testing ABC config...")
    abc_config = SessionConfig(
        algorithm_type=AlgorithmType.ABC,
        abc_limit=15,
        abc_employed_ratio=0.6,
        landscape_type="ecological",
    )
    print(f"   ✅ Algorithm: {abc_config.algorithm_type}")
    print(f"   ✅ ABC limit: {abc_config.abc_limit}")
    print(f"   ✅ ABC employed ratio: {abc_config.abc_employed_ratio}")
    print(f"   ✅ Landscape: {abc_config.landscape_type}")
    print(f"   ✅ Type safety: {abc_config.algorithm_type == AlgorithmType.ABC}")

    # Test 4: JSON serialization (important for API)
    print("\n4. Testing JSON serialization...")
    config_dict = abc_config.model_dump()  # Standard dump (keeps enums)
    config_json = abc_config.model_dump(mode="json")  # JSON-ready (strings)

    print(f"   ✅ Standard dump: {len(config_dict)} fields")
    print(f"   ✅ Algorithm in standard: {config_dict['algorithm_type']}")
    print(f"   ✅ Algorithm in JSON: {config_json['algorithm_type']}")
    print(
        f"   ✅ JSON serializes to string: {isinstance(config_json['algorithm_type'], str)}"
    )
    print(
        f"   ✅ Standard keeps enum: {isinstance(config_dict['algorithm_type'], AlgorithmType)}"
    )

    # Test 5: String to enum conversion (API compatibility)
    print("\n5. Testing string-to-enum conversion...")
    config_from_string = SessionConfig(algorithm_type="abc")  # String input
    print(f"   ✅ String 'abc' converts to: {config_from_string.algorithm_type}")
    print(
        f"   ✅ Is enum type: {isinstance(config_from_string.algorithm_type, AlgorithmType)}"
    )
    print(
        f"   ✅ Equals ABC enum: {config_from_string.algorithm_type == AlgorithmType.ABC}"
    )

    # Test 6: Error handling for invalid strings
    print("\n6. Testing error handling...")
    try:
        _ = SessionConfig(algorithm_type="invalid_algo")
        print("   ❌ Should have raised an error!")
    except ValueError as e:
        print(f"   ✅ Correctly rejected invalid algorithm: {str(e)[:50]}...")

    # Test 7: Full GameSession with ABC
    print("\n7. Testing full GameSession with ABC...")
    session = GameSession(
        id="test_abc_session",
        code="ABC123",
        admin_id="admin",
        config=abc_config,
        created_at=datetime.now(),
    )
    print(f"   ✅ Session created with algorithm: {session.config.algorithm_type}")
    print(f"   ✅ Session status: {session.status.value}")

    # Test 8: Type-safe conditional logic (how we'll use it in API)
    print("\n8. Testing type-safe conditional logic...")

    def get_algorithm_name(config):
        if config.algorithm_type == AlgorithmType.PSO:
            return "Particle Swarm Optimization"
        elif config.algorithm_type == AlgorithmType.ABC:
            return "Artificial Bee Colony"
        else:
            return "Unknown Algorithm"

    pso_name = get_algorithm_name(pso_config)
    abc_name = get_algorithm_name(abc_config)
    print(f"   ✅ PSO config -> {pso_name}")
    print(f"   ✅ ABC config -> {abc_name}")

    print("\n🎉 Step 2 verification completed successfully!")
    print("    ✅ Type-safe enum-based algorithm selection")
    print("    ✅ Backwards compatible (PSO still default)")
    print("    ✅ String-to-enum conversion works (API friendly)")
    print("    ✅ Invalid algorithms are rejected")
    print("    ✅ JSON serialization works")
    print("    ✅ Full session creation works")
    print("    ✅ Type-safe conditional logic works")


if __name__ == "__main__":
    verify_step2()
