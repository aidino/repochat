#!/usr/bin/env python3
import pytest
import sys
import os

# Set environment
os.environ['TESTING_MODE'] = 'true'
os.environ['PYTHONPATH'] = './src'

# Run tests với optimized settings
if __name__ == "__main__":
    pytest.main([
        '-v',
        '--tb=short', 
        '--durations=10',
        '--maxfail=5',
        '--disable-warnings',
        '-x'  # Stop on first failure
    ] + sys.argv[1:])
