import sys
import os

# Add the project root to sys.path
# This file is in /api/index.py, so root is ../
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.backend.main import app
