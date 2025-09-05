
# AutomationAccelerator (packaged)

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
