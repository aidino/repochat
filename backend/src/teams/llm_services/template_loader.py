"""
Template Loader Module for Task 3.4

Loads prompt templates from markdown files with YAML frontmatter.
Provides version control, validation, and management for external template files.
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from .models import PromptTemplate

logger = logging.getLogger(__name__)

@dataclass
class TemplateLoadError:
    """Error information for template loading."""
    file_path: str
    error_type: str
    message: str
    line_number: Optional[int] = None

@dataclass 
class TemplateLoadResult:
    """Result of template loading operation."""
    success: bool
    templates_loaded: List[PromptTemplate] = None
    errors: List[TemplateLoadError] = None
    total_files: int = 0
    successful_files: int = 0

class TemplateLoader:
    """
    Loads prompt templates from markdown files with YAML frontmatter.
    
    Expected markdown format:
    ---
    template_id: example_template
    name: Example Template
    description: Template description
    version: "1.0"
    required_variables:
      - var1
      - var2
    optional_variables:
      - var3
    default_values:
      var3: default_value
    tags:
      - tag1
      - tag2
    ---
    
    # Template content here
    This is the template with {var1} and {var2} placeholders.
    """
    
    def __init__(self, templates_directory: Optional[str] = None):
        """
        Initialize template loader.
        
        Args:
            templates_directory: Path to templates directory. If None, uses default.
        """
        if templates_directory is None:
            # Default to prompt_templates directory relative to this file
            current_dir = Path(__file__).parent
            templates_directory = current_dir / "prompt_templates"
        
        self.templates_directory = Path(templates_directory)
        logger.info(f"TemplateLoader initialized with directory: {self.templates_directory}")
        
        # Validate directory exists
        if not self.templates_directory.exists():
            logger.warning(f"Templates directory does not exist: {self.templates_directory}")
        elif not self.templates_directory.is_dir():
            logger.error(f"Templates path is not a directory: {self.templates_directory}")
    
    def load_all_templates(self) -> TemplateLoadResult:
        """
        Load all templates from the templates directory.
        
        Returns:
            TemplateLoadResult: Result with loaded templates and any errors
        """
        logger.info(f"Loading all templates from: {self.templates_directory}")
        
        templates = []
        errors = []
        total_files = 0
        successful_files = 0
        
        # Check if directory exists
        if not self.templates_directory.exists():
            error = TemplateLoadError(
                file_path=str(self.templates_directory),
                error_type="DIRECTORY_NOT_FOUND",
                message=f"Templates directory not found: {self.templates_directory}"
            )
            return TemplateLoadResult(
                success=False,
                templates_loaded=[],
                errors=[error],
                total_files=0,
                successful_files=0
            )
        
        # Find all .md files
        md_files = list(self.templates_directory.glob("*.md"))
        total_files = len(md_files)
        
        logger.debug(f"Found {total_files} markdown files")
        
        for md_file in md_files:
            try:
                template = self.load_template_from_file(md_file)
                if template:
                    templates.append(template)
                    successful_files += 1
                    logger.debug(f"Successfully loaded template: {template.template_id}")
                else:
                    errors.append(TemplateLoadError(
                        file_path=str(md_file),
                        error_type="LOAD_FAILED", 
                        message="Template loading returned None"
                    ))
            except Exception as e:
                error = TemplateLoadError(
                    file_path=str(md_file),
                    error_type="PARSING_ERROR",
                    message=str(e)
                )
                errors.append(error)
                logger.error(f"Error loading template from {md_file}: {str(e)}")
        
        success = len(errors) == 0
        
        result = TemplateLoadResult(
            success=success,
            templates_loaded=templates,
            errors=errors,
            total_files=total_files,
            successful_files=successful_files
        )
        
        logger.info(f"Template loading completed: {successful_files}/{total_files} successful")
        return result
    
    def load_template_from_file(self, file_path: Path) -> Optional[PromptTemplate]:
        """
        Load a single template from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            PromptTemplate or None if loading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            frontmatter, template_content = self._parse_markdown_with_frontmatter(content)
            
            # Validate required fields
            required_fields = ['template_id', 'name', 'description']
            for field in required_fields:
                if field not in frontmatter:
                    raise ValueError(f"Missing required field: {field}")
            
            # Extract variables with defaults
            template_id = frontmatter['template_id']
            name = frontmatter['name']
            description = frontmatter['description']
            version = frontmatter.get('version', '1.0')
            category = frontmatter.get('category', 'general')
            required_variables = frontmatter.get('required_variables', [])
            optional_variables = frontmatter.get('optional_variables', [])
            default_values = frontmatter.get('default_values', {})
            tags = frontmatter.get('tags', [])
            
            # Create PromptTemplate
            template = PromptTemplate(
                template_id=template_id,
                name=name,
                description=description,
                template_text=template_content.strip(),
                required_variables=required_variables,
                optional_variables=optional_variables,
                default_values=default_values,
                category=category,
                tags=tags,
                version=version,
                created_at=datetime.now()
            )
            
            # Validate template
            self._validate_template(template)
            
            return template
            
        except Exception as e:
            logger.error(f"Error loading template from {file_path}: {str(e)}")
            raise
    
    def _parse_markdown_with_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        Parse markdown content with YAML frontmatter.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (frontmatter_dict, template_content)
        """
        lines = content.split('\n')
        
        # Check if starts with frontmatter delimiter
        if not lines[0].strip() == '---':
            raise ValueError("File must start with YAML frontmatter (---)")
        
        # Find end of frontmatter
        frontmatter_end = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end is None:
            raise ValueError("Frontmatter not properly closed with ---")
        
        # Extract frontmatter and content
        frontmatter_lines = lines[1:frontmatter_end]
        content_lines = lines[frontmatter_end + 1:]
        
        # Parse YAML frontmatter
        frontmatter_yaml = '\n'.join(frontmatter_lines)
        try:
            frontmatter = yaml.safe_load(frontmatter_yaml) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {str(e)}")
        
        # Join content
        template_content = '\n'.join(content_lines)
        
        return frontmatter, template_content
    
    def _validate_template(self, template: PromptTemplate) -> None:
        """
        Validate a loaded template.
        
        Args:
            template: Template to validate
            
        Raises:
            ValueError: If template is invalid
        """
        # Check for placeholder consistency
        template_content = template.template_text
        
        # Find all placeholders in template
        import re
        placeholders = re.findall(r'\{(\w+)\}', template_content)
        unique_placeholders = set(placeholders)
        
        # Check all required variables are in placeholders
        for var in template.required_variables:
            if var not in unique_placeholders:
                logger.warning(f"Required variable '{var}' not found in template content for {template.template_id}")
        
        # Check all placeholders are either required or optional
        all_variables = set(template.required_variables + template.optional_variables)
        undefined_placeholders = unique_placeholders - all_variables
        if undefined_placeholders:
            logger.warning(f"Undefined placeholders in template {template.template_id}: {undefined_placeholders}")
    
    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about the template loader and available templates.
        
        Returns:
            Dict with loader information
        """
        result = self.load_all_templates()
        
        return {
            "templates_directory": str(self.templates_directory),
            "directory_exists": self.templates_directory.exists(),
            "total_templates": len(result.templates_loaded) if result.templates_loaded else 0,
            "load_errors": len(result.errors) if result.errors else 0,
            "template_ids": [t.template_id for t in result.templates_loaded] if result.templates_loaded else [],
            "last_scan": datetime.now().isoformat()
        }
    
    def reload_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Reload a specific template by ID.
        
        Args:
            template_id: ID of template to reload
            
        Returns:
            Reloaded template or None if not found
        """
        template_file = self.templates_directory / f"{template_id}.md"
        
        if not template_file.exists():
            logger.error(f"Template file not found: {template_file}")
            return None
        
        try:
            return self.load_template_from_file(template_file)
        except Exception as e:
            logger.error(f"Error reloading template {template_id}: {str(e)}")
            return None
    
    def list_template_files(self) -> List[str]:
        """
        List all markdown template files in the directory.
        
        Returns:
            List of template file names
        """
        if not self.templates_directory.exists():
            return []
        
        md_files = list(self.templates_directory.glob("*.md"))
        return [f.name for f in md_files]


# Convenience functions
def create_template_loader(templates_directory: Optional[str] = None) -> TemplateLoader:
    """
    Create a template loader instance.
    
    Args:
        templates_directory: Optional custom templates directory
        
    Returns:
        TemplateLoader instance
    """
    return TemplateLoader(templates_directory)

def load_templates_from_directory(templates_directory: Optional[str] = None) -> TemplateLoadResult:
    """
    Load all templates from a directory.
    
    Args:
        templates_directory: Optional custom templates directory
        
    Returns:
        TemplateLoadResult with loaded templates
    """
    loader = create_template_loader(templates_directory)
    return loader.load_all_templates() 