"""
Test suite for StaticAnalysisIntegratorModule

Tests static analysis integration functionality including linters,
formatters, and security analysis tools.

Created: 2025-06-06
Author: AI Agent
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.teams.code_analysis.static_analysis_integrator_module import (
    StaticAnalysisIntegratorModule,
    StaticAnalysisResult,
    AnalysisToolType,
    run_linter,
    check_formatting,
    analyze_security
)


@pytest.fixture
def integrator():
    """Create StaticAnalysisIntegratorModule instance for testing."""
    return StaticAnalysisIntegratorModule()


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return """
def hello_world(name):
    # This is a simple function
    print(f"Hello, {name}!")
    return True

def unused_function():
    pass

if __name__ == "__main__":
    hello_world("World")
"""


@pytest.fixture 
def sample_python_file(sample_python_code):
    """Create temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_python_code)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing."""
    return """
function helloWorld(name) {
    console.log(`Hello, ${name}!`);
    return true;
}

function unusedFunction() {
    // This function is never called
}

helloWorld("World");
"""


@pytest.fixture
def sample_javascript_file(sample_javascript_code):
    """Create temporary JavaScript file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(sample_javascript_code)
        f.flush()
        yield f.name
    os.unlink(f.name)


class TestStaticAnalysisIntegratorModule:
    """Test StaticAnalysisIntegratorModule initialization and basic functionality."""
    
    def test_initialization(self, integrator):
        """Test that StaticAnalysisIntegratorModule initializes correctly."""
        assert integrator is not None
        assert hasattr(integrator, 'tool_configs')
        assert hasattr(integrator, 'available_tools')
        assert 'python' in integrator.tool_configs
        assert 'javascript' in integrator.tool_configs
        assert 'java' in integrator.tool_configs
        
    def test_tool_configs_structure(self, integrator):
        """Test that tool configurations are properly structured."""
        python_config = integrator.tool_configs['python']
        
        assert 'linters' in python_config
        assert 'formatters' in python_config
        assert 'security' in python_config
        
        assert 'pylint' in python_config['linters']
        assert 'flake8' in python_config['linters']
        assert 'black' in python_config['formatters']
        assert 'bandit' in python_config['security']
        
    def test_get_available_tools(self, integrator):
        """Test getting available tools for a language."""
        available = integrator.get_available_tools('python')
        
        assert isinstance(available, dict)
        for tool_type in ['linters', 'formatters', 'security']:
            assert tool_type in available
            assert isinstance(available[tool_type], list)
            
    def test_get_available_tools_unsupported_language(self, integrator):
        """Test getting available tools for unsupported language."""
        available = integrator.get_available_tools('unsupported')
        assert available == {}
        
    def test_get_tool_status(self, integrator):
        """Test getting tool status."""
        status = integrator.get_tool_status()
        
        assert 'module_status' in status
        assert 'supported_languages' in status
        assert 'available_tools' in status
        assert 'tool_configs' in status
        
        assert status['module_status'] == 'active'
        assert isinstance(status['supported_languages'], list)
        assert isinstance(status['available_tools'], dict)


class TestLinterIntegration:
    """Test linter integration functionality."""
    
    @patch('subprocess.run')
    def test_run_pylint_success(self, mock_run, integrator, sample_python_file):
        """Test successful pylint execution."""
        # Mock successful pylint run
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"path": "test.py", "line": 1, "column": 0, "type": "convention", "message": "Missing module docstring", "message-id": "C0114"}]',
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['pylint'] = True
        
        result = integrator.run_linter('python', sample_python_file, 'pylint')
        
        assert isinstance(result, StaticAnalysisResult)
        assert result.tool_name == 'pylint'
        assert result.tool_type == AnalysisToolType.LINTER
        assert result.language == 'python'
        assert result.status == 'success'
        assert result.issues_found > 0
        
    @patch('subprocess.run') 
    def test_run_flake8_success(self, mock_run, integrator, sample_python_file):
        """Test successful flake8 execution."""
        # Mock successful flake8 run
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='test.py:1:1:E302:expected 2 blank lines, found 0',
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['flake8'] = True
        
        result = integrator.run_linter('python', sample_python_file, 'flake8')
        
        assert isinstance(result, StaticAnalysisResult)
        assert result.tool_name == 'flake8'
        assert result.status == 'success'
        assert result.issues_found > 0
        
    @patch('subprocess.run')
    def test_run_mypy_success(self, mock_run, integrator, sample_python_file):
        """Test successful mypy execution."""
        # Mock successful mypy run
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='test.py:1: error: Missing type annotation',
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['mypy'] = True
        
        result = integrator.run_linter('python', sample_python_file, 'mypy')
        
        assert isinstance(result, StaticAnalysisResult)
        assert result.tool_name == 'mypy'
        assert result.status == 'success'
        assert result.issues_found > 0
        
    @patch('subprocess.run')
    def test_run_eslint_success(self, mock_run, integrator, sample_javascript_file):
        """Test successful ESLint execution."""
        # Mock successful ESLint run
        mock_eslint_output = '''[
            {
                "filePath": "test.js",
                "messages": [
                    {
                        "line": 1,
                        "column": 1,
                        "severity": 2,
                        "message": "Unexpected var, use let or const instead.",
                        "ruleId": "no-var"
                    }
                ]
            }
        ]'''
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mock_eslint_output,
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['eslint'] = True
        
        result = integrator.run_linter('javascript', sample_javascript_file, 'eslint')
        
        assert isinstance(result, StaticAnalysisResult)
        assert result.tool_name == 'eslint'
        assert result.language == 'javascript'
        assert result.status == 'success'
        assert result.issues_found > 0
        
    def test_run_linter_unsupported_language(self, integrator):
        """Test linter with unsupported language."""
        result = integrator.run_linter('unsupported', 'dummy_file.txt')
        
        assert result.status == 'error'
        assert 'Unsupported language' in result.metadata['error']
        
    def test_run_linter_no_available_tools(self, integrator, sample_python_file):
        """Test linter when no tools are available."""
        # Mock no tools available
        integrator.available_tools = {}
        
        result = integrator.run_linter('python', sample_python_file)
        
        assert result.status == 'error'
        assert 'No available linters' in result.metadata['error']
        
    @patch('subprocess.run')
    def test_run_linter_timeout(self, mock_run, integrator, sample_python_file):
        """Test linter timeout handling."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(['pylint'], 60)
        
        # Mock tool availability
        integrator.available_tools['pylint'] = True
        
        result = integrator.run_linter('python', sample_python_file, 'pylint')
        
        assert result.status == 'error'
        assert 'timed out' in result.metadata['error']


class TestFormatterIntegration:
    """Test formatter integration functionality."""
    
    @patch('subprocess.run')
    def test_run_black_check_compliant(self, mock_run, integrator, sample_python_file):
        """Test black formatter check with compliant code."""
        # Mock compliant code (no changes needed)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['black'] = True
        
        result = integrator.run_formatter_check('python', sample_python_file)
        
        assert isinstance(result, StaticAnalysisResult)
        assert result.tool_name == 'black'
        assert result.tool_type == AnalysisToolType.FORMATTER
        assert result.status == 'success'
        assert result.issues_found == 0
        assert result.metadata['formatting_compliant'] == True
        
    @patch('subprocess.run')
    def test_run_black_check_non_compliant(self, mock_run, integrator, sample_python_file):
        """Test black formatter check with non-compliant code."""
        # Mock non-compliant code (changes needed)
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="--- test.py\n+++ test.py\n@@ -1,2 +1,3 @@\n def hello():\n-    pass\n+     pass",
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['black'] = True
        
        result = integrator.run_formatter_check('python', sample_python_file)
        
        assert result.tool_name == 'black'
        assert result.status == 'success'
        assert result.issues_found == 1
        assert result.metadata['formatting_compliant'] == False
        
    @patch('subprocess.run')
    def test_run_prettier_check_compliant(self, mock_run, integrator, sample_javascript_file):
        """Test prettier formatter check with compliant code."""
        # Mock compliant code
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['prettier'] = True
        
        result = integrator.run_formatter_check('javascript', sample_javascript_file)
        
        assert result.tool_name == 'prettier'
        assert result.language == 'javascript'
        assert result.status == 'success'
        assert result.issues_found == 0
        
    def test_run_formatter_check_unsupported_language(self, integrator):
        """Test formatter check with unsupported language."""
        result = integrator.run_formatter_check('unsupported', 'dummy_file.txt')
        
        assert result.status == 'error'
        assert 'No formatter configured' in result.metadata['error']


class TestSecurityAnalysis:
    """Test security analysis functionality."""
    
    @patch('subprocess.run')
    def test_run_bandit_success(self, mock_run, integrator, sample_python_file):
        """Test successful bandit security analysis."""
        # Mock bandit output
        mock_bandit_output = '''
        {
            "results": [
                {
                    "filename": "test.py",
                    "line_number": 5,
                    "issue_severity": "medium",
                    "issue_text": "Use of insecure MD5 hash function.",
                    "test_id": "B303",
                    "issue_confidence": "high",
                    "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b303_md5.html"
                }
            ]
        }
        '''
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mock_bandit_output,
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['bandit'] = True
        
        result = integrator.run_security_analysis('python', sample_python_file)
        
        assert isinstance(result, StaticAnalysisResult)
        assert result.tool_name == 'bandit'
        assert result.tool_type == AnalysisToolType.SECURITY
        assert result.language == 'python'
        assert result.status == 'success'
        assert result.issues_found > 0
        assert result.metadata['risk_level'] == 'medium'
        
    @patch('subprocess.run')
    def test_run_bandit_no_issues(self, mock_run, integrator, sample_python_file):
        """Test bandit with no security issues found."""
        # Mock clean bandit output
        mock_bandit_output = '{"results": []}'
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_bandit_output,
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['bandit'] = True
        
        result = integrator.run_security_analysis('python', sample_python_file)
        
        assert result.tool_name == 'bandit'
        assert result.status == 'success'
        assert result.issues_found == 0
        assert result.metadata['risk_level'] == 'low'
        
    def test_run_security_analysis_unsupported_language(self, integrator):
        """Test security analysis with unsupported language."""
        result = integrator.run_security_analysis('java', 'dummy_file.java')
        
        assert result.status == 'error'
        assert 'No security analysis configured' in result.metadata['error']


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('src.teams.code_analysis.static_analysis_integrator_module.StaticAnalysisIntegratorModule')
    def test_run_linter_convenience_function(self, mock_integrator_class):
        """Test run_linter convenience function."""
        # Setup mock
        mock_integrator = Mock()
        mock_result = StaticAnalysisResult(
            tool_name='pylint',
            tool_type=AnalysisToolType.LINTER,
            language='python',
            status='success',
            issues_found=0,
            execution_time_ms=100.0,
            raw_output='',
            structured_issues=[],
            metadata={}
        )
        mock_integrator.run_linter.return_value = mock_result
        mock_integrator_class.return_value = mock_integrator
        
        # Call convenience function
        result = run_linter('python', 'test.py', 'pylint')
        
        # Verify
        assert result == mock_result
        mock_integrator.run_linter.assert_called_once_with('python', 'test.py', 'pylint')
        
    @patch('src.teams.code_analysis.static_analysis_integrator_module.StaticAnalysisIntegratorModule')
    def test_check_formatting_convenience_function(self, mock_integrator_class):
        """Test check_formatting convenience function."""
        # Setup mock
        mock_integrator = Mock()
        mock_result = StaticAnalysisResult(
            tool_name='black',
            tool_type=AnalysisToolType.FORMATTER,
            language='python',
            status='success',
            issues_found=0,
            execution_time_ms=50.0,
            raw_output='',
            structured_issues=[],
            metadata={'formatting_compliant': True}
        )
        mock_integrator.run_formatter_check.return_value = mock_result
        mock_integrator_class.return_value = mock_integrator
        
        # Call convenience function
        result = check_formatting('python', 'test.py', 'black')
        
        # Verify
        assert result == mock_result
        mock_integrator.run_formatter_check.assert_called_once_with('python', 'test.py', 'black')
        
    @patch('src.teams.code_analysis.static_analysis_integrator_module.StaticAnalysisIntegratorModule')
    def test_analyze_security_convenience_function(self, mock_integrator_class):
        """Test analyze_security convenience function."""
        # Setup mock
        mock_integrator = Mock()
        mock_result = StaticAnalysisResult(
            tool_name='bandit',
            tool_type=AnalysisToolType.SECURITY,
            language='python',
            status='success',
            issues_found=0,
            execution_time_ms=200.0,
            raw_output='',
            structured_issues=[],
            metadata={'risk_level': 'low'}
        )
        mock_integrator.run_security_analysis.return_value = mock_result
        mock_integrator_class.return_value = mock_integrator
        
        # Call convenience function
        result = analyze_security('python', 'test.py')
        
        # Verify
        assert result == mock_result
        mock_integrator.run_security_analysis.assert_called_once_with('python', 'test.py')


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('subprocess.run')
    def test_json_parsing_error(self, mock_run, integrator, sample_python_file):
        """Test handling of JSON parsing errors."""
        # Mock invalid JSON output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='invalid json output',
            stderr=""
        )
        
        # Mock tool availability
        integrator.available_tools['pylint'] = True
        
        result = integrator.run_linter('python', sample_python_file, 'pylint')
        
        # Should handle gracefully
        assert result.status == 'success'
        assert len(result.structured_issues) > 0
        assert 'JSON parsing failed' in result.structured_issues[0]['message']
        
    @patch('subprocess.run')
    def test_subprocess_exception(self, mock_run, integrator, sample_python_file):
        """Test handling of subprocess exceptions."""
        # Mock subprocess exception
        mock_run.side_effect = Exception("Subprocess failed")
        
        # Mock tool availability
        integrator.available_tools['pylint'] = True
        
        result = integrator.run_linter('python', sample_python_file, 'pylint')
        
        assert result.status == 'error'
        assert 'Pylint execution failed' in result.metadata['error']


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 