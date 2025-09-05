
import os, runpy

def main():
    os.environ.setdefault("AUTOACCEL_OUTPUT_BASE", os.path.join(os.path.expanduser("~"), ".autoaccel", "output"))
    runpy.run_module("automationaccelerator.housekeeping_cli", run_name="__main__")

if __name__ == "__main__":
    main()
