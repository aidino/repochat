#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from performance_test_real_projects import *

def test_other_languages():
    tester = RealProjectPerformanceTester()
    
    # Test cases for other languages - smaller projects for faster testing
    test_cases = [
        ProjectTestCase(
            name="KMP Production Sample",
            url="https://github.com/Kotlin/kmp-production-sample.git",
            language="kotlin",
            description="Official Kotlin Multiplatform Mobile RSS reader production sample",
            expected_files_min=30
        ),
        ProjectTestCase(
            name="Flutter Simple Calculator",
            url="https://github.com/flutter/flutter.git",
            language="dart",
            description="Flutter simple calculator example (smaller subset)",
            expected_files_min=20
        ),
        ProjectTestCase(
            name="Requests",
            url="https://github.com/psf/requests.git", 
            language="python",
            description="HTTP library for Python",
            expected_files_min=20
        )
    ]
    
    print("🚀 Testing Other Languages (Kotlin KMP, Dart, Python)")
    print("📝 Using smaller projects for faster testing")
    print(f"📋 Total Projects: {len(test_cases)}")
    
    for i, project in enumerate(test_cases, 1):
        print(f"\n📍 Progress: {i}/{len(test_cases)}")
        result = tester.test_project(project)
        tester.results.append(result)
    
    tester.print_summary_report()
    
    # Save report
    report = tester.generate_report()
    import json
    from datetime import datetime
    
    report_file = f"other_languages_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")

if __name__ == "__main__":
    test_other_languages() 