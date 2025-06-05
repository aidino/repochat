#!/usr/bin/env python3
"""
RepoChat CLI Entry Point

Main command line interface for RepoChat v1.0.
For Task 4.1, provides the 'scan-project' command.

Usage:
    python repochat_cli.py scan-project <repository_url>
    python repochat_cli.py scan-project https://github.com/spring-projects/spring-petclinic.git -v
    python repochat_cli.py status
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from teams.interaction_tasking import cli

if __name__ == '__main__':
    cli() 