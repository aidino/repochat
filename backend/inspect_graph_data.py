#!/usr/bin/env python3
"""
Inspect Graph Data - Xem cấu trúc dữ liệu trong Neo4j để hiểu tại sao không có circular dependencies
"""

import os
import sys

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule

def main():
    print("🔍 Graph Data Inspection - Understanding CKG Structure")
    print("=" * 80)
    
    # Connect to Neo4j
    neo4j = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="repochat123"
    )
    neo4j.connect()
    
    with neo4j.get_session() as session:
        print("\n1️⃣ OVERVIEW - Total Nodes & Relationships")
        print("-" * 50)
        
        # Total nodes
        result = session.run("MATCH (n) RETURN count(n) as total_nodes")
        total_nodes = result.single()['total_nodes']
        print(f"📊 Total nodes: {total_nodes}")
        
        # Total relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as total_rels")
        total_rels = result.single()['total_rels']
        print(f"🔗 Total relationships: {total_rels}")
        
        print("\n2️⃣ NODE TYPES - Labels Distribution")
        print("-" * 50)
        
        # Node labels
        result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count ORDER BY count DESC")
        for record in result:
            labels = record['labels']
            count = record['count']
            print(f"📋 {labels}: {count}")
        
        print("\n3️⃣ RELATIONSHIP TYPES - Distribution")
        print("-" * 50)
        
        # Relationship types
        result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count ORDER BY count DESC")
        for record in result:
            rel_type = record['rel_type']
            count = record['count']
            print(f"🔗 {rel_type}: {count}")
        
        print("\n4️⃣ PROJECT DATA - Specific Projects")
        print("-" * 50)
        
        # Projects and their files
        result = session.run("""
        MATCH (p:Project)
        RETURN p.name as project_name, p.project_name as project_name_attr
        """)
        
        projects = []
        for record in result:
            project_name = record['project_name'] or record['project_name_attr']
            projects.append(project_name)
            print(f"📁 Project: {project_name}")
        
        # For each project, show file and class counts
        for project in projects:
            if project:
                print(f"\n   📊 {project} Details:")
                
                # Files
                result = session.run("""
                MATCH (f:File {project_name: $project_name})
                RETURN count(f) as file_count
                """, project_name=project)
                file_count = result.single()['file_count']
                print(f"      📄 Files: {file_count}")
                
                # Classes
                result = session.run("""
                MATCH (c:Class {project_name: $project_name})
                RETURN count(c) as class_count
                """, project_name=project)
                class_count = result.single()['class_count']
                print(f"      🏗️  Classes: {class_count}")
                
                # Methods
                result = session.run("""
                MATCH (m:Method {project_name: $project_name})
                RETURN count(m) as method_count
                """, project_name=project)
                method_count = result.single()['method_count']
                print(f"      ⚙️  Methods: {method_count}")
        
        print("\n5️⃣ RELATIONSHIPS ANALYSIS - Specific to Circular Dependencies")
        print("-" * 50)
        
        # Check for CONTAINS relationships (file cycles)
        result = session.run("""
        MATCH (f1:File)-[:CONTAINS]->(f2:File)
        RETURN count(*) as contains_count
        """)
        contains_count = result.single()['contains_count']
        print(f"🔗 File CONTAINS File relationships: {contains_count}")
        
        # Check for CALLS relationships (method cycles)
        result = session.run("""
        MATCH (m1:Method)-[:CALLS]->(m2:Method)
        RETURN count(*) as calls_count
        """)
        calls_count = result.single()['calls_count']
        print(f"🔗 Method CALLS Method relationships: {calls_count}")
        
        # Check for EXTENDS/IMPLEMENTS (class inheritance cycles)
        result = session.run("""
        MATCH (c1:Class)-[:EXTENDS]->(c2:Class)
        RETURN count(*) as extends_count
        """)
        extends_count = result.single()['extends_count']
        print(f"🔗 Class EXTENDS Class relationships: {extends_count}")
        
        result = session.run("""
        MATCH (c1:Class)-[:IMPLEMENTS]->(c2:Class)
        RETURN count(*) as implements_count
        """)
        implements_count = result.single()['implements_count']
        print(f"🔗 Class IMPLEMENTS Interface relationships: {implements_count}")
        
        print("\n6️⃣ SAMPLE DATA - First Few Entities")
        print("-" * 50)
        
        # Show sample files
        result = session.run("""
        MATCH (f:File)
        RETURN f.name as file_name, f.project_name as project
        LIMIT 5
        """)
        
        print("📄 Sample Files:")
        for record in result:
            print(f"   • {record['file_name']} (project: {record['project']})")
        
        # Show sample classes
        result = session.run("""
        MATCH (c:Class)
        RETURN c.name as class_name, c.project_name as project
        LIMIT 5
        """)
        
        print("\n🏗️  Sample Classes:")
        for record in result:
            print(f"   • {record['class_name']} (project: {record['project']})")
    
    neo4j.disconnect()
    print(f"\n✅ Graph inspection completed!")

if __name__ == "__main__":
    main() 