#!/usr/bin/env python3
"""
Quick test script to verify the installation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Testing NL to SMT Tool Installation")
print("=" * 70)
print()

# Test 1: Check Python version
print("1. Checking Python version...")
if sys.version_info < (3, 8):
    print("   [ERROR] Python 3.8+ required")
    sys.exit(1)
print(f"   [OK] Python {sys.version_info.major}.{sys.version_info.minor}")

# Test 2: Check dependencies
print()
print("2. Checking dependencies...")
try:
    import flask
    print(f"   [OK] Flask {flask.__version__}")
except ImportError:
    print("   [ERROR] Flask not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import z3
    print(f"   [OK] z3-solver installed")
except ImportError:
    print("   [ERROR] z3-solver not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import requests
    print(f"   [OK] requests {requests.__version__}")
except ImportError:
    print("   [ERROR] requests not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Check temporal_engine modules
print()
print("3. Checking temporal_engine modules...")
try:
    from temporal_engine.temporal_encoder import TemporalEncoder
    from temporal_engine.temporal_solver import check_prefix_feasibility
    from temporal_engine.nl_generator import generate_blueprint, generate_encoder_plan
    print("   [OK] All temporal_engine modules found")
except ImportError as e:
    print(f"   [ERROR] Module import failed: {e}")
    sys.exit(1)

# Test 4: Quick functional test
print()
print("4. Running quick functional test...")
try:
    blueprint = {
        "name": "test",
        "time_bound": 5,
        "events": ["event_a", "event_b"],
        "states": ["state_x"]
    }
    encoder = TemporalEncoder(blueprint)
    encoder.make_trace_vars()
    print("   [OK] Temporal encoder working")
except Exception as e:
    print(f"   [ERROR] Functional test failed: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("All tests passed! You can now run:")
print("  python app.py")
print()
print("Then open: http://localhost:5000")
print("=" * 70)
