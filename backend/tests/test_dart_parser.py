"""
Unit tests for the Dart Parser in TEAM CKG Operations.

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

from src.teams.ckg_operations.dart_parser import DartParser
from src.teams.ckg_operations.models import ParseResult, CodeEntity, CallRelationship


class TestDartParser(unittest.TestCase):
    """Test cases for DartParser class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = DartParser()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parser_initialization(self):
        """Test that DartParser initializes correctly."""
        self.assertEqual(self.parser.language, "dart")
        self.assertEqual(self.parser.supported_extensions, [".dart"])
        self.assertEqual(self.parser.get_parser_version(), "1.0.0-regex")
        
        # Check statistics initialization
        stats = self.parser.get_stats()
        self.assertEqual(stats['files_processed'], 0)
        self.assertEqual(stats['files_successful'], 0)
        self.assertEqual(stats['files_with_errors'], 0)
        
    def test_can_parse_file_extensions(self):
        """Test file extension validation."""
        self.assertTrue(self.parser.can_parse_file("test.dart"))
        self.assertTrue(self.parser.can_parse_file("/path/to/File.dart"))
        self.assertTrue(self.parser.can_parse_file("main.dart"))
        
        self.assertFalse(self.parser.can_parse_file("test.java"))
        self.assertFalse(self.parser.can_parse_file("test.py"))
        self.assertFalse(self.parser.can_parse_file("test.kt"))
        self.assertFalse(self.parser.can_parse_file(""))
        self.assertFalse(self.parser.can_parse_file(None))
    
    def test_parse_simple_dart_functions(self):
        """Test parsing simple Dart functions and their relationships."""
        dart_code = '''
library example.test;

String helloWorld() {
  return "Hello, World!";
}

void anotherFunction() {
  helloWorld();
  print("Another function");
}

void main() {
  anotherFunction();
}
'''
        
        # Create temporary Dart file
        dart_file = os.path.join(self.temp_dir, "test.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        # Parse the file
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        # Verify parsing results
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(result.language, "dart")
        self.assertEqual(result.metadata.get('module_name'), "example.test")
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
        
    def test_parse_dart_class_with_methods(self):
        """Test parsing Dart class with methods and properties."""
        dart_code = '''
library example.models;

class User {
  int _id = 0;
  String name = "";
  
  int getId() {
    return _id;
  }
  
  void setName(String newName) {
    name = newName;
  }
  
  void displayInfo() {
    print("User: ${getName()}");
  }
  
  String _getName() {
    return name;
  }
}
'''
        
        # Create temporary Dart file
        dart_file = os.path.join(self.temp_dir, "user.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        # Parse the file
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
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
        self.assertEqual(user_class.qualified_name, "example.models.User")
        
        # Find method entities
        method_entities = [e for e in entities if e.entity_type == "method"]
        self.assertGreaterEqual(len(method_entities), 4)  # getId, setName, displayInfo, _getName
        
        method_names = [e.name for e in method_entities]
        self.assertIn("getId", method_names)
        self.assertIn("setName", method_names)
        self.assertIn("displayInfo", method_names)
        self.assertIn("_getName", method_names)
        
        # Check method visibility (Dart uses _ prefix for private)
        get_name_method = next((e for e in method_entities if e.name == "_getName"), None)
        self.assertIsNotNone(get_name_method)
        self.assertEqual(get_name_method.visibility, "private")
        
        # Check field entities (properties in class)
        field_entities = [e for e in entities if e.entity_type == "field"]
        self.assertGreaterEqual(len(field_entities), 2)  # _id, name
        
        property_names = [e.name for e in field_entities]
        self.assertIn("_id", property_names)
        self.assertIn("name", property_names)
        
        # Check property visibility
        id_property = next((e for e in field_entities if e.name == "_id"), None)
        self.assertIsNotNone(id_property)
        self.assertEqual(id_property.visibility, "private")
    
    def test_parse_dart_with_imports(self):
        """Test parsing Dart file with import statements."""
        dart_code = '''
import 'dart:io';
import 'package:flutter/material.dart';
import '../utils/helpers.dart';

void main() {
  print("Hello from main");
}
'''
        
        # Create temporary Dart file
        dart_file = os.path.join(self.temp_dir, "main.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        # Parse the file
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        # Verify parsing results
        self.assertEqual(len(result.errors), 0)
        
        # Check import entities
        import_entities = [e for e in result.entities if e.entity_type == "import"]
        self.assertGreaterEqual(len(import_entities), 3)
        
        import_names = [e.name for e in import_entities]
        self.assertIn("dart:io", import_names)
        self.assertIn("package:flutter/material.dart", import_names)
        self.assertIn("../utils/helpers.dart", import_names)
    
    def test_parse_file_not_found(self):
        """Test handling of non-existent files."""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.dart")
        result = self.parser.parse_file(non_existent_file, self.temp_dir)
        
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(len(result.relationships), 0)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("not found", result.errors[0].lower())
    
    def test_parse_empty_file(self):
        """Test parsing empty Dart file."""
        # Create empty Dart file
        dart_file = os.path.join(self.temp_dir, "empty.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Parse the file
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        # Should parse successfully with no entities
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(len(result.relationships), 0)
    
    def test_parse_syntax_error_handling(self):
        """Test handling of Dart files with syntax errors."""
        dart_code = '''
library example.broken;

class BrokenClass {
  void brokenFunction(
    // Missing closing parenthesis and brace
'''
        
        # Create Dart file with syntax errors
        dart_file = os.path.join(self.temp_dir, "broken.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        # Parse the file
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
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
    
    def test_module_name_extraction_from_library(self):
        """Test module name extraction from library declaration."""
        dart_code = '''
library example.utils;

void utilityFunction() {
  print("Utility");
}
'''
        
        dart_file = os.path.join(self.temp_dir, "utils.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        self.assertEqual(result.metadata.get('module_name'), "example.utils")
    
    def test_module_name_extraction_from_path(self):
        """Test module name extraction from file path when no library declaration."""
        dart_code = '''
void simpleFunction() {
  print("Simple");
}
'''
        
        # Create nested directory structure
        nested_dir = os.path.join(self.temp_dir, "lib", "src", "example")
        os.makedirs(nested_dir, exist_ok=True)
        dart_file = os.path.join(nested_dir, "simple.dart")
        
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        # Should derive module name from path structure
        self.assertEqual(result.metadata.get('module_name'), "example.simple")
    
    def test_parse_dart_enum(self):
        """Test parsing Dart enum declarations."""
        dart_code = '''
enum Color {
  red,
  green,
  blue
}

void main() {
  Color color = Color.red;
  print(color);
}
'''
        
        dart_file = os.path.join(self.temp_dir, "colors.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        # Check enum entity (mapped to class)
        enum_entities = [e for e in result.entities if e.entity_type == "class" and e.name == "Color"]
        self.assertGreaterEqual(len(enum_entities), 1)
        
        color_enum = next((e for e in enum_entities if e.name == "Color"), None)
        self.assertIsNotNone(color_enum)
    
    def test_parse_dart_mixin(self):
        """Test parsing Dart mixin declarations."""
        dart_code = '''
mixin Flyable {
  void fly() {
    print("Flying");
  }
}

class Bird with Flyable {
  void chirp() {
    print("Chirping");
  }
}
'''
        
        dart_file = os.path.join(self.temp_dir, "bird.dart")
        with open(dart_file, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        result = self.parser.parse_file(dart_file, self.temp_dir)
        
        # Check mixin entity (mapped to interface)
        mixin_entities = [e for e in result.entities if e.entity_type == "interface" and e.name == "Flyable"]
        self.assertGreaterEqual(len(mixin_entities), 1)
        
        flyable_mixin = next((e for e in mixin_entities if e.name == "Flyable"), None)
        self.assertIsNotNone(flyable_mixin)
        
        # Check class entity
        class_entities = [e for e in result.entities if e.entity_type == "class"]
        self.assertGreaterEqual(len(class_entities), 1)
        
        bird_class = next((e for e in class_entities if e.name == "Bird"), None)
        self.assertIsNotNone(bird_class)
    
    def test_parser_statistics_tracking(self):
        """Test that parser correctly tracks statistics."""
        # Create multiple test files
        for i in range(3):
            dart_code = f'''
library example.test{i};

void function{i}() {{
  print("Function {i}");
}}
'''
            dart_file = os.path.join(self.temp_dir, f"test{i}.dart")
            with open(dart_file, 'w', encoding='utf-8') as f:
                f.write(dart_code)
            
            # Parse each file
            result = self.parser.parse_file(dart_file, self.temp_dir)
            self.assertEqual(len(result.errors), 0)
        
        # Check statistics
        stats = self.parser.get_stats()
        self.assertEqual(stats['files_processed'], 3)
        self.assertEqual(stats['files_successful'], 3)
        self.assertEqual(stats['files_with_errors'], 0)
        self.assertGreater(stats['total_entities_found'], 0)


if __name__ == '__main__':
    unittest.main() 