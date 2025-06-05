#!/usr/bin/env python3
"""
Demo Script for CodeParserCoordinatorModule - Task 2.2 (F2.2)

Demonstrates the core functionality of the Code Parser Coordinator Module:
- Receiving ProjectDataContext with detected_languages and cloned_code_path
- Coordinating language-specific parsers based on detected_languages
- Aggregating results from all parsers

This script showcases the complete Task 2.2 workflow using mock parsers.

Usage:
    python demo_code_parser_coordinator.py
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from shared.models.project_data_context import ProjectDataContext
from teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule
from teams.ckg_operations.mock_parser import MockJavaParser, MockPythonParser, MockKotlinParser


def setup_demo_project(temp_dir: str) -> dict:
    """
    Setup a demo multi-language project for testing.
    
    Args:
        temp_dir: Temporary directory path
        
    Returns:
        Dictionary with project statistics
    """
    print("🔧 Setting up demo multi-language project...")
    
    # Create Java files
    java_dir = Path(temp_dir) / "src" / "main" / "java" / "com" / "example"
    java_dir.mkdir(parents=True, exist_ok=True)
    
    # Main Application class
    (java_dir / "Application.java").write_text("""
package com.example;

public class Application {
    private UserService userService;
    private Calculator calculator;
    
    public Application() {
        this.userService = new UserService();
        this.calculator = new Calculator();
    }
    
    public static void main(String[] args) {
        Application app = new Application();
        app.run();
    }
    
    public void run() {
        System.out.println("Starting application...");
        
        // Test calculator
        int result = calculator.add(10, 5);
        System.out.println("Calculation result: " + result);
        
        // Test user service
        userService.createUser("John Doe");
        userService.updateUser("john.doe", "Jane Doe");
    }
}
    """)
    
    # Calculator class
    (java_dir / "Calculator.java").write_text("""
package com.example;

public class Calculator {
    private static final String VERSION = "1.0";
    
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
    
    public double divide(double a, double b) {
        if (b == 0) {
            throw new IllegalArgumentException("Division by zero");
        }
        return a / b;
    }
    
    public String getVersion() {
        return VERSION;
    }
}
    """)
    
    # UserService class
    (java_dir / "UserService.java").write_text("""
package com.example;

import java.util.HashMap;
import java.util.Map;

public class UserService {
    private Map<String, String> users;
    
    public UserService() {
        this.users = new HashMap<>();
    }
    
    public void createUser(String name) {
        String username = generateUsername(name);
        users.put(username, name);
        System.out.println("Created user: " + name + " (" + username + ")");
    }
    
    public void updateUser(String username, String newName) {
        if (users.containsKey(username)) {
            users.put(username, newName);
            System.out.println("Updated user: " + username + " -> " + newName);
        }
    }
    
    public void deleteUser(String username) {
        users.remove(username);
        System.out.println("Deleted user: " + username);
    }
    
    private String generateUsername(String name) {
        return name.toLowerCase().replace(" ", ".");
    }
}
    """)
    
    # Create Python files
    python_dir = Path(temp_dir) / "src" / "python"
    python_dir.mkdir(parents=True, exist_ok=True)
    
    # Main Python script
    (python_dir / "main.py").write_text("""
#!/usr/bin/env python3
\"\"\"
Main application entry point
\"\"\"

from calculator import Calculator
from user_manager import UserManager
from config import Config

def main():
    \"\"\"Main application function\"\"\"
    print("Starting Python application...")
    
    # Initialize components
    config = Config()
    calculator = Calculator()
    user_manager = UserManager()
    
    # Test calculator
    result = calculator.add(15, 25)
    print(f"Python calculation result: {result}")
    
    # Test user manager
    user_manager.create_user("Alice Smith")
    user_manager.update_user("alice.smith", "Alice Johnson")
    
    print("Application completed successfully!")

if __name__ == "__main__":
    main()
    """)
    
    # Calculator module
    (python_dir / "calculator.py").write_text("""
\"\"\"
Calculator module with basic mathematical operations
\"\"\"

import logging
from typing import Union

logger = logging.getLogger(__name__)

class Calculator:
    \"\"\"A simple calculator class\"\"\"
    
    def __init__(self):
        self.version = "2.0"
        logger.info("Calculator initialized")
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        \"\"\"Add two numbers\"\"\"
        result = a + b
        logger.debug(f"Addition: {a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        \"\"\"Subtract two numbers\"\"\"
        result = a - b
        logger.debug(f"Subtraction: {a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        \"\"\"Multiply two numbers\"\"\"
        result = a * b
        logger.debug(f"Multiplication: {a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        \"\"\"Divide two numbers\"\"\"
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a / b
        logger.debug(f"Division: {a} / {b} = {result}")
        return result
    
    def get_version(self) -> str:
        \"\"\"Get calculator version\"\"\"
        return self.version

def quick_calculation(x: int, y: int) -> int:
    \"\"\"Quick calculation function\"\"\"
    calc = Calculator()
    return calc.add(x, y)
    """)
    
    # User Manager module
    (python_dir / "user_manager.py").write_text("""
\"\"\"
User management functionality
\"\"\"

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class UserManager:
    \"\"\"Manages user operations\"\"\"
    
    def __init__(self):
        self.users: Dict[str, str] = {}
        logger.info("UserManager initialized")
    
    def create_user(self, name: str) -> str:
        \"\"\"Create a new user\"\"\"
        username = self._generate_username(name)
        self.users[username] = name
        logger.info(f"Created user: {name} ({username})")
        return username
    
    def update_user(self, username: str, new_name: str) -> bool:
        \"\"\"Update user information\"\"\"
        if username in self.users:
            old_name = self.users[username]
            self.users[username] = new_name
            logger.info(f"Updated user {username}: {old_name} -> {new_name}")
            return True
        else:
            logger.warning(f"User not found: {username}")
            return False
    
    def delete_user(self, username: str) -> bool:
        \"\"\"Delete a user\"\"\"
        if username in self.users:
            name = self.users.pop(username)
            logger.info(f"Deleted user: {name} ({username})")
            return True
        else:
            logger.warning(f"User not found: {username}")
            return False
    
    def get_user(self, username: str) -> Optional[str]:
        \"\"\"Get user by username\"\"\"
        return self.users.get(username)
    
    def list_users(self) -> Dict[str, str]:
        \"\"\"List all users\"\"\"
        return self.users.copy()
    
    def _generate_username(self, name: str) -> str:
        \"\"\"Generate username from name\"\"\"
        return name.lower().replace(" ", ".")

def validate_username(username: str) -> bool:
    \"\"\"Validate username format\"\"\"
    return len(username) >= 3 and "." in username
    """)
    
    # Config module
    (python_dir / "config.py").write_text("""
\"\"\"
Configuration management
\"\"\"

import os
from typing import Dict, Any

class Config:
    \"\"\"Application configuration\"\"\"
    
    def __init__(self):
        self.settings: Dict[str, Any] = {
            'debug': True,
            'version': '1.0.0',
            'max_users': 1000,
            'log_level': 'INFO'
        }
        self._load_from_environment()
    
    def _load_from_environment(self):
        \"\"\"Load configuration from environment variables\"\"\"
        if os.getenv('DEBUG'):
            self.settings['debug'] = os.getenv('DEBUG').lower() == 'true'
        
        if os.getenv('MAX_USERS'):
            self.settings['max_users'] = int(os.getenv('MAX_USERS'))
    
    def get(self, key: str, default: Any = None) -> Any:
        \"\"\"Get configuration value\"\"\"
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        \"\"\"Set configuration value\"\"\"
        self.settings[key] = value
    """)
    
    # Create Kotlin files
    kotlin_dir = Path(temp_dir) / "src" / "kotlin"
    kotlin_dir.mkdir(parents=True, exist_ok=True)
    
    # Main Kotlin file
    (kotlin_dir / "Main.kt").write_text("""
package com.example.kotlin

fun main() {
    println("Starting Kotlin application...")
    
    val calculator = Calculator()
    val result = calculator.add(20, 30)
    println("Kotlin calculation result: $result")
    
    val userProcessor = UserProcessor()
    userProcessor.processUser("Bob Wilson")
    
    println("Kotlin application completed!")
}

class Calculator {
    fun add(a: Int, b: Int): Int {
        return a + b
    }
    
    fun multiply(a: Int, b: Int): Int {
        return a * b
    }
    
    fun divide(a: Double, b: Double): Double {
        require(b != 0.0) { "Division by zero" }
        return a / b
    }
}

class UserProcessor {
    private val users = mutableMapOf<String, String>()
    
    fun processUser(name: String) {
        val username = generateUsername(name)
        users[username] = name
        println("Processed user: $name ($username)")
    }
    
    private fun generateUsername(name: String): String {
        return name.lowercase().replace(" ", ".")
    }
}
    """)
    
    # Count files created
    java_files = list(java_dir.glob("*.java"))
    python_files = list(python_dir.glob("*.py"))
    kotlin_files = list(kotlin_dir.glob("*.kt"))
    
    stats = {
        'java_files': len(java_files),
        'python_files': len(python_files),
        'kotlin_files': len(kotlin_files),
        'total_files': len(java_files) + len(python_files) + len(kotlin_files)
    }
    
    print(f"✅ Created {stats['total_files']} files:")
    print(f"   - Java: {stats['java_files']} files")
    print(f"   - Python: {stats['python_files']} files")
    print(f"   - Kotlin: {stats['kotlin_files']} files")
    
    return stats


def main():
    """Main demo function."""
    print("🚀 CodeParserCoordinatorModule Demo - Task 2.2 (F2.2)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: Setup demo project
        project_stats = setup_demo_project(temp_dir)
        print()
        
        # Step 2: Create ProjectDataContext (simulating TEAM Data Acquisition output)
        print("📋 Creating ProjectDataContext (from TEAM Data Acquisition)...")
        project_context = ProjectDataContext(
            cloned_code_path=temp_dir,
            detected_languages=["java", "python", "kotlin"],
            repository_url="https://github.com/demo/multi-language-project.git",
            language_statistics={
                "java": {"files": project_stats['java_files'], "lines": 120},
                "python": {"files": project_stats['python_files'], "lines": 95},
                "kotlin": {"files": project_stats['kotlin_files'], "lines": 45}
            }
        )
        print(f"✅ ProjectDataContext created:")
        print(f"   - Path: {project_context.cloned_code_path}")
        print(f"   - Detected languages: {project_context.detected_languages}")
        print(f"   - Repository URL: {project_context.repository_url}")
        print()
        
        # Step 3: Initialize CodeParserCoordinatorModule
        print("🎛️  Initializing CodeParserCoordinatorModule...")
        coordinator = CodeParserCoordinatorModule()
        print(f"✅ Coordinator initialized: {coordinator}")
        print()
        
        # Step 4: Register language parsers
        print("🔧 Registering language parsers...")
        java_parser = MockJavaParser()
        python_parser = MockPythonParser()
        kotlin_parser = MockKotlinParser()
        
        coordinator.register_parser(java_parser)
        coordinator.register_parser(python_parser)
        coordinator.register_parser(kotlin_parser)
        
        print(f"✅ Registered parsers: {coordinator.get_registered_languages()}")
        print()
        
        # Step 5: Validate ProjectDataContext
        print("✔️  Validating ProjectDataContext...")
        validation_errors = coordinator.validate_project_data_context(project_context)
        if validation_errors:
            print(f"❌ Validation errors: {validation_errors}")
            return
        else:
            print("✅ ProjectDataContext validation passed")
        print()
        
        # Step 6: Execute coordination (main Task 2.2 function)
        print("🎯 Executing coordination parsing (Task 2.2 core functionality)...")
        print("   - Receiving ProjectDataContext with detected_languages and cloned_code_path")
        print("   - Calling appropriate parsers based on detected_languages")
        print("   - Aggregating results from all parsers")
        print()
        
        result = coordinator.coordinate_parsing(project_context)
        
        # Step 7: Display results
        print("📊 COORDINATION RESULTS")
        print("=" * 40)
        print(f"Project Path: {result.project_path}")
        print(f"Languages Processed: {result.languages_processed}")
        print(f"Total Files Parsed: {result.total_files_parsed}")
        print(f"Total Entities Found: {result.total_entities_found}")
        print(f"Total Relationships Found: {result.total_relationships_found}")
        print(f"Success Rate: {result.success_rate:.2%}")
        print(f"Coordination Duration: {result.coordination_duration_ms:.2f}ms")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        print()
        
        # Step 8: Show detailed language results
        print("📋 DETAILED LANGUAGE RESULTS")
        print("=" * 40)
        
        for language, lang_result in result.language_results.items():
            print(f"\n🔤 {language.upper()} PARSER RESULTS:")
            print(f"   Files Parsed: {len(lang_result.files_parsed)}")
            print(f"   Total Entities: {lang_result.total_entities}")
            print(f"   Total Relationships: {lang_result.total_relationships}")
            print(f"   Files with Errors: {lang_result.files_with_errors}")
            print(f"   Parse Duration: {lang_result.parse_duration_ms:.2f}ms")
            print(f"   Parser Version: {lang_result.parser_version}")
            
            # Show sample entities
            if lang_result.files_parsed:
                sample_file = lang_result.files_parsed[0]
                print(f"   Sample File: {sample_file.file_path}")
                if sample_file.entities:
                    print(f"   Sample Entities:")
                    for entity in sample_file.entities[:3]:  # Show first 3
                        print(f"     - {entity.entity_type.value}: {entity.name} (line {entity.start_line})")
        
        print()
        
        # Step 9: Show coordination statistics
        print("📈 COORDINATION STATISTICS")
        print("=" * 40)
        stats = coordinator.get_coordination_stats()
        print(f"Coordination Sessions: {stats['coordination_sessions']}")
        print(f"Total Languages Processed: {stats['total_languages_processed']}")
        print(f"Total Files Coordinated: {stats['total_files_coordinated']}")
        print(f"Total Entities Coordinated: {stats['total_entities_coordinated']}")
        print(f"Average Coordination Time: {stats['average_coordination_time_ms']:.2f}ms")
        print(f"Average Entities per Session: {stats['average_entities_per_session']:.1f}")
        print()
        
        # Step 10: Show parser information
        print("🔍 PARSER INFORMATION")
        print("=" * 40)
        for language in coordinator.get_registered_languages():
            parser_info = coordinator.get_parser_info(language)
            if parser_info:
                print(f"\n{language.upper()} Parser:")
                print(f"   Type: {parser_info['parser_type']}")
                print(f"   Version: {parser_info['parser_version']}")
                print(f"   Extensions: {parser_info['supported_extensions']}")
                stats = parser_info['parser_stats']
                print(f"   Files Processed: {stats['files_processed']}")
                print(f"   Success Rate: {stats['files_successful']}/{stats['files_processed']}")
        
        print()
        print("✅ TASK 2.2 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("The CodeParserCoordinatorModule has successfully:")
        print("✓ Received ProjectDataContext with detected_languages and cloned_code_path")
        print("✓ Called appropriate language parsers based on detected_languages")
        print("✓ Aggregated results from all parsers")
        print("✓ Provided comprehensive parsing statistics and coordination metrics")


if __name__ == "__main__":
    main() 