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
- PresentationModule: Result formatting and display ✅ COMPLETED (Task 4.8)
- UserIntentParserAgent: Natural language understanding ✅ COMPLETED
- DialogManagerAgent: Conversation management ✅ COMPLETED
- ConfigurationManagementAgent: User settings management ✅ COMPLETED
- TeamInteractionOrchestrator: Original orchestrator ✅ COMPLETED
- EnhancedTeamInteractionOrchestrator: LangGraph & A2A SDK enhanced version ✅ NEW
"""

from .task_initiation_module import TaskInitiationModule
from .cli_interface import CLIInterface, cli
from .presentation_module import PresentationModule
from .user_intent_parser_agent import UserIntentParserAgent, UserIntent, IntentType
from .dialog_manager_agent import DialogManagerAgent, DialogContext, DialogResponse, DialogState
from .configuration_management_agent import ConfigurationManagementAgent
from .team_interaction_orchestrator import TeamInteractionOrchestrator
from .enhanced_orchestrator import EnhancedTeamInteractionOrchestrator

__all__ = [
    'TaskInitiationModule',
    'CLIInterface', 
    'cli',
    'PresentationModule',
    'UserIntentParserAgent',
    'UserIntent',
    'IntentType',
    'DialogManagerAgent',
    'DialogContext', 
    'DialogResponse',
    'DialogState',
    'ConfigurationManagementAgent',
    'TeamInteractionOrchestrator',
    'EnhancedTeamInteractionOrchestrator'  # Enhanced version with LangGraph & A2A SDK
]
