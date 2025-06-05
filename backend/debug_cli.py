#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from click.testing import CliRunner
from teams.interaction_tasking.cli_interface import cli

def debug_cli():
    runner = CliRunner()
    
    print("=== Testing CLI ===")
    
    # Test 1: Main help
    print("\n1. Main help:")
    result = runner.invoke(cli, ['--help'])
    print(f"Exit code: {result.exit_code}")
    print("Output preview:", result.output[:200] + "..." if len(result.output) > 200 else result.output)
    
    # Test 2: review-pr help
    print("\n2. review-pr help:")
    result = runner.invoke(cli, ['review-pr', '--help'])
    print(f"Exit code: {result.exit_code}")
    print("Output preview:", result.output[:200] + "..." if len(result.output) > 200 else result.output)
    
    # Test 3: review-pr without enough args
    print("\n3. review-pr without args:")
    result = runner.invoke(cli, ['review-pr'])
    print(f"Exit code: {result.exit_code}")
    print("Output preview:", result.output[:200] + "..." if len(result.output) > 200 else result.output)

if __name__ == '__main__':
    debug_cli() 