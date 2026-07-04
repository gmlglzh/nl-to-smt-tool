"""
Temporal Policy Solver - Prefix Feasibility Checker

This module provides functions to check whether a trace prefix can be completed
to satisfy temporal policy constraints.
"""

from z3 import *
from typing import Dict, Any
from .temporal_encoder import TemporalEncoder


def check_prefix_feasibility(
    blueprint: dict,
    encoder_plan: dict,
    trace_prefix: dict
) -> dict:
    """
    Check if a trace prefix can be feasibly completed to satisfy the policy.

    This is the core of L3 predictive safety checking: given a partial trace
    (some events have occurred, some states are known), can the Agent continue
    in a way that satisfies all temporal constraints?

    Args:
        blueprint: Temporal policy blueprint containing events, states, time_bound
        encoder_plan: Encoding plan with temporal_constraints and business_constraints
        trace_prefix: Observed trace prefix with events, states, and check requirements

    Returns:
        Dict containing:
            - result: "sat" | "unsat" | "unknown"
            - unsat_core: List of constraint names causing UNSAT (if applicable)
            - model: String representation of satisfying model (if SAT)
            - explanation: Human-readable explanation of result
    """
    # Create encoder and build solver
    encoder = TemporalEncoder(blueprint)
    solver = encoder.build_solver_from_plan(encoder_plan, trace_prefix)

    # Check satisfiability
    result = solver.check()

    response = {
        "result": str(result),
        "unsat_core": [],
        "model": "",
        "explanation": ""
    }

    if result == sat:
        # Satisfiable: there exists a future trace that satisfies the policy
        model = solver.model()
        response["model"] = str(model)
        response["explanation"] = (
            "SAT: A safe execution path exists. The trace prefix can be completed "
            "in a way that satisfies all temporal and business constraints."
        )

    elif result == unsat:
        # Unsatisfiable: no future trace can satisfy the policy
        # Extract unsat core for explanation
        core = solver.unsat_core()
        response["unsat_core"] = [str(c) for c in core]

        # Generate explanation
        core_names = [str(c) for c in core]
        explanation_parts = [
            "UNSAT: No safe execution path exists from this prefix.",
            f"Conflicting constraints ({len(core_names)} in unsat core):"
        ]

        # Categorize constraints in unsat core
        prefix_constraints = [c for c in core_names if c.startswith('prefix_')]
        temporal_constraints = [c for c in core_names if 'main_send_precondition' in c]
        business_constraints = [c for c in core_names if any(
            keyword in c for keyword in ['approval', 'project', 'override', 'emergency', 'encryption']
        )]
        eventually_constraints = [c for c in core_names if 'require_eventually' in c]

        if prefix_constraints:
            explanation_parts.append(f"  - Observed state/events: {len(prefix_constraints)} constraints")
        if temporal_constraints:
            explanation_parts.append(f"  - Temporal ordering requirements: {len(temporal_constraints)} constraints")
        if business_constraints:
            explanation_parts.append(f"  - Business logic constraints: {len(business_constraints)} constraints")
        if eventually_constraints:
            explanation_parts.append(f"  - Future requirements: {len(eventually_constraints)} constraints")

        explanation_parts.append("")
        explanation_parts.append(
            "The system detected that regardless of future actions, "
            "the policy cannot be satisfied due to the current state. "
            "This enables proactive circuit-breaking before policy violation occurs."
        )

        response["explanation"] = "\n".join(explanation_parts)

    else:  # unknown
        response["explanation"] = (
            "UNKNOWN: Z3 solver could not determine satisfiability "
            "(timeout or resource limit reached)."
        )

    return response


def format_result(result: dict, verbose: bool = True) -> str:
    """
    Format the feasibility check result for display.

    Args:
        result: Result dict from check_prefix_feasibility
        verbose: If True, include full details; otherwise show summary only

    Returns:
        Formatted string representation
    """
    lines = []
    lines.append("=" * 70)
    lines.append("TEMPORAL POLICY PREFIX FEASIBILITY CHECK")
    lines.append("=" * 70)
    lines.append(f"Result: {result['result'].upper()}")
    lines.append("")

    if result['result'] == 'unsat':
        lines.append("UNSAT Core:")
        if result['unsat_core']:
            for constraint in result['unsat_core']:
                lines.append(f"  - {constraint}")
        else:
            lines.append("  (empty)")
        lines.append("")

    lines.append("Explanation:")
    lines.append(result['explanation'])

    if verbose and result['result'] == 'sat' and result['model']:
        lines.append("")
        lines.append("Satisfying Model (sample):")
        model_lines = result['model'].split('\n')[:20]  # Show first 20 lines
        for line in model_lines:
            lines.append(f"  {line}")
        if len(result['model'].split('\n')) > 20:
            lines.append("  ...")

    lines.append("=" * 70)
    return "\n".join(lines)
