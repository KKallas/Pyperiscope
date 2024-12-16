# tests/conftest.py

import asyncio
import sys
import os
import pytest

# Set Jupyter platform dirs
os.environ["JUPYTER_PLATFORM_DIRS"] = "1"

# Configure event loop policy for Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())