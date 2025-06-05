"""
Data Models for TEAM CKG Operations

Defines data structures for code parsing results, AST representations,
and Code Knowledge Graph entities.

Used by CodeParserCoordinatorModule and language-specific parsers
to standardize data exchange and CKG construction.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class CodeEntityType(str, Enum):
    """Types of code entities that can be extracted from source code"""
    FILE = "file"
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    METHOD = "method"
    CONSTRUCTOR = "constructor"
    FIELD = "field"
    VARIABLE = "variable"
    IMPORT = "import"
    PACKAGE = "package"
    MODULE = "module"


class VisibilityModifier(str, Enum):
    """Visibility modifiers for code entities"""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    PACKAGE = "package"  # package-private
    INTERNAL = "internal"  # Kotlin internal
    UNKNOWN = "unknown"


class CodeEntity(BaseModel):
    """
    Represents a single code entity (class, method, function, etc.)
    extracted from source code parsing.
    """
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    entity_type: CodeEntityType = Field(
        ...,
        description="Type of the code entity"
    )
    
    name: str = Field(
        ...,
        description="Name of the entity",
        min_length=1
    )
    
    qualified_name: Optional[str] = Field(
        None,
        description="Fully qualified name (e.g., com.example.Class.method)"
    )
    
    file_path: str = Field(
        ...,
        description="Relative path to the source file containing this entity"
    )
    
    start_line: Optional[int] = Field(
        None,
        description="Starting line number in the source file",
        ge=1
    )
    
    end_line: Optional[int] = Field(
        None,
        description="Ending line number in the source file",
        ge=1
    )
    
    visibility: VisibilityModifier = Field(
        default=VisibilityModifier.UNKNOWN,
        description="Visibility modifier of the entity"
    )
    
    parent_entity: Optional[str] = Field(
        None,
        description="Name of the parent entity (class for methods, package for classes)"
    )
    
    signature: Optional[str] = Field(
        None,
        description="Method/function signature including parameters"
    )
    
    return_type: Optional[str] = Field(
        None,
        description="Return type for methods and functions"
    )
    
    parameters: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of parameters with name and type"
    )
    
    modifiers: List[str] = Field(
        default_factory=list,
        description="Additional modifiers (static, final, abstract, etc.)"
    )
    
    annotations: List[str] = Field(
        default_factory=list,
        description="Annotations or decorators"
    )
    
    language: str = Field(
        ...,
        description="Programming language of this entity"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional language-specific metadata"
    )


class CallRelationship(BaseModel):
    """
    Represents a method/function call relationship between code entities.
    """
    
    caller: str = Field(
        ...,
        description="Qualified name of the calling entity"
    )
    
    callee: str = Field(
        ...,
        description="Qualified name of the called entity"
    )
    
    call_type: str = Field(
        default="direct",
        description="Type of call (direct, indirect, virtual, etc.)"
    )
    
    file_path: str = Field(
        ...,
        description="File where the call occurs"
    )
    
    line_number: Optional[int] = Field(
        None,
        description="Line number where the call occurs"
    )
    
    language: str = Field(
        ...,
        description="Programming language"
    )


class ParseResult(BaseModel):
    """
    Result from parsing a single source file.
    """
    
    file_path: str = Field(
        ...,
        description="Relative path to the parsed file"
    )
    
    language: str = Field(
        ...,
        description="Programming language of the file"
    )
    
    entities: List[CodeEntity] = Field(
        default_factory=list,
        description="Code entities found in the file"
    )
    
    relationships: List[CallRelationship] = Field(
        default_factory=list,
        description="Call relationships found in the file"
    )
    
    parse_duration_ms: Optional[float] = Field(
        None,
        description="Time taken to parse this file in milliseconds"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="Parsing errors encountered"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Parsing warnings"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parsing metadata"
    )


class LanguageParseResult(BaseModel):
    """
    Aggregated parsing results for a specific programming language.
    """
    
    language: str = Field(
        ...,
        description="Programming language"
    )
    
    files_parsed: List[ParseResult] = Field(
        default_factory=list,
        description="Results from individual file parsing"
    )
    
    total_entities: int = Field(
        default=0,
        description="Total number of entities found"
    )
    
    total_relationships: int = Field(
        default=0,
        description="Total number of relationships found"
    )
    
    parse_duration_ms: Optional[float] = Field(
        None,
        description="Total time for parsing all files of this language"
    )
    
    files_with_errors: int = Field(
        default=0,
        description="Number of files that had parsing errors"
    )
    
    parser_version: Optional[str] = Field(
        None,
        description="Version of the parser used"
    )


class CoordinatorParseResult(BaseModel):
    """
    Complete parsing results from CodeParserCoordinatorModule.
    Contains results from all supported languages.
    """
    
    project_path: str = Field(
        ...,
        description="Path to the project that was parsed"
    )
    
    languages_processed: List[str] = Field(
        default_factory=list,
        description="List of languages that were processed"
    )
    
    language_results: Dict[str, LanguageParseResult] = Field(
        default_factory=dict,
        description="Parsing results organized by language"
    )
    
    total_files_parsed: int = Field(
        default=0,
        description="Total number of files successfully parsed"
    )
    
    total_entities_found: int = Field(
        default=0,
        description="Total number of code entities found across all languages"
    )
    
    total_relationships_found: int = Field(
        default=0,
        description="Total number of call relationships found"
    )
    
    coordination_duration_ms: Optional[float] = Field(
        None,
        description="Total time for coordination and parsing"
    )
    
    parse_timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when parsing was completed"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="High-level coordination errors"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="High-level coordination warnings"
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of parsing"""
        if not self.language_results:
            return 0.0
        
        total_files = sum(len(result.files_parsed) for result in self.language_results.values())
        files_with_errors = sum(result.files_with_errors for result in self.language_results.values())
        
        if total_files == 0:
            return 0.0
        
        return max(0.0, (total_files - files_with_errors) / total_files)
    
    @property
    def languages_with_results(self) -> List[str]:
        """Get list of languages that have parsing results"""
        return [lang for lang, result in self.language_results.items() 
                if result.total_entities > 0 or result.total_relationships > 0]
    
    def get_entities_by_type(self, entity_type: CodeEntityType) -> List[CodeEntity]:
        """Get all entities of a specific type across all languages"""
        entities = []
        for lang_result in self.language_results.values():
            for file_result in lang_result.files_parsed:
                entities.extend([e for e in file_result.entities if e.entity_type == entity_type])
        return entities
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the parsing results"""
        return {
            "project_path": self.project_path,
            "languages_processed": self.languages_processed,
            "languages_with_results": self.languages_with_results,
            "total_files_parsed": self.total_files_parsed,
            "total_entities_found": self.total_entities_found,
            "total_relationships_found": self.total_relationships_found,
            "success_rate": self.success_rate,
            "coordination_duration_ms": self.coordination_duration_ms,
            "parse_timestamp": self.parse_timestamp.isoformat() if self.parse_timestamp else None
        } 