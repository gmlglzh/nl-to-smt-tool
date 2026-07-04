"""
Temporal Policy Encoder - Bounded Trace Z3 Encoder

This module provides deterministic Z3 encoding for bounded trace temporal policies.
It supports temporal constraints like 'always_previously_requires', 'eventually', etc.
"""

from z3 import *
from typing import List, Dict, Any, Tuple, Optional


class TemporalEncoder:
    """
    Encodes temporal policies into Z3 constraints for bounded trace verification.

    A trace is a sequence of events and states over discrete time steps [0, T-1].
    Each event is modeled as a Bool variable event_name_t.
    Each state is modeled as a Bool variable state_name_t.
    """

    def __init__(self, blueprint: dict):
        """
        Initialize encoder with a temporal blueprint.

        Args:
            blueprint: Dict containing:
                - events: List of event names
                - states: List of state names
                - time_bound: Maximum trace length T
        """
        self.blueprint = blueprint
        self.events = blueprint.get('events', [])
        self.states = blueprint.get('states', [])
        self.time_bound = blueprint.get('time_bound', 10)
        self.trace_vars = None

    def make_trace_vars(self) -> Dict[str, List]:
        """
        Create Z3 Bool variables for all events and states across all time steps.

        Returns:
            Dict with keys 'events' and 'states', each mapping names to lists of Bool vars.
            Example: {'events': {'send_email': [Bool('send_email_0'), ...]}, ...}
        """
        trace_vars = {'events': {}, 'states': {}}

        for event in self.events:
            trace_vars['events'][event] = [
                Bool(f"{event}_{t}") for t in range(self.time_bound)
            ]

        for state in self.states:
            trace_vars['states'][state] = [
                Bool(f"{state}_{t}") for t in range(self.time_bound)
            ]

        self.trace_vars = trace_vars
        return trace_vars

    def occurred_before(self, event_vars: List, t: int) -> Any:
        """
        Create a Z3 expression: event occurred at least once before time t.

        Args:
            event_vars: List of Bool variables for an event across time steps
            t: Current time step (exclusive upper bound)

        Returns:
            Z3 expression: Or(event_0, event_1, ..., event_{t-1})
            If t <= 0, returns False (no time before t=0)
        """
        if t <= 0:
            return BoolVal(False)
        return Or([event_vars[i] for i in range(t)])

    def encode_always_previously_requires(
        self,
        solver: Solver,
        trigger: str,
        all_before: List[str],
        one_of_before: List[List[str]],
        constraint_name: str
    ):
        """
        Encode: For all t, if trigger[t] then:
          - All events in all_before must have occurred_before(t)
          - At least one group in one_of_before must be satisfied

        Args:
            solver: Z3 solver instance
            trigger: Trigger event name
            all_before: List of events that must all occur before trigger
            one_of_before: List of event groups, at least one group must be satisfied.
                          Each group is a list of events that must all occur before trigger.
            constraint_name: Name for tracking in unsat_core
        """
        trigger_vars = self.trace_vars['events'][trigger]

        for t in range(self.time_bound):
            # Antecedent: trigger fires at time t
            antecedent = trigger_vars[t]

            # Consequent part 1: all_before events
            all_before_clauses = []
            for event in all_before:
                event_vars = self.trace_vars['events'][event]
                all_before_clauses.append(self.occurred_before(event_vars, t))

            # Consequent part 2: one_of_before groups
            one_of_clauses = []
            for group in one_of_before:
                group_clauses = []
                for event in group:
                    event_vars = self.trace_vars['events'][event]
                    group_clauses.append(self.occurred_before(event_vars, t))
                # All events in this group must have occurred
                one_of_clauses.append(And(group_clauses))

            # Build full consequent
            consequent_parts = all_before_clauses.copy()
            if one_of_clauses:
                consequent_parts.append(Or(one_of_clauses))

            consequent = And(consequent_parts) if consequent_parts else BoolVal(True)

            # Add constraint with tracking
            constraint = Implies(antecedent, consequent)
            solver.assert_and_track(constraint, f"{constraint_name}_t{t}")

    def encode_event_requires_state(
        self,
        solver: Solver,
        event: str,
        state: str,
        value: bool,
        constraint_name: str
    ):
        """
        Encode: For all t, event[t] -> state[t] == value

        Args:
            solver: Z3 solver instance
            event: Event name
            state: State name
            value: Required state value (True or False)
            constraint_name: Name for tracking
        """
        event_vars = self.trace_vars['events'][event]
        state_vars = self.trace_vars['states'][state]

        for t in range(self.time_bound):
            if value:
                constraint = Implies(event_vars[t], state_vars[t])
            else:
                constraint = Implies(event_vars[t], Not(state_vars[t]))
            solver.assert_and_track(constraint, f"{constraint_name}_t{t}")

    def encode_state_implication(
        self,
        solver: Solver,
        if_state: str,
        if_value: bool,
        then_state: str,
        then_value: bool,
        constraint_name: str
    ):
        """
        Encode: For all t, if_state[t] == if_value -> then_state[t] == then_value

        Args:
            solver: Z3 solver instance
            if_state: Condition state name
            if_value: Condition state value
            then_state: Consequent state name
            then_value: Consequent state value
            constraint_name: Name for tracking
        """
        if_state_vars = self.trace_vars['states'][if_state]
        then_state_vars = self.trace_vars['states'][then_state]

        for t in range(self.time_bound):
            # Build antecedent
            if if_value:
                antecedent = if_state_vars[t]
            else:
                antecedent = Not(if_state_vars[t])

            # Build consequent
            if then_value:
                consequent = then_state_vars[t]
            else:
                consequent = Not(then_state_vars[t])

            constraint = Implies(antecedent, consequent)
            solver.assert_and_track(constraint, f"{constraint_name}_t{t}")

    def encode_state_blocks_event(
        self,
        solver: Solver,
        state: str,
        value: bool,
        event: str,
        constraint_name: str
    ):
        """
        Encode: For all t, state[t] == value -> Not(event[t])

        Args:
            solver: Z3 solver instance
            state: State name
            value: State value that blocks the event
            event: Event name that is blocked
            constraint_name: Name for tracking
        """
        state_vars = self.trace_vars['states'][state]
        event_vars = self.trace_vars['events'][event]

        for t in range(self.time_bound):
            if value:
                antecedent = state_vars[t]
            else:
                antecedent = Not(state_vars[t])

            constraint = Implies(antecedent, Not(event_vars[t]))
            solver.assert_and_track(constraint, f"{constraint_name}_t{t}")

    def encode_prefix_constraints(
        self,
        solver: Solver,
        trace_prefix: dict
    ):
        """
        Encode constraints from a trace prefix (observed events and states).

        Args:
            solver: Z3 solver instance
            trace_prefix: Dict containing:
                - prefix_length: Number of observed time steps
                - events: List of {time, event} dicts
                - states: List of {time, state, value} dicts
        """
        prefix_length = trace_prefix.get('prefix_length', 0)

        # Collect which (event, time) pairs were explicitly observed
        observed_event_time_pairs = set()
        for event_obs in trace_prefix.get('events', []):
            t = event_obs['time']
            event = event_obs['event']

            # If event is not in blueprint, warn and skip
            if event not in self.trace_vars['events']:
                print(f"Warning: Event '{event}' at time {t} not in blueprint, ignoring")
                continue

            observed_event_time_pairs.add((event, t))
            event_vars = self.trace_vars['events'][event]
            if t < len(event_vars):
                solver.assert_and_track(event_vars[t], f"prefix_event_{event}_t{t}")

        # For each blueprint event and each time step in prefix:
        # if not observed at that (event, time), assert Not(event[t])
        for event in self.events:
            event_vars = self.trace_vars['events'][event]
            for t in range(prefix_length):
                if (event, t) not in observed_event_time_pairs:
                    solver.assert_and_track(Not(event_vars[t]), f"prefix_no_{event}_t{t}")

        # Encode observed states
        # States persist from their observation point forward (frame axiom)
        for state_obs in trace_prefix.get('states', []):
            t = state_obs['time']
            state = state_obs['state']
            value = state_obs['value']

            if state not in self.trace_vars['states']:
                print(f"Warning: State '{state}' at time {t} not in blueprint, ignoring")
                continue

            state_vars = self.trace_vars['states'][state]

            # State holds at observation time and persists forward
            for time_step in range(t, self.time_bound):
                if value:
                    solver.assert_and_track(state_vars[time_step], f"prefix_state_{state}_t{time_step}")
                else:
                    solver.assert_and_track(Not(state_vars[time_step]), f"prefix_state_{state}_t{time_step}")

    def encode_require_eventually(
        self,
        solver: Solver,
        event: str,
        start_t: int
    ):
        """
        Encode: event must occur at least once in [start_t, T-1]

        Args:
            solver: Z3 solver instance
            event: Event name that must eventually occur
            start_t: Starting time step (inclusive)
        """
        event_vars = self.trace_vars['events'][event]

        # Create disjunction: event occurs at some t >= start_t
        eventually_clauses = [event_vars[t] for t in range(start_t, self.time_bound)]

        if eventually_clauses:
            constraint = Or(eventually_clauses)
            solver.assert_and_track(constraint, f"require_eventually_{event}")
        else:
            # No future time steps available
            solver.assert_and_track(BoolVal(False), f"require_eventually_{event}_impossible")

    def encode_always_prevents_while_state(
        self,
        solver: Solver,
        state: str,
        event: str,
        constraint_name: str
    ):
        """
        Encode: For all t, state[t] -> Not(event[t])

        Args:
            solver: Z3 solver instance
            state: State name that prevents the event
            event: Event name that is blocked
            constraint_name: Name for tracking
        """
        state_vars = self.trace_vars['states'][state]
        event_vars = self.trace_vars['events'][event]

        for t in range(self.time_bound):
            constraint = Implies(state_vars[t], Not(event_vars[t]))
            solver.assert_and_track(constraint, f"{constraint_name}_t{t}")

    def encode_always_within_requires(
        self,
        solver: Solver,
        trigger: str,
        required: str,
        within: int,
        constraint_name: str
    ):
        """
        Encode: For all t, trigger[t] -> Or(required[t], required[t+1], ..., required[min(t+k, T-1)])
        where k = within

        Args:
            solver: Z3 solver instance
            trigger: Trigger event name
            required: Required event name
            within: Window size (number of steps)
            constraint_name: Name for tracking
        """
        trigger_vars = self.trace_vars['events'][trigger]
        required_vars = self.trace_vars['events'][required]

        for t in range(self.time_bound):
            # Build window [t, min(t + within, T-1)]
            window_end = min(t + within, self.time_bound - 1)
            window_clauses = [required_vars[i] for i in range(t, window_end + 1)]

            if window_clauses:
                consequent = Or(window_clauses)
            else:
                # Empty window (should not happen if within >= 0)
                consequent = BoolVal(False)

            constraint = Implies(trigger_vars[t], consequent)
            solver.assert_and_track(constraint, f"{constraint_name}_t{t}")

    def encode_always_next_requires(
        self,
        solver: Solver,
        trigger: str,
        required_state: str,
        constraint_name: str
    ):
        """
        Encode: For all t in [0, T-2], trigger[t] -> required_state[t+1]
                For t = T-1, trigger[T-1] -> False

        Args:
            solver: Z3 solver instance
            trigger: Trigger event name
            required_state: Required state name in next step
            constraint_name: Name for tracking
        """
        trigger_vars = self.trace_vars['events'][trigger]
        state_vars = self.trace_vars['states'][required_state]

        for t in range(self.time_bound):
            if t < self.time_bound - 1:
                # Normal case: next state exists
                constraint = Implies(trigger_vars[t], state_vars[t + 1])
                solver.assert_and_track(constraint, f"{constraint_name}_t{t}")
            else:
                # Last time step: trigger implies False
                constraint = Implies(trigger_vars[t], BoolVal(False))
                solver.assert_and_track(constraint, f"{constraint_name}_t{t}_last")

    def encode_state_persistence_until(
        self,
        solver: Solver,
        start_event: str,
        state: str,
        end_event: str,
        constraint_name: str
    ):
        """
        Encode: For all t, start_event[t] -> state[t]
                For all t in [0, T-2], And(state[t], Not(end_event[t])) -> state[t+1]

        Args:
            solver: Z3 solver instance
            start_event: Event that initiates the state
            state: State name that persists
            end_event: Event that ends the state persistence
            constraint_name: Name for tracking
        """
        start_vars = self.trace_vars['events'][start_event]
        state_vars = self.trace_vars['states'][state]
        end_vars = self.trace_vars['events'][end_event]

        # Constraint 1: start_event[t] -> state[t]
        for t in range(self.time_bound):
            constraint = Implies(start_vars[t], state_vars[t])
            solver.assert_and_track(constraint, f"{constraint_name}_start_t{t}")

        # Constraint 2: state[t] AND Not(end_event[t]) -> state[t+1]
        for t in range(self.time_bound - 1):
            antecedent = And(state_vars[t], Not(end_vars[t]))
            consequent = state_vars[t + 1]
            constraint = Implies(antecedent, consequent)
            solver.assert_and_track(constraint, f"{constraint_name}_persist_t{t}")

    def build_solver_from_plan(self, encoder_plan: dict, trace_prefix: Optional[dict] = None) -> Solver:
        """
        Build a complete Z3 solver from an encoder plan and optional trace prefix.

        Args:
            encoder_plan: Dict containing constraint specifications
            trace_prefix: Optional trace prefix to encode

        Returns:
            Z3 Solver instance with all constraints added
        """
        solver = Solver()

        # Create trace variables
        self.make_trace_vars()

        # Encode temporal constraints
        for constraint in encoder_plan.get('temporal_constraints', []):
            kind = constraint['kind']

            if kind == 'always_previously_requires':
                self.encode_always_previously_requires(
                    solver,
                    trigger=constraint['trigger'],
                    all_before=constraint['all_before'],
                    one_of_before=constraint['one_of_before'],
                    constraint_name=constraint['name']
                )
            elif kind == 'always_prevents_while_state':
                self.encode_always_prevents_while_state(
                    solver,
                    state=constraint['state'],
                    event=constraint['event'],
                    constraint_name=constraint['name']
                )
            elif kind == 'always_within_requires':
                self.encode_always_within_requires(
                    solver,
                    trigger=constraint['trigger'],
                    required=constraint['required'],
                    within=constraint['within'],
                    constraint_name=constraint['name']
                )
            elif kind == 'always_next_requires':
                self.encode_always_next_requires(
                    solver,
                    trigger=constraint['trigger'],
                    required_state=constraint['required_state'],
                    constraint_name=constraint['name']
                )
            elif kind == 'state_persistence_until':
                self.encode_state_persistence_until(
                    solver,
                    start_event=constraint['start_event'],
                    state=constraint['state'],
                    end_event=constraint['end_event'],
                    constraint_name=constraint['name']
                )

        # Encode business constraints
        for constraint in encoder_plan.get('business_constraints', []):
            kind = constraint['kind']

            if kind == 'event_requires_state':
                self.encode_event_requires_state(
                    solver,
                    event=constraint['event'],
                    state=constraint['state'],
                    value=constraint['value'],
                    constraint_name=constraint['name']
                )
            elif kind == 'state_implication':
                self.encode_state_implication(
                    solver,
                    if_state=constraint['if_state'],
                    if_value=constraint['if_value'],
                    then_state=constraint['then_state'],
                    then_value=constraint['then_value'],
                    constraint_name=constraint['name']
                )
            elif kind == 'state_blocks_event':
                self.encode_state_blocks_event(
                    solver,
                    state=constraint['state'],
                    value=constraint['value'],
                    event=constraint['event'],
                    constraint_name=constraint['name']
                )

        # Encode trace prefix if provided
        if trace_prefix:
            self.encode_prefix_constraints(solver, trace_prefix)

            # Encode require_eventually if specified
            check = trace_prefix.get('check', {})
            if check.get('require_eventually'):
                event = check['require_eventually']
                start_t = trace_prefix.get('prefix_length', 0)
                self.encode_require_eventually(solver, event, start_t)

        return solver
