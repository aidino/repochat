#!/usr/bin/env python3
"""
Demo script for Neo4j Connection Module

This script demonstrates the Neo4jConnectionModule functionality:
- Connection to Neo4j (if available)
- Basic query operations
- Error handling
- Statistics reporting

Run this after setting up Neo4j Community Edition to verify connectivity.
"""

import sys
import os
sys.path.append('src')

from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule


def demo_neo4j_connection():
    """
    Demonstrate Neo4j connection functionality.
    """
    print("🚀 RepoChat - Neo4j Connection Module Demo")
    print("=" * 50)
    
    # Initialize module with default settings
    print("\n1. Initializing Neo4j Connection Module...")
    neo4j_module = Neo4jConnectionModule()
    
    print(f"   URI: {neo4j_module.uri}")
    print(f"   Username: {neo4j_module.username}")
    print(f"   Database: {neo4j_module.database}")
    print(f"   Connected: {neo4j_module.is_connected()}")
    
    # Test health check without connection
    print("\n2. Testing health check (not connected)...")
    health = neo4j_module.health_check()
    print(f"   Health Status: {health}")
    
    # Attempt connection
    print("\n3. Attempting to connect to Neo4j...")
    try:
        success = neo4j_module.connect()
        if success:
            print("   ✅ Connection successful!")
            
            # Test health check with connection
            print("\n4. Testing health check (connected)...")
            health = neo4j_module.health_check()
            print(f"   Health Status: {health}")
            
            # Test basic query
            print("\n5. Testing basic query...")
            result = neo4j_module.execute_query("RETURN 'Hello Neo4j!' as message")
            print(f"   Query Result: {result}")
            
            # Test node creation
            print("\n6. Testing node creation...")
            node_data = neo4j_module.create_node(
                'DemoNode', 
                {'name': 'test_node', 'timestamp': '2024-12-05', 'type': 'demo'}
            )
            if node_data:
                print(f"   ✅ Node created: {node_data}")
            else:
                print("   ❌ Node creation failed")
            
            # Test node finding
            print("\n7. Testing node search...")
            nodes = neo4j_module.find_nodes('DemoNode', {'type': 'demo'})
            print(f"   Found {len(nodes)} demo nodes")
            
            # Test advanced query with session
            print("\n8. Testing session-based query...")
            try:
                with neo4j_module.get_session() as session:
                    result = session.run("MATCH (n:DemoNode) RETURN count(n) as demo_count")
                    count = result.single()["demo_count"]
                    print(f"   Demo nodes count: {count}")
            except Exception as e:
                print(f"   Session query error: {e}")
            
            # Get statistics
            print("\n9. Connection Statistics...")
            stats = neo4j_module.get_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
                
        else:
            print("   ❌ Connection failed (Neo4j may not be running)")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test context manager
    print("\n10. Testing context manager...")
    try:
        with Neo4jConnectionModule() as neo4j:
            if neo4j.is_connected():
                result = neo4j.execute_query("RETURN 42 as answer")
                print(f"    Context manager result: {result}")
            else:
                print("    Context manager: connection failed")
    except Exception as e:
        print(f"    Context manager error: {e}")
    
    # Cleanup
    print("\n11. Disconnecting...")
    neo4j_module.disconnect()
    print(f"   Connected after disconnect: {neo4j_module.is_connected()}")
    
    print("\n" + "=" * 50)
    print("🎯 Demo completed!")
    print("\nNext steps to test with real Neo4j:")
    print("1. Install Neo4j Community Edition")
    print("2. Start Neo4j server: neo4j start")
    print("3. Set password: neo4j-admin set-initial-password password")
    print("4. Access browser: http://localhost:7474")
    print("5. Run this demo again")


if __name__ == "__main__":
    demo_neo4j_connection() 