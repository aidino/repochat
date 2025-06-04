"""
Test configuration for RepoChat backend tests.

Configures the test environment and import paths.
"""

import sys
import os

# Add the src directory to Python path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir) 