#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule

neo4j = Neo4jConnectionModule('bolt://localhost:7687', 'neo4j', 'repochat123')
neo4j.connect()

with neo4j.get_session() as session:
    # Check available projects
    result = session.run('MATCH (p:Project) RETURN p.name as name, p.project_name as project_name')
    projects = [(record['name'], record.get('project_name')) for record in result]
    print('Available projects:', projects)
    
    if projects:
        project_name = projects[0][0] or projects[0][1]
        print(f'Using project: {project_name}')
        
        # Check files for this project
        result = session.run('MATCH (f:File {project_name: $project_name}) RETURN count(f) as file_count', project_name=project_name)
        file_count = result.single()['file_count']
        print(f'Files for project {project_name}: {file_count}')
        
        # Check classes
        result = session.run('MATCH (c:Class {project_name: $project_name}) RETURN count(c) as class_count', project_name=project_name)
        class_count = result.single()['class_count']
        print(f'Classes for project {project_name}: {class_count}')

neo4j.close() 