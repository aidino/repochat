#!/usr/bin/env python3
"""
Manual test Neo4j connection với credentials đúng
"""
import os
import sys

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule

def main():
    print("🔗 Testing Neo4j Connection with correct credentials")
    
    # Use correct credentials for the running container
    neo4j = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        username="neo4j", 
        password="repochat123"
    )
    
    try:
        success = neo4j.connect()
        if success:
            print("✅ Neo4j connection successful!")
            
            # Test simple query
            result = neo4j.execute_query("RETURN 1 as test, 'Hello Neo4j' as message")
            print(f"✅ Query result: {result}")
            
            # Test health check
            health = neo4j.health_check()
            print(f"✅ Health check: {health}")
            
        else:
            print("❌ Neo4j connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        neo4j.disconnect()
        print("🔌 Disconnected")

if __name__ == "__main__":
    main() 