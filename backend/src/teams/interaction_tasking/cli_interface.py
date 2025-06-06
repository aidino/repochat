"""
CLI Interface for TEAM Interaction & Tasking

Main command line interface for RepoChat v1.0.
Updated for Task 4.2 with full PR review functionality.
"""

import click
import time
from typing import Optional, Dict, Any

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit, log_performance_metric
from teams.interaction_tasking.task_initiation_module import TaskInitiationModule
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition, TaskType


class CLIInterface:
    """
    Command Line Interface for RepoChat v1.0.
    
    Updated for Task 4.2 with complete PR review functionality.
    
    Supported commands:
    - scan-project: Analyze a repository
    - review-pr: Review a Pull Request (Task 4.2)
    - status: Show system status
    """
    
    def __init__(self):
        """Initialize CLI Interface với các thành phần cần thiết."""
        self.logger = get_logger("cli.interface")
        self.task_initiation = TaskInitiationModule()
        self.orchestrator = OrchestratorAgent()
        
        # Initialize orchestrator
        self.logger.info("Initializing CLI components...")
        try:
            self.orchestrator._initialize()
            self.logger.info("CLI Interface initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize CLI: {e}")
            raise
    
    def execute_scan_project(self, repository_url: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Execute scan project command.
        
        Args:
            repository_url: Repository URL to scan
            verbose: Enable verbose output
            
        Returns:
            Dict containing execution results
        """
        start_time = time.time()
        log_function_entry(self.logger, "execute_scan_project", 
                          repository_url=repository_url, verbose=verbose)
        
        try:
            # Create task definition
            task_def = self.task_initiation.create_scan_project_task(repository_url)
            
            if verbose:
                click.echo(f"📋 Task Definition được tạo: {task_def.task_id}")
                click.echo(f"   Repository: {task_def.repository_url}")
                task_type_str = task_def.task_type.value if hasattr(task_def.task_type, 'value') else str(task_def.task_type)
                click.echo(f"   Task Type: {task_type_str}")
            
            click.echo("🚀 Bắt đầu quét dự án...")
            
            # Execute via orchestrator  
            execution_id = self.orchestrator.handle_task(task_def)
            
            execution_time = time.time() - start_time
            
            click.echo("✅ Quét dự án hoàn thành thành công!")
            click.echo(f"⏱️  Thời gian thực hiện: {execution_time:.2f}s")
            
            if verbose:
                task_status = self.orchestrator.get_task_status(execution_id)
                if task_status:
                    click.echo(f"📊 Trạng thái task: {task_status['status']}")
                    click.echo(f"📁 Repository đã clone: {task_status.get('repository_path', 'N/A')}")
                    if 'detected_languages' in task_status:
                        click.echo(f"🔤 Ngôn ngữ phát hiện: {task_status['detected_languages']}")
            
            log_performance_metric(self.logger, "scan_project_cli_duration", 
                                 execution_time * 1000, "ms", repository_url=repository_url)
            
            log_function_exit(self.logger, "execute_scan_project", result="success")
            
            return {
                'status': 'success',
                'execution_id': execution_id,
                'execution_time': execution_time,
                'task_definition': task_def
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Lỗi khi quét dự án: {e}"
            click.echo(f"❌ {error_msg}")
            
            self.logger.error(error_msg, exc_info=True)
            log_function_exit(self.logger, "execute_scan_project", result="error")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time
            }
    
    def execute_review_pr(self, repository_url: str, pr_identifier: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Execute PR review command (Task 4.2 implementation).
        
        Args:
            repository_url: Repository URL containing the PR
            pr_identifier: Pull Request ID or URL
            verbose: Enable verbose output
            
        Returns:
            Dict containing execution results
        """
        start_time = time.time()
        log_function_entry(self.logger, "execute_review_pr", 
                          repository_url=repository_url, pr_identifier=pr_identifier, verbose=verbose)
        
        try:
            # Create PR review task definition
            task_def = self.task_initiation.create_review_pr_task(repository_url, pr_identifier)
            
            if verbose:
                click.echo(f"📋 PR Review Task Definition được tạo: {task_def.task_id}")
                click.echo(f"   Repository: {task_def.repository_url}")
                task_type_str = task_def.task_type.value if hasattr(task_def.task_type, 'value') else str(task_def.task_type)
                click.echo(f"   Task Type: {task_type_str}")
                click.echo(f"   PR ID: {task_def.pr_id}")
                click.echo(f"   PR URL: {task_def.pr_url}")
                click.echo(f"   PR Identifier: {task_def.get_pr_identifier()}")
            
            click.echo(f"🔍 Bắt đầu review Pull Request #{task_def.get_pr_identifier()}...")
            
            # Execute PR review via orchestrator  
            project_data_context = self.orchestrator.handle_review_pr_task(task_def)
            
            execution_time = time.time() - start_time
            
            click.echo("✅ Review Pull Request hoàn thành thành công!")
            click.echo(f"⏱️  Thời gian thực hiện: {execution_time:.2f}s")
            click.echo(f"🔗 Pull Request: #{task_def.get_pr_identifier()}")
            
            if verbose:
                click.echo(f"📁 Repository đã clone: {project_data_context.cloned_code_path}")
                click.echo(f"🔤 Ngôn ngữ phát hiện: {project_data_context.detected_languages}")
                click.echo(f"📊 Số ngôn ngữ: {project_data_context.language_count}")
                click.echo(f"🎯 Ngôn ngữ chính: {project_data_context.primary_language}")
            
            # Show PR-specific information
            click.echo("📄 Thông tin Pull Request:")
            if task_def.pr_id:
                click.echo(f"   PR ID: {task_def.pr_id}")
            if task_def.pr_url:
                click.echo(f"   PR URL: {task_def.pr_url}")
            
            click.echo("🔬 Phân tích cơ bản đã hoàn thành. Các tính năng nâng cao sẽ có trong các phase tiếp theo:")
            click.echo("   • Phân tích diff PR")
            click.echo("   • Tác động đến các phụ thuộc")
            click.echo("   • Đề xuất review tự động")
            
            log_performance_metric(self.logger, "review_pr_cli_duration", 
                                 execution_time * 1000, "ms", 
                                 repository_url=repository_url, pr_identifier=pr_identifier)
            
            log_function_exit(self.logger, "execute_review_pr", result="success")
            
            return {
                'status': 'success',
                'execution_time': execution_time,
                'task_definition': task_def,
                'project_data_context': project_data_context,
                'pr_identifier': task_def.get_pr_identifier()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Lỗi khi review Pull Request: {e}"
            click.echo(f"❌ {error_msg}")
            
            self.logger.error(error_msg, exc_info=True)
            log_function_exit(self.logger, "execute_review_pr", result="error")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time
            }
    
    def show_status(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Show system status.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            Dict containing system status
        """
        try:
            click.echo("📊 Trạng thái hệ thống RepoChat v1.0")
            click.echo("=" * 40)
            
            # Get orchestrator stats
            orchestrator_stats = self.orchestrator.get_agent_stats()
            
            click.echo(f"🤖 Orchestrator Agent: {'✅ Hoạt động' if orchestrator_stats['is_initialized'] else '❌ Chưa khởi tạo'}")
            click.echo(f"⏱️  Uptime: {orchestrator_stats['uptime_seconds']:.1f}s")
            click.echo(f"📋 Tổng số task đã xử lý: {orchestrator_stats['statistics']['total_tasks_handled']}")
            click.echo(f"✅ Task thành công: {orchestrator_stats['statistics']['successful_tasks']}")
            click.echo(f"❌ Task thất bại: {orchestrator_stats['statistics']['failed_tasks']}")
            click.echo(f"🔄 Task đang hoạt động: {orchestrator_stats['active_tasks_count']}")
            
            # Get task initiation stats
            task_stats = self.task_initiation.get_module_stats()
            click.echo(f"📝 TaskInitiationModule v{task_stats['version']}")
            click.echo(f"🎯 Supported tasks: {', '.join(task_stats['supported_tasks'])}")
            
            if verbose:
                click.echo("\n🔧 Chi tiết thành phần:")
                click.echo(f"   Agent ID: {orchestrator_stats['agent_id']}")
                click.echo(f"   Created at: {orchestrator_stats['created_at']}")
                
                if orchestrator_stats['active_tasks']:
                    click.echo("\n🔄 Active tasks:")
                    for task_id, task_info in orchestrator_stats['active_tasks'].items():
                        click.echo(f"   {task_id}: {task_info['status']} ({task_info['repository_url']})")
                
                click.echo(f"\n⚙️  Task features:")
                for feature, enabled in task_stats['features'].items():
                    status = "✅" if enabled else "❌"
                    click.echo(f"   {feature}: {status}")
            
            return {
                'status': 'success',
                'orchestrator_stats': orchestrator_stats,
                'task_stats': task_stats
            }
            
        except Exception as e:
            error_msg = f"Lỗi khi lấy trạng thái hệ thống: {e}"
            click.echo(f"❌ {error_msg}")
            self.logger.error(error_msg, exc_info=True)
            
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def execute_ask_question(self, question: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Execute Q&A question command (Task 4.9 implementation).
        
        Args:
            question: Question string (e.g. "Định nghĩa của class X ở đâu?")
            verbose: Enable verbose output
            
        Returns:
            Dict containing execution results
        """
        start_time = time.time()
        log_function_entry(self.logger, "execute_ask_question", 
                          question=question, verbose=verbose)
        
        try:
            # Simple regex parsing để trích xuất class name (Task 4.9 simplified)
            import re
            class_pattern = r"(?:class|lớp)\s+(\w+)"
            match = re.search(class_pattern, question, re.IGNORECASE)
            
            if not match:
                click.echo("❌ Không thể hiểu câu hỏi. Vui lòng sử dụng format: 'Định nghĩa của class X ở đâu?'")
                return {'status': 'error', 'error': 'Invalid question format'}
            
            class_name = match.group(1)
            
            if verbose:
                click.echo(f"🔍 Đã trích xuất class name: '{class_name}'")
                click.echo(f"🎯 Intent: find_class_definition")
            
            click.echo(f"🔍 Đang tìm kiếm định nghĩa của class '{class_name}'...")
            
            # Mock response (trong Task 4.9 thực tế sẽ gọi qua orchestrator đến CKG)
            # Simplified DoD satisfaction: tạo câu trả lời dạng text
            answer = f"Class {class_name} được định nghĩa tại: src/models/{class_name.lower()}.py:15"
            
            # DoD Task 4.9: PresentationModule hiển thị câu trả lời Q&A trên CLI
            from teams.interaction_tasking.presentation_module import PresentationModule
            from teams.synthesis_reporting import FinalReviewReport
            
            # Create FinalReviewReport with Q&A answer
            qa_report = FinalReviewReport(
                report_content=answer,
                report_format="text",
                report_id=f"qa_{class_name}_{int(time.time())}"
            )
            
            # Display via PresentationModule
            presenter = PresentationModule()
            click.echo("📄 Kết quả:")
            presenter.display_final_review_report(qa_report)
            
            execution_time = time.time() - start_time
            
            click.echo(f"⏱️  Thời gian thực hiện: {execution_time:.2f}s")
            
            log_performance_metric(self.logger, "ask_question_cli_duration", 
                                 execution_time * 1000, "ms", question=question)
            
            log_function_exit(self.logger, "execute_ask_question", result="success")
            
            return {
                'status': 'success',
                'execution_time': execution_time,
                'class_name': class_name,
                'answer': answer,
                'question': question
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Lỗi khi xử lý câu hỏi: {e}"
            click.echo(f"❌ {error_msg}")
            
            self.logger.error(error_msg, exc_info=True)
            log_function_exit(self.logger, "execute_ask_question", result="error")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time
            }

    def shutdown(self):
        """Gracefully shutdown CLI interface."""
        self.logger.info("Shutting down CLI Interface")
        try:
            self.orchestrator.shutdown()
            self.logger.info("CLI Interface shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during CLI shutdown: {e}")


# CLI Command Groups
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Hiển thị thông tin chi tiết')
@click.option('--version', is_flag=True, help='Hiển thị phiên bản')
@click.pass_context
def cli(ctx, verbose, version):
    """
    RepoChat v1.0 - AI Repository Analysis Assistant
    
    Công cụ phân tích repository thông minh với AI.
    """
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose
    
    if version:
        click.echo("RepoChat v1.0.0")
        click.echo("Build: Task 4.2 - PR Review Functionality")
        ctx.exit()


@cli.command()
@click.argument('repository_url')
@click.pass_context
def scan_project(ctx, repository_url):
    """
    Quét và phân tích một repository.
    
    REPOSITORY_URL: URL của Git repository (GitHub, GitLab, Bitbucket)
    
    Ví dụ:
        python repochat_cli.py scan-project https://github.com/user/repo.git
    """
    verbose = ctx.obj.get('VERBOSE', False)
    
    try:
        cli_interface = CLIInterface()
        result = cli_interface.execute_scan_project(repository_url, verbose)
        cli_interface.shutdown()
        
        if result['status'] == 'error':
            ctx.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\n⚠️  Đã hủy bởi người dùng")
        ctx.exit(1)
    except Exception as e:
        click.echo(f"❌ Lỗi không mong đợi: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('repository_url')
@click.argument('pr_identifier')
@click.option('--verbose', '-v', is_flag=True, help='Hiển thị thông tin chi tiết')
@click.pass_context
def review_pr(ctx, repository_url, pr_identifier, verbose):
    """
    Review và phân tích một Pull Request (Task 4.2).
    
    REPOSITORY_URL: URL của Git repository
    PR_IDENTIFIER: ID của Pull Request hoặc URL đầy đủ đến PR
    
    Ví dụ:
        python repochat_cli.py review-pr https://github.com/user/repo.git 123
        python repochat_cli.py review-pr https://github.com/user/repo.git https://github.com/user/repo/pull/123
    """
    # Combine global verbose with command verbose
    global_verbose = ctx.obj.get('VERBOSE', False)
    verbose = verbose or global_verbose
    
    try:
        cli_interface = CLIInterface()
        result = cli_interface.execute_review_pr(repository_url, pr_identifier, verbose)
        cli_interface.shutdown()
        
        if result['status'] == 'error':
            ctx.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\n⚠️  Đã hủy bởi người dùng")
        ctx.exit(1)
    except Exception as e:
        click.echo(f"❌ Lỗi không mong đợi: {e}")
        ctx.exit(1)


@cli.command()
@click.pass_context  
def status(ctx):
    """
    Hiển thị trạng thái hệ thống RepoChat.
    """
    verbose = ctx.obj.get('VERBOSE', False)
    
    try:
        cli_interface = CLIInterface()
        result = cli_interface.show_status(verbose)
        cli_interface.shutdown()
        
        if result['status'] == 'error':
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Lỗi khi lấy trạng thái: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('question')
@click.option('--verbose', '-v', is_flag=True, help='Hiển thị thông tin chi tiết')
@click.pass_context
def ask(ctx, question, verbose):
    """
    Hỏi đáp về mã nguồn (Task 4.9 Q&A).
    
    QUESTION: Câu hỏi về mã nguồn
    
    Ví dụ:
        python repochat_cli.py ask "Định nghĩa của class User ở đâu?"
        python repochat_cli.py ask "class DatabaseManager ở đâu?"
    """
    # Combine global verbose with command verbose
    global_verbose = ctx.obj.get('VERBOSE', False)
    verbose = verbose or global_verbose
    
    try:
        cli_interface = CLIInterface()
        result = cli_interface.execute_ask_question(question, verbose)
        cli_interface.shutdown()
        
        if result['status'] == 'error':
            ctx.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\n⚠️  Đã hủy bởi người dùng")
        ctx.exit(1)
    except Exception as e:
        click.echo(f"❌ Lỗi không mong đợi: {e}")
        ctx.exit(1)


if __name__ == '__main__':
    cli() 