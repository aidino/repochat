"""
CLI Interface for RepoChat v1.0

Command Line Interface for TEAM Interaction & Tasking.
For Task 4.1 (F4.1), implements basic CLI with 'scan_project' command.
"""

import click
import sys
import os
from typing import Optional

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from teams.interaction_tasking.task_initiation_module import TaskInitiationModule
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.project_data_context import ProjectDataContext


class CLIInterface:
    """
    Command Line Interface handler for RepoChat.
    
    Provides CLI commands for interacting with the RepoChat system.
    For Task 4.1, implements the 'scan_project' command.
    """
    
    def __init__(self):
        """Initialize CLI interface with logging and components."""
        self.logger = get_logger("cli.interface")
        self.task_initiation = TaskInitiationModule()
        self.logger.info("CLI Interface initialized")
    
    def scan_project_command(self, repository_url: str, verbose: bool = False) -> Optional[ProjectDataContext]:
        """
        Execute scan project command.
        
        Args:
            repository_url: URL of the repository to scan
            verbose: Enable verbose output
            
        Returns:
            ProjectDataContext if successful, None if failed
        """
        log_function_entry(self.logger, "scan_project_command", 
                          repository_url=repository_url, verbose=verbose)
        
        try:
            # Display start message
            click.echo(f"🚀 Bắt đầu quét dự án: {repository_url}")
            if verbose:
                click.echo("🔧 Đang khởi tạo Orchestrator Agent...")
            
            # Create task definition
            task_definition = self.task_initiation.create_scan_project_task(repository_url)
            
            if verbose:
                click.echo(f"📋 Task ID: {task_definition.task_id}")
                click.echo(f"🕐 Thời gian tạo: {task_definition.created_at}")
            
            # Initialize orchestrator  
            orchestrator = OrchestratorAgent()
            
            if verbose:
                click.echo("📦 Đang thực hiện Phase 1: Thu thập dữ liệu...")
            
            # Execute scan project task
            project_context = orchestrator.handle_scan_project_task(task_definition)
            
            # Display results
            click.echo("✅ Quét dự án hoàn thành thành công!")
            click.echo(f"📁 Đường dẫn: {project_context.cloned_code_path}")
            click.echo(f"🔤 Ngôn ngữ: {', '.join(project_context.detected_languages)}")
            click.echo(f"🎯 Ngôn ngữ chính: {project_context.primary_language}")
            click.echo(f"📊 Số lượng ngôn ngữ: {project_context.language_count}")
            
            if verbose:
                click.echo("\n📈 Thống kê Agent:")
                stats = orchestrator.get_agent_stats()
                click.echo(f"  • Tasks thành công: {stats['statistics']['successful_tasks']}")
                click.echo(f"  • Uptime: {stats['uptime_seconds']:.2f}s")
            
            # Cleanup
            orchestrator.shutdown()
            
            log_function_exit(self.logger, "scan_project_command", result="success")
            return project_context
            
        except ValueError as e:
            click.echo(f"❌ Lỗi đầu vào: {e}", err=True)
            log_function_exit(self.logger, "scan_project_command", result="input_error")
            return None
        except Exception as e:
            click.echo(f"❌ Lỗi thực thi: {e}", err=True)
            self.logger.error(f"Scan project command failed: {e}", exc_info=True)
            log_function_exit(self.logger, "scan_project_command", result="error")
            return None


# CLI Application using Click
@click.group()
@click.version_option(version='1.0.0', prog_name='RepoChat')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """
    🤖 RepoChat v1.0 - AI Repository Analysis Assistant
    
    Trợ lý AI thông minh để phân tích repository code một cách sâu sắc và hiệu quả.
    """
    # Store verbose flag in context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        click.echo("🔧 RepoChat CLI khởi động với chế độ verbose")


@cli.command('scan-project')
@click.argument('repository_url', type=str)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def scan_project(ctx, repository_url: str, verbose: bool):
    """
    Quét và phân tích một repository Git.
    
    REPOSITORY_URL: URL của repository Git cần phân tích
    
    Ví dụ:
      repochat scan-project https://github.com/user/repo.git
      repochat scan-project https://github.com/spring-projects/spring-petclinic.git -v
    """
    # Use verbose from context or command option
    verbose = verbose or ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo(f"🎯 Lệnh: scan-project")
        click.echo(f"📍 Repository: {repository_url}")
    
    # Initialize CLI interface and execute command
    cli_interface = CLIInterface()
    result = cli_interface.scan_project_command(repository_url, verbose)
    
    if result is None:
        sys.exit(1)


@cli.command('review-pr')
@click.argument('repository_url', type=str)
@click.argument('pr_id', type=str)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def review_pr(ctx, repository_url: str, pr_id: str, verbose: bool):
    """
    Review một Pull Request (Placeholder cho Task 4.2).
    
    REPOSITORY_URL: URL của repository Git
    PR_ID: ID hoặc URL của Pull Request
    
    Lưu ý: Tính năng này sẽ được implement trong Task 4.2.
    """
    verbose = verbose or ctx.obj.get('verbose', False)
    
    click.echo("🚧 Tính năng Review PR sẽ được implement trong Task 4.2")
    click.echo(f"📍 Repository: {repository_url}")
    click.echo(f"🔀 PR ID: {pr_id}")
    
    if verbose:
        click.echo("ℹ️  Hiện tại chỉ hỗ trợ scan-project command")


@cli.command()
def status():
    """
    Hiển thị trạng thái hệ thống RepoChat.
    """
    click.echo("📊 Trạng thái RepoChat v1.0:")
    click.echo("  ✅ Phase 1: Data Acquisition - COMPLETED")
    click.echo("  ✅ Phase 2: Code Knowledge Graph - COMPLETED") 
    click.echo("  ✅ Phase 3: Code Analysis & LLM - COMPLETED")
    click.echo("  🚧 Phase 4: CLI Interface - IN PROGRESS")
    click.echo("  ⏳ Phase 5: Frontend - PLANNED")
    click.echo("  ⏳ Phase 6: Testing & Deployment - PLANNED")
    click.echo("\n🛠️  Các lệnh hiện có:")
    click.echo("  • scan-project: Quét repository Git")
    click.echo("  • review-pr: Review PR (sắp có)")
    click.echo("  • status: Hiển thị trạng thái")


if __name__ == '__main__':
    cli() 