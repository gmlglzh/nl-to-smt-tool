#!/usr/bin/env python3
"""
NL to SMT Policy Translator - Web Application

A simple web interface for translating natural language temporal policies
into SMT constraints using LLM assistance.
"""

from flask import Flask, render_template, request, jsonify
import json
import sys
from pathlib import Path

# Add temporal encoder path
sys.path.insert(0, str(Path(__file__).parent))

from temporal_engine.nl_generator import generate_blueprint, generate_encoder_plan
from temporal_engine.temporal_encoder import TemporalEncoder
from temporal_engine.temporal_solver import check_prefix_feasibility

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate Blueprint and Encoder Plan from natural language policy.

    Request JSON:
        {
            "nl_policy": "natural language policy text",
            "api_key": "LLM API key",
            "base_url": "LLM API base URL (optional)"
        }

    Response JSON:
        {
            "success": true/false,
            "blueprint": {...},
            "encoder_plan": {...},
            "error": "error message (if failed)"
        }
    """
    try:
        data = request.json
        nl_policy = data.get('nl_policy', '').strip()
        api_key = data.get('api_key', '').strip()
        base_url = data.get('base_url', 'https://api.deepseek.com').strip()

        if not nl_policy:
            return jsonify({
                'success': False,
                'error': 'NL policy cannot be empty'
            })

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            })

        # Generate blueprint
        print(f"Generating blueprint for policy: {nl_policy[:100]}...")
        blueprint = generate_blueprint(nl_policy, api_key, base_url)

        # Generate encoder plan
        print(f"Generating encoder plan...")
        encoder_plan = generate_encoder_plan(nl_policy, blueprint, api_key, base_url)

        return jsonify({
            'success': True,
            'blueprint': blueprint,
            'encoder_plan': encoder_plan
        })

    except Exception as e:
        print(f"Error in generate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/validate', methods=['POST'])
def validate():
    """
    Validate the generated JSON by building a solver.

    Request JSON:
        {
            "blueprint": {...},
            "encoder_plan": {...},
            "trace_prefix": {...} (optional)
        }

    Response JSON:
        {
            "success": true/false,
            "result": "sat/unsat/unknown",
            "num_constraints": 42,
            "error": "error message (if failed)"
        }
    """
    try:
        data = request.json
        blueprint = data.get('blueprint')
        encoder_plan = data.get('encoder_plan')
        trace_prefix = data.get('trace_prefix')

        if not blueprint or not encoder_plan:
            return jsonify({
                'success': False,
                'error': 'Blueprint and encoder plan are required'
            })

        # Build encoder and solver
        encoder = TemporalEncoder(blueprint)
        solver = encoder.build_solver_from_plan(encoder_plan, trace_prefix)

        # Check satisfiability
        result = str(solver.check())
        num_constraints = len(solver.assertions())

        return jsonify({
            'success': True,
            'result': result,
            'num_constraints': num_constraints
        })

    except Exception as e:
        print(f"Error in validate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/test_scenario', methods=['POST'])
def test_scenario():
    """
    Test a specific scenario (trace prefix) against the policy.

    Request JSON:
        {
            "blueprint": {...},
            "encoder_plan": {...},
            "trace_prefix": {...}
        }

    Response JSON:
        {
            "success": true/false,
            "result": "sat/unsat/unknown",
            "explanation": "human-readable explanation",
            "unsat_core": [...] (if unsat),
            "error": "error message (if failed)"
        }
    """
    try:
        data = request.json
        blueprint = data.get('blueprint')
        encoder_plan = data.get('encoder_plan')
        trace_prefix = data.get('trace_prefix')

        if not all([blueprint, encoder_plan, trace_prefix]):
            return jsonify({
                'success': False,
                'error': 'Blueprint, encoder plan, and trace prefix are required'
            })

        # Check feasibility
        result = check_prefix_feasibility(blueprint, encoder_plan, trace_prefix)

        return jsonify({
            'success': True,
            'result': result['result'],
            'explanation': result['explanation'],
            'unsat_core': result.get('unsat_core', [])
        })

    except Exception as e:
        print(f"Error in test_scenario: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/examples', methods=['GET'])
def get_examples():
    """
    Get list of example policies.

    Response JSON:
        {
            "examples": [
                {
                    "name": "Email Runtime Safety",
                    "nl_policy": "...",
                    "blueprint": {...},
                    "encoder_plan": {...}
                },
                ...
            ]
        }
    """
    examples_dir = Path(__file__).parent / 'examples'
    examples = []

    if examples_dir.exists():
        for example_file in examples_dir.glob('*.json'):
            try:
                with open(example_file, 'r', encoding='utf-8') as f:
                    example_data = json.load(f)
                    examples.append(example_data)
            except Exception as e:
                print(f"Error loading example {example_file}: {e}")

    return jsonify({'examples': examples})


if __name__ == '__main__':
    print("=" * 70)
    print("NL to SMT Policy Translator")
    print("=" * 70)
    print()
    print("Starting web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)

    app.run(host='0.0.0.0', port=5000, debug=True)
