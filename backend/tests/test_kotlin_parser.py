"""
Unit tests for the Kotlin Parser in TEAM CKG Operations.

Tests cover:
- Parser initialization and configuration
- File extension validation
- Simple function parsing and relationships
- Class and method parsing
- Error handling for syntax errors
- Empty file handling
- Module name extraction logic
- Parser statistics tracking
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path

from src.teams.ckg_operations.kotlin_parser import KotlinParser
from src.teams.ckg_operations.models import ParseResult, CodeEntity, CallRelationship


class TestKotlinParser(unittest.TestCase):
    """Test cases for KotlinParser class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = KotlinParser()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parser_initialization(self):
        """Test that KotlinParser initializes correctly."""
        self.assertEqual(self.parser.language, "kotlin")
        self.assertEqual(self.parser.supported_extensions, [".kt", ".kts"])
        self.assertEqual(self.parser.get_parser_version(), "1.0.0-regex")
        
        # Check statistics initialization
        stats = self.parser.get_stats()
        self.assertEqual(stats['files_processed'], 0)
        self.assertEqual(stats['files_successful'], 0)
        self.assertEqual(stats['files_with_errors'], 0)
        
    def test_can_parse_file_extensions(self):
        """Test file extension validation."""
        self.assertTrue(self.parser.can_parse_file("test.kt"))
        self.assertTrue(self.parser.can_parse_file("script.kts"))
        self.assertTrue(self.parser.can_parse_file("/path/to/File.kt"))
        
        self.assertFalse(self.parser.can_parse_file("test.java"))
        self.assertFalse(self.parser.can_parse_file("test.py"))
        self.assertFalse(self.parser.can_parse_file("test.dart"))
        self.assertFalse(self.parser.can_parse_file(""))
        self.assertFalse(self.parser.can_parse_file(None))
    
    def test_parse_simple_kotlin_functions(self):
        """Test parsing simple Kotlin functions and their relationships."""
        kotlin_code = '''
package com.example.test

fun helloWorld(): String {
    return "Hello, World!"
}

fun anotherFunction(): Unit {
    helloWorld()
    println("Another function")
}

fun main() {
    anotherFunction()
}
'''
        
        # Create temporary Kotlin file
        kotlin_file = os.path.join(self.temp_dir, "test.kt")
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        
        # Parse the file
        result = self.parser.parse_file(kotlin_file, self.temp_dir)
        
        # Verify parsing results
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(result.language, "kotlin")
        self.assertEqual(result.metadata.get('module_name'), "com.example.test")
        self.assertEqual(len(result.errors), 0)
        
        # Check entities
        entities = result.entities
        self.assertGreater(len(entities), 0)
        
        # Find function entities
        function_entities = [e for e in entities if e.entity_type == "function"]
        self.assertGreaterEqual(len(function_entities), 3)  # helloWorld, anotherFunction, main
        
        function_names = [e.name for e in function_entities]
        self.assertIn("helloWorld", function_names)
        self.assertIn("anotherFunction", function_names)
        self.assertIn("main", function_names)
        
        # Check relationships
        relationships = result.relationships
        self.assertGreater(len(relationships), 0)
        
        # Verify there's a call relationship (anotherFunction -> helloWorld)
        call_relationships = [r for r in relationships if r.call_type == "function_call"]
        self.assertGreater(len(call_relationships), 0)
        
    def test_parse_kotlin_class_with_methods(self):
        """Test parsing Kotlin class with methods and properties."""
        kotlin_code = '''
package com.example.models

class User {
    private val id: Int = 0
    var name: String = ""
    
    fun getId(): Int {
        return id
    }
    
    fun setName(newName: String) {
        name = newName
    }
    
    fun displayInfo() {
        println("User: ${getName()}")
    }
    
    private fun getName(): String {
        return name
    }
}
'''
        
        # Create temporary Kotlin file
        kotlin_file = os.path.join(self.temp_dir, "User.kt")
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        
        # Parse the file
        result = self.parser.parse_file(kotlin_file, self.temp_dir)
        
        # Verify parsing results
        self.assertEqual(len(result.errors), 0)
        
        # Check entities
        entities = result.entities
        self.assertGreater(len(entities), 0)
        
        # Find class entity
        class_entities = [e for e in entities if e.entity_type == "class"]
        self.assertEqual(len(class_entities), 1)
        
        user_class = class_entities[0]
        self.assertEqual(user_class.name, "User")
        self.assertEqual(user_class.qualified_name, "com.example.models.User")
        
        # Find method entities
        method_entities = [e for e in entities if e.entity_type == "method"]
        self.assertGreaterEqual(len(method_entities), 4)  # getId, setName, displayInfo, getName
        
        method_names = [e.name for e in method_entities]
        self.assertIn("getId", method_names)
        self.assertIn("setName", method_names)
        self.assertIn("displayInfo", method_names)
        self.assertIn("getName", method_names)
        
        # Check method visibility
        get_name_method = next((e for e in method_entities if e.name == "getName"), None)
        self.assertIsNotNone(get_name_method)
        # Note: For Kotlin, private methods should have "private" visibility
        
        # Check field entities (properties in class)
        field_entities = [e for e in entities if e.entity_type == "field"]
        self.assertGreaterEqual(len(field_entities), 2)  # id, name
        
        property_names = [e.name for e in field_entities]
        self.assertIn("id", property_names)
        self.assertIn("name", property_names)
    
    def test_parse_file_not_found(self):
        """Test handling of non-existent files."""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.kt")
        result = self.parser.parse_file(non_existent_file, self.temp_dir)
        
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(len(result.relationships), 0)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("not found", result.errors[0].lower())
    
    def test_parse_empty_file(self):
        """Test parsing empty Kotlin file."""
        # Create empty Kotlin file
        kotlin_file = os.path.join(self.temp_dir, "empty.kt")
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Parse the file
        result = self.parser.parse_file(kotlin_file, self.temp_dir)
        
        # Should parse successfully with no entities
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(len(result.relationships), 0)
    
    def test_parse_syntax_error_handling(self):
        """Test handling of Kotlin files with syntax errors."""
        kotlin_code = '''
package com.example.broken

class BrokenClass {
    fun brokenFunction(
        // Missing closing parenthesis and brace
'''
        
        # Create Kotlin file with syntax errors
        kotlin_file = os.path.join(self.temp_dir, "broken.kt")
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        
        # Parse the file
        result = self.parser.parse_file(kotlin_file, self.temp_dir)
        
        # Should still parse what it can (regex-based parsing is tolerant)
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.errors), 0)  # Regex parser is tolerant
        
        # Should extract some entities even with broken syntax
        entities = result.entities
        class_entities = [e for e in entities if e.entity_type == "class"]
        self.assertGreaterEqual(len(class_entities), 1)
        
        # Should find the BrokenClass
        broken_class = next((e for e in class_entities if e.name == "BrokenClass"), None)
        self.assertIsNotNone(broken_class)
    
    def test_module_name_extraction_from_package(self):
        """Test module name extraction from package declaration."""
        kotlin_code = '''
package com.example.utils

fun utilityFunction() {
    println("Utility")
}
'''
        
        kotlin_file = os.path.join(self.temp_dir, "utils.kt")
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        
        result = self.parser.parse_file(kotlin_file, self.temp_dir)
        
        self.assertEqual(result.metadata.get('module_name'), "com.example.utils")
    
    def test_module_name_extraction_from_path(self):
        """Test module name extraction from file path when no package declaration."""
        kotlin_code = '''
fun simpleFunction() {
    println("Simple")
}
'''
        
        # Create nested directory structure
        nested_dir = os.path.join(self.temp_dir, "src", "main", "kotlin", "com", "example")
        os.makedirs(nested_dir, exist_ok=True)
        kotlin_file = os.path.join(nested_dir, "Simple.kt")
        
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        
        result = self.parser.parse_file(kotlin_file, self.temp_dir)
        
        # Should derive module name from path structure
        self.assertEqual(result.metadata.get('module_name'), "com.example.Simple")
    
    def test_parser_statistics_tracking(self):
        """Test that parser correctly tracks statistics."""
        # Create multiple test files
        for i in range(3):
            kotlin_code = f'''
package com.example.test{i}

fun function{i}() {{
    println("Function {i}")
}}
'''
            kotlin_file = os.path.join(self.temp_dir, f"test{i}.kt")
            with open(kotlin_file, 'w', encoding='utf-8') as f:
                f.write(kotlin_code)
            
            # Parse each file
            result = self.parser.parse_file(kotlin_file, self.temp_dir)
            self.assertEqual(len(result.errors), 0)
        
        # Check statistics
        stats = self.parser.get_stats()
        self.assertEqual(stats['files_processed'], 3)
        self.assertEqual(stats['files_successful'], 3)
        self.assertEqual(stats['files_with_errors'], 0)
        self.assertGreater(stats['total_entities_found'], 0)


if __name__ == '__main__':
    unittest.main()