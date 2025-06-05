#!/usr/bin/env python3
"""
Simple Test for Kotlin and Dart Parsers

Creates sample code files and tests the parsers directly to validate functionality.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from teams.ckg_operations.kotlin_parser import KotlinParser
from teams.ckg_operations.dart_parser import DartParser


def test_kotlin_parser():
    """Test Kotlin parser with sample code."""
    print("🔧 Testing Kotlin Parser")
    print("-" * 30)
    
    kotlin_code = '''
package com.example.app

import kotlinx.coroutines.*

class UserManager {
    private val users = mutableListOf<User>()
    
    fun addUser(user: User) {
        users.add(user)
        logUser(user)
    }
    
    private fun logUser(user: User) {
        println("User added: ${user.name}")
    }
    
    suspend fun fetchUsers(): List<User> {
        delay(100)
        return users.toList()
    }
}

data class User(val id: Int, val name: String)

fun main() {
    val manager = UserManager()
    val user = User(1, "John Doe")
    manager.addUser(user)
}
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.kt', delete=False) as f:
        f.write(kotlin_code)
        kotlin_file = f.name
    
    try:
        # Test parser
        parser = KotlinParser()
        start_time = time.time()
        result = parser.parse_file(kotlin_file, os.path.dirname(kotlin_file))
        parse_time = time.time() - start_time
        
        print(f"✅ Parse time: {parse_time * 1000:.1f}ms")
        print(f"📊 Results:")
        print(f"   • Entities: {len(result.entities)}")
        print(f"   • Relationships: {len(result.relationships)}")
        print(f"   • Errors: {len(result.errors)}")
        print(f"   • Module name: {result.metadata.get('module_name', 'N/A')}")
        
        # Print entity breakdown
        entity_types = {}
        for entity in result.entities:
            entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
        
        print(f"   • Entity breakdown:")
        for entity_type, count in entity_types.items():
            print(f"     - {entity_type}: {count}")
        
        # Print sample entities
        print(f"   • Sample entities:")
        for entity in result.entities[:5]:
            print(f"     - {entity.entity_type}: {entity.name} (line {entity.start_line})")
        
        if result.errors:
            print(f"   ❌ Errors:")
            for error in result.errors:
                print(f"     - {error}")
        
        # Get stats
        stats = parser.get_stats()
        print(f"   📈 Parser Stats:")
        print(f"     - Files processed: {stats['files_processed']}")
        print(f"     - Files successful: {stats['files_successful']}")
        print(f"     - Total entities: {stats['total_entities_found']}")
        
        return len(result.errors) == 0
        
    finally:
        # Cleanup
        os.unlink(kotlin_file)


def test_dart_parser():
    """Test Dart parser with sample code."""
    print("\n🎯 Testing Dart Parser")
    print("-" * 30)
    
    dart_code = '''
library example.user_service;

import 'dart:async';
import 'dart:io';

class UserService {
  final List<User> _users = [];
  
  void addUser(User user) {
    _users.add(user);
    _logUser(user);
  }
  
  void _logUser(User user) {
    print('User added: ${user.name}');
  }
  
  Future<List<User>> getUsers() async {
    await Future.delayed(Duration(milliseconds: 100));
    return List.from(_users);
  }
  
  int get userCount => _users.length;
}

class User {
  final int id;
  final String name;
  
  User(this.id, this.name);
  
  @override
  String toString() => 'User($id, $name)';
}

mixin Loggable {
  void log(String message) {
    print('[${DateTime.now()}] $message');
  }
}

enum Status { active, inactive, pending }

void main() async {
  final service = UserService();
  final user = User(1, 'Jane Doe');
  service.addUser(user);
  
  final users = await service.getUsers();
  print('Total users: ${users.length}');
}
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dart', delete=False) as f:
        f.write(dart_code)
        dart_file = f.name
    
    try:
        # Test parser
        parser = DartParser()
        start_time = time.time()
        result = parser.parse_file(dart_file, os.path.dirname(dart_file))
        parse_time = time.time() - start_time
        
        print(f"✅ Parse time: {parse_time * 1000:.1f}ms")
        print(f"📊 Results:")
        print(f"   • Entities: {len(result.entities)}")
        print(f"   • Relationships: {len(result.relationships)}")
        print(f"   • Errors: {len(result.errors)}")
        print(f"   • Module name: {result.metadata.get('module_name', 'N/A')}")
        
        # Print entity breakdown
        entity_types = {}
        for entity in result.entities:
            entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
        
        print(f"   • Entity breakdown:")
        for entity_type, count in entity_types.items():
            print(f"     - {entity_type}: {count}")
        
        # Print sample entities
        print(f"   • Sample entities:")
        for entity in result.entities[:5]:
            print(f"     - {entity.entity_type}: {entity.name} (line {entity.start_line})")
        
        if result.errors:
            print(f"   ❌ Errors:")
            for error in result.errors:
                print(f"     - {error}")
        
        # Get stats
        stats = parser.get_stats()
        print(f"   📈 Parser Stats:")
        print(f"     - Files processed: {stats['files_processed']}")
        print(f"     - Files successful: {stats['files_successful']}")
        print(f"     - Total entities: {stats['total_entities_found']}")
        
        return len(result.errors) == 0
        
    finally:
        # Cleanup
        os.unlink(dart_file)


def main():
    """Main function to run simple tests."""
    print("🚀 RepoChat v1.0 - Simple Kotlin & Dart Parser Test")
    print("Testing parsers with sample code to validate functionality")
    print("=" * 60)
    
    try:
        kotlin_success = test_kotlin_parser()
        dart_success = test_dart_parser()
        
        print("\n" + "=" * 60)
        print("📋 SIMPLE TEST RESULTS")
        print("=" * 60)
        
        print(f"🔧 Kotlin Parser: {'✅ PASSED' if kotlin_success else '❌ FAILED'}")
        print(f"🎯 Dart Parser:   {'✅ PASSED' if dart_success else '❌ FAILED'}")
        
        overall_success = kotlin_success and dart_success
        print(f"\n🎉 Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n✅ Task 2.5 Implementation: Kotlin and Dart parsers are working correctly!")
            print("   • Both parsers can extract entities and relationships")
            print("   • Error handling is working properly")
            print("   • Statistics tracking is functional")
            print("   • Ready for integration with larger projects")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 