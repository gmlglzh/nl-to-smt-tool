"""
NL to JSON Generator for Temporal Policies

This module provides LLM-based translation from natural language policies
to Blueprint JSON and Encoder Plan JSON.
"""

import json
import requests
from typing import Dict, Any


def call_llm(prompt: str, api_key: str, base_url: str = "https://api.deepseek.com") -> str:
    """
    Call LLM API with a prompt.

    Args:
        prompt: The prompt to send
        api_key: API key
        base_url: API base URL

    Returns:
        Generated text response
    """
    url = f"{base_url}/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()
    return result['choices'][0]['message']['content']


def generate_blueprint(nl_policy: str, api_key: str, base_url: str = "https://api.deepseek.com") -> Dict[str, Any]:
    """Generate Temporal Blueprint JSON from natural language policy."""
    prompt = f"""You are a temporal policy expert. Convert the following natural language policy into a Temporal Blueprint JSON.

CRITICAL DISTINCTIONS:

1. EVENTS are instantaneous occurrences (completed actions):
   - "email_sent" (not "send_email" which sounds like an action to do)
   - "approval_received" (not "get_approval")
   - "drug_interaction_detected"
   - "physician_override_issued"

2. STATES are persistent conditions that span time:
   - "alert_mode_active"
   - "emergency_protocol_active"
   - "high_risk_medication_pending"

3. For "blocks X" statements:
   - X should be an EVENT that can occur
   - Example: "emergency mode blocks automated refills"
     → state: "emergency_mode_active"
     → event: "automated_refill_requested" (the thing being blocked)

4. Use PAST TENSE for events, ADJECTIVE/NOUN for states

Blueprint JSON format:
{{
  "name": "policy_name",
  "description": "brief description",
  "time_bound": 10,
  "events": ["event1", "event2", ...],
  "states": ["state1", "state2", ...]
}}

Example:
Policy: "Before sending email, approval is required. Emergency mode blocks email sending."
→ events: ["approval_received", "email_sent"]
→ states: ["emergency_mode_active"]

Natural Language Policy:
{nl_policy}

Output ONLY valid JSON, no explanations:"""

    response = call_llm(prompt, api_key, base_url)

    start = response.find('{')
    end = response.rfind('}') + 1
    json_str = response[start:end]

    return json.loads(json_str)


def generate_encoder_plan(nl_policy: str, blueprint: Dict[str, Any], api_key: str, base_url: str = "https://api.deepseek.com") -> Dict[str, Any]:
    """Generate Encoder Plan JSON from natural language policy and blueprint."""
    prompt = f"""You are a temporal logic expert. Convert the following natural language policy into an Encoder Plan JSON.

Blueprint (events and states available):
{json.dumps(blueprint, indent=2)}

TEMPLATE SELECTION GUIDE:

1. "X requires Y to happen first" / "Before X, Y must occur"
   → always_previously_requires

2. "State S persists from event A until event B"
   → state_persistence_until

3. "State S blocks/prevents event E"
   → always_prevents_while_state

4. "Event A requires event B within N steps"
   → always_within_requires

5. "Event E triggers state S in the next step"
   → always_next_requires

6. "Event E can only happen when state S is true/false"
   → event_requires_state

COMMON MISTAKES TO AVOID:

1. Don't use always_within_requires for "event → state in next step"
   → Use always_next_requires instead

2. For "state blocks X", X must be an EVENT in the blueprint
   → Not a "block_X" action event

3. For conditional requirements like "high-risk medications require X":
   → Either create separate events (prescribe_high_risk vs prescribe_normal)
   → OR use event_requires_state with a "high_risk_pending" state

Available constraint templates:

always_previously_requires:
{{
  "name": "constraint_name",
  "kind": "always_previously_requires",
  "trigger": "event_name",
  "all_before": ["event1", "event2"],
  "one_of_before": [["eventA"], ["eventB", "eventC"]],
  "description": "explanation"
}}

state_persistence_until:
{{
  "name": "constraint_name",
  "kind": "state_persistence_until",
  "start_event": "event_name",
  "state": "state_name",
  "end_event": "event_name",
  "description": "explanation"
}}

always_prevents_while_state:
{{
  "name": "constraint_name",
  "kind": "always_prevents_while_state",
  "state": "state_name",
  "event": "event_name",
  "description": "explanation"
}}

always_within_requires:
{{
  "name": "constraint_name",
  "kind": "always_within_requires",
  "trigger": "event_name",
  "required": "event_name",
  "within": 2,
  "description": "explanation"
}}

always_next_requires:
{{
  "name": "constraint_name",
  "kind": "always_next_requires",
  "trigger": "event_name",
  "required_state": "state_name",
  "description": "explanation"
}}

event_requires_state:
{{
  "name": "constraint_name",
  "kind": "event_requires_state",
  "event": "event_name",
  "state": "state_name",
  "value": true,
  "description": "explanation"
}}

state_implication:
{{
  "name": "constraint_name",
  "kind": "state_implication",
  "if_state": "state_name",
  "if_value": true,
  "then_state": "state_name",
  "then_value": true,
  "description": "explanation"
}}

state_blocks_event:
{{
  "name": "constraint_name",
  "kind": "state_blocks_event",
  "state": "state_name",
  "value": true,
  "event": "event_name",
  "description": "explanation"
}}

Output format:
{{
  "name": "encoder_plan_name",
  "temporal_constraints": [...],
  "business_constraints": [...]
}}

Natural Language Policy:
{nl_policy}

Think step by step:
1. Identify each policy statement
2. Choose the most appropriate template
3. Map events/states from blueprint
4. Double-check event vs state usage

Output ONLY valid JSON:"""

    response = call_llm(prompt, api_key, base_url)

    start = response.find('{')
    end = response.rfind('}') + 1
    json_str = response[start:end]

    return json.loads(json_str)
