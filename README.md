# regorg

RégimA Zone organizational development repository — tracking the learning cycle, Zone Concept framework, and professional skincare tools.

## About RégimA Zone

RégimA is a professional skincare brand built around the **Zone Concept**: evidence-based protocols targeting the three core pillars of skin ageing and skin health:

- **Anti-Inflammatory** — reducing pro-inflammatory responses that cause cell damage, redness, and premature ageing
- **Anti-Oxidant** — protecting against free-radical damage and environmental oxidative stress
- **Rejuvenation** — restoring and renewing skin through clinically active ingredients and professional treatments

Practitioners use the Zone Concept to create personalized treatment protocols that address individual skin concerns while bringing the skin into its zone of optimal health.

## Repository Structure

### Core Data Files
- `cycleCompletion.json` — Organizational learning cycle completion insights: Zone integration status, professional development milestones, and evidence-based practice advancement
- `regcyc.json` — Comprehensive Zone Concept organizational tracking: current professional state, zone capabilities, guidance systems, and innovation scanning
- `man20.md` — RégimA Manual 2020 source guide: product references, Zone Concept documentation, and training content

### Scripts
- `scripts/regima_ai_processor.py` — AI-powered analysis of the organizational learning cycle data; generates insights and strategic recommendations from `regcyc.json` and `cycleCompletion.json`
- `scripts/ai_integration.py` — Multi-provider AI integration module (OpenAI, Anthropic, Google) with automatic failover
- `scripts/treatment_protocol_builder.py` — Practical tool for skincare practitioners to map client concerns to Zone Concept pillars and generate personalized treatment protocols with specific product recommendations
- `scripts/slack_directory.py` — Generates and queries the RegimA Zone Slack workspace directory

### Workspace
- `slack/` — RegimA Zone Slack workspace directory (member list, channels, interactive HTML view)

### Configuration
- `config/ai_models.json` — AI model configurations and analysis prompts for the learning cycle processor
- `config/phase3_capabilities.json` — Module capability configurations

### Automation & Testing
- `.github/workflows/regima-learning-cycle.yml` — GitHub Actions workflow: AI-powered analysis of organizational learning cycle data on push, pull request, weekly schedule, or manual dispatch
- `tests/` — pytest test suite

### Output
- `outputs/` — Generated AI analysis reports and summaries

## AI-Powered Learning Cycle Analysis

The `regima-learning-cycle.yml` workflow analyzes the Zone Concept organizational data and generates practitioner-relevant insights.

### GitHub Actions Workflow

- **Triggers**: Push to main (when JSON files change), pull requests, weekly schedule, or manual dispatch
- **Processes**: `regcyc.json` and `cycleCompletion.json` — Zone Concept framework data and cycle completion status
- **Generates**: AI-powered insights and strategic recommendations for professional development and Zone integration
- **Outputs**: Markdown and JSON analysis reports; opens GitHub issues with key findings
- **Artifacts**: Reports available for download from the Actions run

### Analysis Types

- **Full** — Comprehensive analysis of all Zone Concept and organizational learning aspects
- **Zone Concept Only** — Focused analysis of the three-pillar Zone Concept framework
- **Consciousness Only** — Organizational development and professional evolution analysis
- **Guidance Only** — Professional guidance and practitioner development recommendations

### Running the AI Processor Locally

```bash
# Full analysis (default)
python scripts/regima_ai_processor.py

# Specific analysis type
ANALYSIS_TYPE=zone_concept_only python scripts/regima_ai_processor.py
```

Requires one of: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_AI_API_KEY` set in the environment.

### Generated Outputs

- Individual analysis reports (Markdown) per analysis type
- JSON data file with all results for programmatic access
- Summary report with key findings
- GitHub issue (when run via Actions) with strategic recommendations

## Treatment Protocol Builder

A practical tool for practitioners building personalized client protocols:

```bash
python scripts/treatment_protocol_builder.py
```

The tool:
- Maps client skin concerns to the relevant Zone Concept pillars
- Recommends specific RégimA products matched to those concerns
- Generates AM/PM routines, weekly in-salon treatments, and professional recommendations
- Reflects the agent-arena-relation: Practitioner + RégimA products (agent) working with the client's skin and goals (arena) through the Zone Concept framework (relation)

## Slack Workspace Directory

```bash
# Generate/update the workspace summary
python scripts/slack_directory.py

# Browse the interactive directory
cd slack && python -m http.server 8080
# Open http://localhost:8080
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```