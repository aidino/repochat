#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from shared.models.task_definition import TaskDefinition, TaskType

def test_validation():
    print("Testing TaskDefinition validation...")
    
    # Test 1: Valid scan project
    try:
        scan_task = TaskDefinition(
            repository_url='https://github.com/user/repo.git',
            task_type=TaskType.SCAN_PROJECT,
            task_id='test-123'
        )
        print("✅ Scan task creation: OK")
        print(f"   Task: {scan_task}")
    except Exception as e:
        print(f"❌ Scan task creation failed: {e}")
    
    # Test 2: Valid PR task with ID
    try:
        pr_task_id = TaskDefinition(
            repository_url='https://github.com/user/repo.git',
            task_type=TaskType.REVIEW_PR,
            pr_id='123',
            task_id='test-pr-123'
        )
        print("✅ PR task with ID: OK")
        print(f"   Task: {pr_task_id}")
        print(f"   PR identifier: {pr_task_id.get_pr_identifier()}")
    except Exception as e:
        print(f"❌ PR task with ID failed: {e}")
    
    # Test 3: Valid PR task with URL
    try:
        pr_task_url = TaskDefinition(
            repository_url='https://github.com/user/repo.git',
            task_type=TaskType.REVIEW_PR,
            pr_url='https://github.com/user/repo/pull/456',
            task_id='test-pr-456'
        )
        print("✅ PR task with URL: OK")
        print(f"   Task: {pr_task_url}")
        print(f"   PR identifier: {pr_task_url.get_pr_identifier()}")
    except Exception as e:
        print(f"❌ PR task with URL failed: {e}")
    
    # Test 4: Invalid PR task (no PR info) - should fail
    try:
        invalid_task = TaskDefinition(
            repository_url='https://github.com/user/repo.git',
            task_type=TaskType.REVIEW_PR,
            task_id='invalid'
        )
        print(f"❌ Invalid PR task should have failed but didn't: {invalid_task}")
    except Exception as e:
        print(f"✅ Invalid PR task correctly failed: {e}")

if __name__ == '__main__':
    test_validation() 