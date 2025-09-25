# regorg

RegimA's organizational development and zone concept refinement repository.

## Cycle Completion

The repository tracks cycle completion insights through two complementary configuration files:

### cycleCompletion.json
Contains basic cycle completion insights and progress tracking:
- **Zone Concept Application**: Refinement and deepening of zone-based organizational principles
- **Organizational Consciousness**: Evolution through systematic processing and awareness development  
- **Professional Guidance**: Enhancement of capabilities for providing expert guidance
- **Wisdom Integration**: Strengthening RegimA's expertise through integrated learning and experience

### regcyc.json
Contains comprehensive organizational consciousness and cycle tracking with structured insights:
- **Organizational Consciousness**: Current state and evolution level tracking
- **Zone Concept Framework**: Detailed anti-inflammatory, anti-oxidant, and rejuvenation protocol specifications
- **Professional Guidance**: Focus areas and actionable insights for practitioners
- **Environmental Scanning**: Analysis of emerging technologies and industry developments
- **Integration Strategy**: Immediate actions and long-term evolution planning

## Structure

- `cycleCompletion.json` - Basic cycle completion insights and progress tracking
- `regcyc.json` - Comprehensive organizational consciousness and zone concept implementation tracking
- `.github/workflows/regima-learning-cycle.yml` - GitHub Actions workflow for AI-powered analysis
- `scripts/regima_ai_processor.py` - Python script for generating AI responses from organizational data
- `outputs/` - Directory for generated AI analysis reports

## AI-Powered Learning Cycle Analysis

This repository includes automated AI analysis capabilities that process the organizational consciousness data to generate insights and recommendations.

### GitHub Actions Workflow

The `regima-learning-cycle.yml` workflow automatically:

- **Triggers**: Runs on pushes to main (when JSON files change), pull requests, weekly schedule, or manual dispatch
- **Processes**: Analyzes organizational consciousness data and Zone Concept framework
- **Generates**: AI-powered insights, recommendations, and strategic guidance
- **Outputs**: Creates detailed analysis reports and automatically opens GitHub issues with findings
- **Artifacts**: Stores generated reports for download and review

### Analysis Types

The workflow supports different analysis modes:

- **Full Analysis**: Comprehensive analysis of all organizational aspects
- **Zone Concept Only**: Focused analysis of the Zone Concept framework
- **Consciousness Only**: Analysis of organizational consciousness evolution
- **Guidance Only**: Professional guidance and actionable insights

### Manual Execution

Run the AI processor locally:

```bash
# Full analysis (default)
python scripts/regima_ai_processor.py

# Specific analysis type
ANALYSIS_TYPE=zone_concept_only python scripts/regima_ai_processor.py
```

### Generated Outputs

The AI analysis generates:

- Individual analysis reports (Markdown format)
- Comprehensive JSON data for programmatic access
- Summary insights for quick review
- Automated GitHub issues with key findings