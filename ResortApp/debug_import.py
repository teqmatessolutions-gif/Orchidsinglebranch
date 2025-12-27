import sys
import traceback

try:
    from app.api import inventory
    print("Import successful")
except Exception:
    traceback.print_exc()
