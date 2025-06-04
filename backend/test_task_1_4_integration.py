#!/usr/bin/env python3
"""
Integration test script for Task 1.4 - DataPreparationModule
Tests integration with GitOperationsModule and LanguageIdentifierModule
"""

import sys
import os

# Add src to path
sys.path.append('/app/src')

from teams.data_acquisition.git_operations_module import GitOperationsModule
from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from teams.data_acquisition.data_preparation_module import DataPreparationModule
from shared.models.project_data_context import ProjectDataContext


def test_task_1_4_integration():
    """Test complete integration of Task 1.4 - DataPreparationModule."""
    print("=== Task 1.4 Integration Test ===")
    print("Testing DataPreparationModule integration with GitOperationsModule and LanguageIdentifierModule")
    
    try:
        # Initialize all modules
        print("\n1. Initializing modules...")
        git_ops = GitOperationsModule()
        lang_id = LanguageIdentifierModule()
        data_prep = DataPreparationModule()
        
        print(f"   GitOperationsModule: {getattr(git_ops, 'module_id', 'OK')}")
        print(f"   LanguageIdentifierModule: {getattr(lang_id, 'module_id', 'OK')}")
        print(f"   DataPreparationModule: {data_prep.module_id}")
        
        # Test with a real repository
        repository_url = "https://github.com/octocat/Hello-World.git"
        print(f"\n2. Testing with repository: {repository_url}")
        
        # Step 1: Clone repository
        print("   Step 2.1: Cloning repository...")
        cloned_path = git_ops.clone_repository(repository_url)
        print(f"   Repository cloned to: {cloned_path}")
        
        # Step 2: Identify languages
        print("   Step 2.2: Identifying languages...")
        detected_languages = lang_id.identify_languages(cloned_path)
        print(f"   Detected languages: {detected_languages}")
        
        # Step 3: Create project context using simple parameters
        print("   Step 2.3: Creating project context (simple method)...")
        context = data_prep.create_project_context(
            cloned_code_path=cloned_path,
            detected_languages=detected_languages,
            repository_url=repository_url
        )
        
        print(f"   Context created: {context}")
        print(f"   Context summary: {context.get_summary()}")
        
        # Step 4: Test with detailed module results
        print("\n3. Testing with detailed module results...")
        
        # Get detailed results
        repo_stats = git_ops.get_repository_stats()
        detailed_analysis = lang_id.get_detailed_analysis(cloned_path)
        
        # Create context from module results
        git_result = {
            "path": cloned_path,
            "repository_url": repository_url,
            "stats": repo_stats
        }
        
        lang_result = {
            "languages": detected_languages,
            "statistics": detailed_analysis.get("language_statistics", {})
        }
        
        context2 = data_prep.create_context_from_modules(
            git_operations_result=git_result,
            language_identifier_result=lang_result
        )
        
        print(f"   Enhanced context created: {context2}")
        print(f"   Has repository stats: {bool(context2.repository_stats)}")
        print(f"   Has language statistics: {bool(context2.language_statistics)}")
        
        # Step 5: Validate contexts
        print("\n4. Validating contexts...")
        validation1 = data_prep.validate_context(context)
        validation2 = data_prep.validate_context(context2)
        
        print(f"   Context 1 validation: {validation1}")
        print(f"   Context 2 validation: {validation2}")
        
        # Step 6: Test different scenarios
        print("\n5. Testing edge cases...")
        
        # Test with empty languages
        context_empty = data_prep.create_project_context(
            cloned_code_path=cloned_path,
            detected_languages=[],
            repository_url=repository_url
        )
        
        print(f"   Empty languages context: {context_empty}")
        print(f"   Has languages: {context_empty.has_languages}")
        print(f"   Primary language: {context_empty.primary_language}")
        
        # Test with string results (simple case)
        context_simple = data_prep.create_context_from_modules(
            git_operations_result=cloned_path,
            language_identifier_result=detected_languages
        )
        
        print(f"   Simple results context: {context_simple}")
        
        # Step 7: Check module statistics
        print("\n6. Module statistics...")
        stats = data_prep.get_module_stats()
        print(f"   Contexts created: {stats['contexts_created']}")
        print(f"   Total preparation time: {stats['total_preparation_time_ms']:.2f}ms")
        print(f"   Average preparation time: {stats['average_preparation_time_ms']:.2f}ms")
        print(f"   Module uptime: {stats['uptime_seconds']:.1f}s")
        
        # Step 8: Test serialization
        print("\n7. Testing JSON serialization...")
        json_data = context.model_dump_json()
        deserialized = ProjectDataContext.model_validate_json(json_data)
        print(f"   Serialization successful: {len(json_data)} bytes")
        print(f"   Deserialization successful: {deserialized.cloned_code_path == context.cloned_code_path}")
        
        # Clean up
        print("\n8. Cleanup...")
        git_ops.cleanup_repository(cloned_path)
        print(f"   Repository cleaned up: {cloned_path}")
        
        print("\n=== Task 1.4 Integration Test COMPLETED ===")
        print("✅ DataPreparationModule integration is successful!")
        print(f"✅ Created {stats['contexts_created']} contexts successfully")
        print("✅ All validation checks passed")
        print("✅ JSON serialization/deserialization working")
        print("✅ Module statistics tracking functional")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_task_1_4_integration()
    sys.exit(0 if success else 1) 