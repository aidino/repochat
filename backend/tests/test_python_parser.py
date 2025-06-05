"""
Tests for Python Language Parser

Comprehensive unit tests for the Python parser implementation,
covering AST parsing, entity extraction, and relationship detection.

Created for Task 2.4 (F2.4) requirements.
"""

import os
import pytest
import tempfile
from pathlib import Path
from typing import List, Dict, Any

# Import the Python parser
try:
    from src.teams.ckg_operations.python_parser import PythonParser, PythonASTVisitor
    from src.teams.ckg_operations.models import CodeEntity, CallRelationship, CodeEntityType, VisibilityModifier
    PYTHON_PARSER_AVAILABLE = True
except ImportError:
    PYTHON_PARSER_AVAILABLE = False


class TestPythonParser:
    """Test cases for PythonParser functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create a Python parser instance for testing."""
        if not PYTHON_PARSER_AVAILABLE:
            pytest.skip("Python parser not available")
        return PythonParser()
    
    @pytest.fixture
    def temp_python_file(self):
        """Create a temporary Python file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            yield f
        # Cleanup
        if os.path.exists(f.name):
            os.unlink(f.name)
    
    def test_parser_initialization(self, parser):
        """Test parser initialization."""
        assert parser.language == "python"
        assert ".py" in parser.supported_extensions
        assert parser._python_stats is not None
        assert isinstance(parser._python_stats, dict)
    
    def test_can_parse_file(self, parser):
        """Test file extension validation."""
        assert parser.can_parse_file("test.py")
        assert parser.can_parse_file("module.py")
        assert not parser.can_parse_file("test.java")
        assert not parser.can_parse_file("test.txt")
        assert not parser.can_parse_file("")
    
    def test_get_parser_version(self, parser):
        """Test parser version reporting."""
        version = parser.get_parser_version()
        assert version.startswith("ast-python-")
        assert len(version.split(".")) >= 3  # Major.minor.micro format
    
    def test_parse_simple_function(self, parser, temp_python_file):
        """Test parsing a simple function."""
        python_code = '''
def hello_world():
    """A simple greeting function."""
    print("Hello, World!")
    return "Hello"

def another_function():
    result = hello_world()
    return result
'''
        temp_python_file.write(python_code)
        temp_python_file.flush()
        
        project_root = str(Path(temp_python_file.name).parent)
        result = parser.parse_file(temp_python_file.name, project_root)
        
        assert result.language == "python"
        assert len(result.errors) == 0
        assert len(result.entities) >= 2  # At least 2 functions
        
        # Check function entities
        function_names = [entity.name for entity in result.entities if entity.entity_type == CodeEntityType.FUNCTION]
        assert "hello_world" in function_names
        assert "another_function" in function_names
        
        # Check relationships (another_function calls hello_world)
        assert len(result.relationships) >= 1
    
    def test_parse_class_with_methods(self, parser, temp_python_file):
        """Test parsing a class with methods."""
        python_code = '''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    def add(self, number):
        """Add a number to the current value."""
        self.value += number
        return self.value
    
    def multiply(self, number):
        """Multiply current value by a number."""
        result = self.add(0)  # Call to add method
        self.value = result * number
        return self.value
    
    def _private_method(self):
        """A private method."""
        return self.value * 2
'''
        temp_python_file.write(python_code)
        temp_python_file.flush()
        
        project_root = str(Path(temp_python_file.name).parent)
        result = parser.parse_file(temp_python_file.name, project_root)
        
        assert len(result.errors) == 0
        
        # Check class entity
        class_entities = [entity for entity in result.entities if entity.entity_type == CodeEntityType.CLASS]
        assert len(class_entities) == 1
        assert class_entities[0].name == "Calculator"
        
        # Check method entities
        method_entities = [entity for entity in result.entities if entity.entity_type == CodeEntityType.METHOD]
        method_names = [entity.name for entity in method_entities]
        assert "__init__" in method_names
        assert "add" in method_names
        assert "multiply" in method_names
        assert "_private_method" in method_names
        
        # Check visibility
        private_methods = [entity for entity in method_entities if entity.visibility == VisibilityModifier.PROTECTED]
        assert len(private_methods) >= 1  # _private_method should be protected
    
    def test_parse_syntax_error(self, parser, temp_python_file):
        """Test handling of Python syntax errors."""
        python_code = '''
def broken_function():
    if True
        return "missing colon"
    return "unreachable"
'''
        temp_python_file.write(python_code)
        temp_python_file.flush()
        
        project_root = str(Path(temp_python_file.name).parent)
        result = parser.parse_file(temp_python_file.name, project_root)
        
        assert len(result.errors) > 0
        assert any("syntax error" in error.lower() for error in result.errors)
        assert len(result.entities) == 0  # No entities should be extracted on syntax error
    
    def test_parse_empty_file(self, parser, temp_python_file):
        """Test parsing an empty file."""
        temp_python_file.write("")
        temp_python_file.flush()
        
        project_root = str(Path(temp_python_file.name).parent)
        result = parser.parse_file(temp_python_file.name, project_root)
        
        assert len(result.errors) == 0
        assert len(result.warnings) >= 1  # Should warn about empty file
        assert len(result.entities) == 0
    
    def test_module_name_extraction(self, parser):
        """Test module name extraction from file paths."""
        test_cases = [
            ("module.py", "module"),
            ("package/module.py", "package.module"),
            ("src/package/subpackage/module.py", "src.package.subpackage.module"),
            ("test_module.py", "test_module")
        ]
        
        for file_path, expected_module in test_cases:
            module_name = parser._extract_module_name(file_path)
            assert module_name == expected_module
    
    def test_parser_statistics(self, parser, temp_python_file):
        """Test that parser statistics are correctly tracked."""
        python_code = '''
class TestClass:
    def method1(self):
        return self.method2()
    
    async def method2(self):
        return "async result"

def regular_function():
    obj = TestClass()
    return obj.method1()

global_var = "test"
'''
        temp_python_file.write(python_code)
        temp_python_file.flush()
        
        project_root = str(Path(temp_python_file.name).parent)
        result = parser.parse_file(temp_python_file.name, project_root)
        
        stats = parser.get_python_stats()
        python_stats = stats['python_specific']
        
        assert python_stats['classes_found'] >= 1
        assert python_stats['functions_found'] >= 1
        assert python_stats['methods_found'] >= 2
        assert python_stats['async_functions_found'] >= 1
        assert python_stats['variables_found'] >= 1
