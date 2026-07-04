# NL to SMT Policy Translator

A web-based tool for translating natural language temporal policies into formal SMT constraints using LLM assistance.

## Features

- 🤖 **LLM-Assisted Translation**: Uses DeepSeek (or compatible) API to generate Blueprint and Encoder Plan JSON from natural language
- ✏️ **Editable Results**: Generated JSON can be manually edited and validated
- ✅ **Real-time Validation**: Build Z3 solver and check constraint satisfiability
- 🧪 **Scenario Testing**: Test specific execution traces against the policy
- 📚 **Template Reference**: Built-in documentation for all constraint templates
- 🎯 **Example Policies**: Load pre-built examples to get started quickly

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nl-to-smt-tool.git
   cd nl-to-smt-tool
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the web server**:
   ```bash
   python app.py
   ```

4. **Open in browser**:
   Navigate to `http://localhost:5000`

## Usage

### 1. Configure LLM

Enter your API credentials:
- **Base URL**: e.g., `https://api.deepseek.com`
- **API Key**: Your DeepSeek API key (get one at https://platform.deepseek.com)

### 2. Input Natural Language Policy

Write or paste your temporal policy in plain language:

```
Medical prescription system policy:

1. Before prescribing medication, the doctor must verify patient allergies 
   and check insurance coverage.

2. High-risk medications require both supervisor approval AND pharmacy verification.

3. If a drug interaction is detected, the system enters alert mode.

4. In alert mode, the prescription cannot be finalized until either:
   - A physician override is issued, OR
   - The medication is changed to resolve the interaction

5. Alert mode persists until the interaction is resolved.

6. When a physician override is issued, emergency protocol must be activated 
   in the next step.

7. Emergency protocol blocks automated refills.
```

### 3. Generate and Edit

Click **Generate JSON** to get:
- **Blueprint JSON**: Events, states, and time bound
- **Encoder Plan JSON**: Temporal and business constraints

Edit the generated JSON if needed (e.g., fix event names, adjust constraints).

### 4. Validate

Click **Validate JSON** to:
- Check JSON syntax
- Build Z3 solver
- Verify constraint satisfiability

### 5. Test Scenarios (Optional)

Click **Test Scenario** to test specific execution traces:

```json
{
  "prefix_length": 2,
  "events": [
    {"time": 0, "event": "drug_interaction_detected"},
    {"time": 1, "event": "prescription_finalized"}
  ],
  "states": [],
  "check": {"require_eventually": "physician_override_issued"}
}
```

### 6. Download

Click **Download JSON** to save your policy for later use.

## Constraint Templates

The system supports 8 types of temporal constraint templates:

1. **always_previously_requires**: Event A must occur before event B
2. **state_persistence_until**: State persists from start_event to end_event
3. **always_prevents_while_state**: State blocks event
4. **always_within_requires**: Event requires another event within N steps
5. **always_next_requires**: Event triggers state in next step
6. **event_requires_state**: Event can only occur when state holds
7. **state_implication**: One state implies another
8. **state_blocks_event**: State prevents event

See the built-in Template Reference in the UI for detailed documentation.

## Project Structure

```
nl-to-smt-tool/
├── app.py                      # Flask web server
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── index.html             # Web UI
├── temporal_engine/
│   ├── __init__.py
│   ├── nl_generator.py        # LLM-based JSON generation
│   ├── temporal_encoder.py    # Z3 constraint encoder
│   └── temporal_solver.py     # Feasibility checker
└── examples/
    └── *.json                 # Example policies
```

## How It Works

```
Natural Language Policy
        ↓ (LLM generates ~85% correct)
Blueprint JSON + Encoder Plan JSON
        ↓ (Human reviews and edits)
Corrected JSON
        ↓ (Automatic encoding)
Z3 SMT Constraints
        ↓ (Solver checks)
SAT/UNSAT Result
```

## LLM Generation Accuracy

Based on our experiments:
- **JSON Structure**: 100% valid
- **Event/State Identification**: ~95% correct
- **Template Selection**: ~85% correct
- **Overall Logic**: ~85% correct (may need minor human review)

**Recommendation**: Use LLM output as a draft, then manually review for logic correctness.

## Troubleshooting

### Port already in use
If port 5000 is occupied, edit `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Change to 5001 or any available port
```

### API Key errors
- Verify your API key is correct
- Check that base URL matches your LLM provider
- Ensure you have API credits/quota remaining

### JSON validation fails
- Check for syntax errors (missing commas, brackets)
- Ensure event/state names match between Blueprint and Encoder Plan
- Verify constraint parameters match template requirements

## Examples

Example policies are included in the `examples/` directory:
- Email Runtime Safety
- Medical Prescription System
- API Authorization (coming soon)

Load them via the **Load Example** button in the UI.

## Contact

For questions or issues, please open a GitHub issue.
