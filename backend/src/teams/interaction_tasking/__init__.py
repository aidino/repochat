"""
TEAM Interaction & Tasking

Responsible for:
- User interface and communication
- Natural language understanding and intent parsing
- Task initiation and configuration management
- User session management
- Result presentation and formatting

Main components implemented:
- TaskInitiationModule: Creates TaskDefinition from user input
- CLIInterface: Command line interface using Click

Components to be implemented in future phases:
- UserIntentParserAgent: Natural language understanding
- DialogManagerAgent: Conversation management
- ConfigurationManagementAgent: User settings management
- PresentationModule: Result formatting and display
"""

from .task_initiation_module import TaskInitiationModule
from .cli_interface import CLIInterface, cli

__all__ = [
    'TaskInitiationModule',
    'CLIInterface', 
    'cli'
]
