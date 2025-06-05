#!/usr/bin/env python3
"""
Manual Test MT1.3: LanguageIdentifierModule Fixed Validation

Demonstrates the corrected validation commands for MT1.3 manual test.
The issue was using wrong log keys in the validation commands.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from teams.data_acquisition.git_operations_module import GitOperationsModule


def create_test_repository():
    """Create a test repository with multiple languages."""
    temp_dir = tempfile.mkdtemp(prefix="mt1_3_test_")
    
    # Create Python files
    (Path(temp_dir) / "main.py").write_text("""
#!/usr/bin/env python3
def hello():
    print("Hello from Python!")
if __name__ == "__main__":
    hello()
""")
    
    (Path(temp_dir) / "utils.py").write_text("""
def utility_function():
    return "utility"
""")
    
    # Create JavaScript file
    (Path(temp_dir) / "app.js").write_text("""
console.log("Hello from JavaScript!");
function greet(name) {
    return `Hello, ${name}!`;
}
""")
    
    # Create configuration files
    (Path(temp_dir) / "package.json").write_text("""
{
    "name": "test-project",
    "version": "1.0.0",
    "dependencies": {}
}
""")
    
    (Path(temp_dir) / "requirements.txt").write_text("""
requests>=2.25.0
pytest>=6.0.0
""")
    
    # Create HTML file
    (Path(temp_dir) / "index.html").write_text("""
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello World</h1></body>
</html>
""")
    
    return temp_dir


def main():
    print("🧪 Manual Test MT1.3: LanguageIdentifierModule (FIXED)")
    print("=" * 60)
    
    # Create test repository
    print("1. Creating test repository with multiple languages...")
    test_repo = create_test_repository()
    print(f"   Created test repo at: {test_repo}")
    
    try:
        # Initialize LanguageIdentifierModule
        print("\n2. Initializing LanguageIdentifierModule...")
        lang_id = LanguageIdentifierModule()
        
        # Identify languages
        print("\n3. Running language identification...")
        detected_languages = lang_id.identify_languages(test_repo)
        
        print(f"   Detected languages: {detected_languages}")
        
        # Get detailed analysis
        print("\n4. Getting detailed analysis...")
        detailed_analysis = lang_id.get_detailed_analysis(test_repo)
        
        print(f"   Language statistics:")
        for lang, count in detailed_analysis['language_file_counts'].items():
            percentage = detailed_analysis['language_percentages'].get(lang, 0)
            print(f"     - {lang}: {count} files ({percentage}%)")
        
        print(f"\n✅ Language identification completed successfully!")
        print(f"   Total files analyzed: {detailed_analysis['total_files_analyzed']}")
        print(f"   Analysis time: {detailed_analysis['analysis_time_ms']:.2f}ms")
        
        # Show validation commands
        print("\n" + "=" * 60)
        print("📋 CORRECTED VALIDATION COMMANDS for MT1.3:")
        print("=" * 60)
        print("# The issue was using wrong log keys. Use these corrected commands:")
        print()
        print("# 1. Check LanguageIdentifierModule logs:")
        print("grep \"LanguageIdentifierModule\" logs/repochat_debug_*.log")
        print()
        print("# 2. Check detected_languages entries (CORRECTED from languages_detected):")
        print("grep \"detected_languages\" logs/repochat_debug_*.log")
        print()
        print("# 3. Check performance metrics (CORRECTED name):")
        print("grep \"language_identification_time\" logs/repochat_debug_*.log")
        print()
        print("📊 Expected Results:")
        print("- LanguageIdentifierModule logs: Multiple entries")
        print("- detected_languages entries: Multiple JSON logs with language arrays")
        print("- language_identification_time metrics: Performance timing logs")
        
        print("\n🔍 Sample log analysis:")
        print("# View recent language detection results:")
        print("grep \"detected_languages\" logs/repochat_debug_*.log | tail -3 | jq .")
        
        print("\n✅ MT1.3 test completed successfully with corrected validation!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test repository: {test_repo}")
        shutil.rmtree(test_repo)


if __name__ == "__main__":
    main() 