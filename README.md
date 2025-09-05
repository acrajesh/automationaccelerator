
# Automation Accelerators

CLI tools for mainframe modernization:
- Third-party utilities discovery (JCL/COBOL/ASM)
- Factory tool version report
- Conversion log scanners
- IMS Analyzer

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate
pip install -U pip build
pip install -e .
autoaccel
```

Outputs are written to `~/.autoaccel/output/<tool>` by default. Set `AUTOACCEL_OUTPUT_BASE` to override.

## Notes
This is a packaging of your original code into a `src/`-layout with an entrypoint.

## Why this matters for GenAI Solutions Architecture

These accelerators are the foundation for two OpenAI-ready prototypes:

- **Legacy Data Transformer (EBCDIC→ASCII)** – deterministic conversion with AI-assisted schema suggestions, evals, and guardrails.
- **Modernization Copilot** – analyzes JCL/COBOL/ASM, classifies utilities, builds dependency traces, and provides migration insights.

Together, they show how modernization expertise translates into practical GenAI adoption patterns: prototypes with **structured outputs, eval gates, cost/latency logging, and PII redaction** that scale from pilot to production.
