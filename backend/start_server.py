#!/usr/bin/env python3
"""
Direct server startup script
"""

import uvicorn
import os
import sys
from pathlib import Path
from config import config

# Get the directory where this script is located
backend_dir = Path(__file__).parent.absolute()
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.SERVER_HOST, port=config.SERVER_PORT, reload=True)