#!/usr/bin/env python3
"""
Manual Test MT1.4: DataPreparationModule Fixed

Demonstrates the fixed DataPreparationModule test with corrected import paths.
The issue was import path mismatch causing isinstance() failures in tests.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path with consistent import method
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from teams.data_acquisition.git_operations_module import GitOperationsModule
from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from teams.data_acquisition.data_preparation_module import DataPreparationModule
from shared.models.project_data_context import ProjectDataContext


def create_test_repository_advanced():
    """Create a more complex test repository with multiple languages."""
    temp_dir = tempfile.mkdtemp(prefix="mt1_4_test_")
    
    # Create Python application
    (Path(temp_dir) / "app.py").write_text("""
#!/usr/bin/env python3
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Python API!"})

if __name__ == "__main__":
    app.run(debug=True)
""")
    
    (Path(temp_dir) / "models.py").write_text("""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None
    
@dataclass
class Project:
    name: str
    description: str
    languages: List[str]
""")
    
    # Create JavaScript frontend
    (Path(temp_dir) / "frontend.js").write_text("""
// React component for user interface
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUsers();
    }, []);
    
    const fetchUsers = async () => {
        try {
            const response = await axios.get('/api/users');
            setUsers(response.data);
        } catch (error) {
            console.error('Error fetching users:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="dashboard">
            <h1>User Dashboard</h1>
            {loading ? <p>Loading...</p> : (
                <ul>
                    {users.map(user => (
                        <li key={user.id}>{user.name}</li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default UserDashboard;
""")
    
    # Create configuration files
    (Path(temp_dir) / "package.json").write_text("""
{
    "name": "test-fullstack-app",
    "version": "1.0.0",
    "description": "Test application for language detection",
    "main": "frontend.js",
    "dependencies": {
        "react": "^18.0.0",
        "axios": "^1.4.0",
        "flask": "^2.3.0"
    },
    "scripts": {
        "start": "react-scripts start",
        "build": "react-scripts build",
        "test": "react-scripts test"
    }
}
""")
    
    (Path(temp_dir) / "requirements.txt").write_text("""
Flask>=2.3.0
requests>=2.31.0
gunicorn>=21.0.0
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
""")
    
    # Create HTML template
    (Path(temp_dir) / "index.html").write_text("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Application</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="root">
        <header>
            <h1>Full Stack Test Application</h1>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#dashboard">Dashboard</a></li>
                    <li><a href="#about">About</a></li>
                </ul>
            </nav>
        </header>
        <main>
            <section id="content">
                <p>Welcome to our test application!</p>
            </section>
        </main>
    </div>
    <script src="frontend.js"></script>
</body>
</html>
""")
    
    # Create CSS styles
    (Path(temp_dir) / "styles.css").write_text("""
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
}

main {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.dashboard {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
""")
    
    # Create README
    (Path(temp_dir) / "README.md").write_text("""
# Test Full-Stack Application

This is a test application designed to test the DataPreparationModule language detection capabilities.

## Technologies Used

- **Backend**: Python with Flask framework
- **Frontend**: JavaScript with React
- **Styling**: CSS3
- **Documentation**: Markdown

## Features

- RESTful API endpoints
- Responsive web interface  
- User management system
- Modern JavaScript (ES6+)
- Python data models with type hints

## Setup

1. Install Python dependencies: `pip install -r requirements.txt`
2. Install Node.js dependencies: `npm install`
3. Run the application: `python app.py`

## Testing

The application includes comprehensive language detection testing for:
- Python application code
- JavaScript frontend code
- HTML templates
- CSS styling
- Configuration files
""")
    
    return temp_dir


def run_comprehensive_workflow():
    """Run a comprehensive DataPreparationModule workflow test."""
    print("🧪 Manual Test MT1.4: DataPreparationModule Comprehensive Test")
    print("=" * 70)
    
    # Create test repository
    print("1. Creating comprehensive test repository...")
    test_repo = create_test_repository_advanced()
    print(f"   Created test repo at: {test_repo}")
    print(f"   Repository contains: Python, JavaScript, HTML, CSS, Markdown")
    
    try:
        # Initialize modules
        print("\n2. Initializing data acquisition modules...")
        git_ops = GitOperationsModule()
        lang_id = LanguageIdentifierModule()
        data_prep = DataPreparationModule()
        print("   ✅ All modules initialized successfully")
        
        # Simulate Git operations result
        print("\n3. Simulating GitOperationsModule result...")
        git_result = {
            "path": test_repo,
            "repository_url": "https://github.com/test/fullstack-app.git",
            "stats": {
                "size_bytes": 15234,
                "total_files": 8,
                "clone_time_ms": 1250.5
            }
        }
        print(f"   Simulated Git result: {git_result['repository_url']}")
        
        # Run language identification
        print("\n4. Running language identification...")
        detected_languages = lang_id.identify_languages(test_repo)
        print(f"   Detected languages: {detected_languages}")
        
        # Get detailed language analysis
        detailed_analysis = lang_id.get_detailed_analysis(test_repo)
        lang_result = {
            "languages": detected_languages,
            "statistics": detailed_analysis
        }
        print(f"   Language statistics collected for {len(detected_languages)} languages")
        
        # Test Method 1: Direct context creation
        print("\n5. Testing direct ProjectDataContext creation...")
        context1 = data_prep.create_project_context(
            cloned_code_path=test_repo,
            detected_languages=detected_languages,
            repository_url=git_result["repository_url"],
            repository_stats=git_result["stats"],
            language_statistics=detailed_analysis
        )
        
        print(f"   ✅ Direct creation successful")
        print(f"     - Type: {type(context1).__name__}")
        print(f"     - isinstance check: {isinstance(context1, ProjectDataContext)}")
        print(f"     - Languages: {context1.detected_languages}")
        print(f"     - Primary language: {context1.primary_language}")
        print(f"     - Language count: {context1.language_count}")
        print(f"     - Has languages: {context1.has_languages}")
        
        # Test Method 2: Creation from module results
        print("\n6. Testing context creation from module results...")
        context2 = data_prep.create_context_from_modules(
            git_operations_result=git_result,
            language_identifier_result=lang_result
        )
        
        print(f"   ✅ Module-based creation successful")
        print(f"     - Type: {type(context2).__name__}")
        print(f"     - isinstance check: {isinstance(context2, ProjectDataContext)}")
        print(f"     - Repository URL: {context2.repository_url}")
        print(f"     - Languages: {context2.detected_languages}")
        
        # Test validation
        print("\n7. Testing context validation...")
        is_valid1 = data_prep.validate_context(context1)
        is_valid2 = data_prep.validate_context(context2)
        
        print(f"   Context 1 validation: {'✅ PASS' if is_valid1 else '❌ FAIL'}")
        print(f"   Context 2 validation: {'✅ PASS' if is_valid2 else '❌ FAIL'}")
        
        # Get module statistics
        print("\n8. Getting module statistics...")
        stats = data_prep.get_module_stats()
        print(f"   Module statistics:")
        print(f"     - Contexts created: {stats['contexts_created']}")
        print(f"     - Total preparation time: {stats['total_preparation_time_ms']:.2f}ms")
        print(f"     - Average preparation time: {stats['average_preparation_time_ms']:.2f}ms")
        
        # Show corrected validation commands
        print("\n" + "=" * 70)
        print("📋 CORRECTED VALIDATION COMMANDS for MT1.4:")
        print("=" * 70)
        print("# Fixed import paths resolve isinstance() failures")
        print()
        print("# 1. Check DataPreparationModule logs:")
        print("grep \"DataPreparationModule\" logs/repochat_debug_*.log")
        print()
        print("# 2. Check context creation success logs (CORRECTED):")
        print("grep \"Project data context created successfully\" logs/repochat_debug_*.log")
        print()
        print("# 3. Check create_project_context function calls:")
        print("grep \"create_project_context\" logs/repochat_debug_*.log")
        print()
        print("📊 Expected Results:")
        print("- DataPreparationModule initialization logs")
        print("- ProjectDataContext creation success logs")
        print("- Function entry/exit logs with performance metrics")
        print("- All isinstance() checks should now pass")
        
        print("\n✅ MT1.4 comprehensive test completed successfully!")
        print("🔧 Issue was import path mismatch - now fixed in test files")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test repository: {test_repo}")
        shutil.rmtree(test_repo)


def main():
    run_comprehensive_workflow()


if __name__ == "__main__":
    main() 