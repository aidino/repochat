"""
Configuration Management Agent cho TEAM Interaction & Tasking

Agent này chịu trách nhiệm quản lý cấu hình của người dùng, đặc biệt là:
- Cấu hình model LLM cho từng TEAM agent/chức năng
- Lưu trữ và truy xuất preferences người dùng  
- Quản lý session và user settings
- Cung cấp cấu hình mặc định hợp lý
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit


class LLMProvider(Enum):
    """Các nhà cung cấp LLM được hỗ trợ"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class LLMConfiguration:
    """Cấu hình cho một model LLM cụ thể"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.1
    max_tokens: int = 1000
    timeout: int = 30
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dictionary"""
        return {
            "provider": self.provider.value,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "api_key_env": self.api_key_env,
            "base_url": self.base_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfiguration':
        """Tạo từ dictionary"""
        return cls(
            provider=LLMProvider(data["provider"]),
            model_name=data["model_name"],
            temperature=data.get("temperature", 0.1),
            max_tokens=data.get("max_tokens", 1000),
            timeout=data.get("timeout", 30),
            api_key_env=data.get("api_key_env"),
            base_url=data.get("base_url")
        )


@dataclass
class TeamLLMConfigs:
    """Cấu hình LLM cho tất cả các TEAM"""
    interaction_tasking: LLMConfiguration  # Cho NLU và dialog management
    code_analysis: LLMConfiguration       # Cho phân tích code chuyên sâu  
    synthesis_reporting: LLMConfiguration # Cho tóm tắt và sinh báo cáo
    llm_services_default: LLMConfiguration # Cấu hình mặc định cho TEAM LLM Services
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dictionary"""
        return {
            "interaction_tasking": self.interaction_tasking.to_dict(),
            "code_analysis": self.code_analysis.to_dict(),
            "synthesis_reporting": self.synthesis_reporting.to_dict(),
            "llm_services_default": self.llm_services_default.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamLLMConfigs':
        """Tạo từ dictionary"""
        return cls(
            interaction_tasking=LLMConfiguration.from_dict(data["interaction_tasking"]),
            code_analysis=LLMConfiguration.from_dict(data["code_analysis"]),
            synthesis_reporting=LLMConfiguration.from_dict(data["synthesis_reporting"]),
            llm_services_default=LLMConfiguration.from_dict(data["llm_services_default"])
        )


@dataclass
class UserConfiguration:
    """Cấu hình tổng thể của người dùng"""
    user_id: str
    display_name: str
    llm_configs: TeamLLMConfigs
    preferences: Dict[str, Any]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dictionary"""
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "llm_configs": self.llm_configs.to_dict(),
            "preferences": self.preferences,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserConfiguration':
        """Tạo từ dictionary"""
        return cls(
            user_id=data["user_id"],
            display_name=data["display_name"],
            llm_configs=TeamLLMConfigs.from_dict(data["llm_configs"]),
            preferences=data.get("preferences", {}),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )


class ConfigurationManagementAgent:
    """
    Agent quản lý cấu hình người dùng.
    
    Chức năng chính:
    - Lưu trữ và truy xuất cấu hình LLM cho từng TEAM
    - Quản lý preferences người dùng
    - Cung cấp cấu hình mặc định hợp lý
    - Validate cấu hình trước khi sử dụng
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """Khởi tạo Configuration Management Agent"""
        self.logger = get_logger("team.interaction.config_manager")
        
        # Xác định thư mục lưu trữ cấu hình
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".repochat" / "configs"
        
        # Tạo thư mục nếu chưa tồn tại
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache cấu hình trong session
        self._config_cache: Dict[str, UserConfiguration] = {}
        
        self.logger.info(f"Khởi tạo ConfigurationManagementAgent với config_dir: {self.config_dir}")
    
    def get_default_llm_configs(self) -> TeamLLMConfigs:
        """
        Tạo cấu hình LLM mặc định cho tất cả các TEAM.
        
        Returns:
            TeamLLMConfigs với cấu hình mặc định hợp lý
        """
        log_function_entry(self.logger, "get_default_llm_configs")
        
        try:
            # Cấu hình cho TEAM Interaction & Tasking (NLU, dialog)
            # Sử dụng model nhỏ, nhanh và tiết kiệm chi phí
            interaction_config = LLMConfiguration(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4o-mini",
                temperature=0.1,  # Ít random để có kết quả ổn định
                max_tokens=500,   # Đủ cho intent parsing và dialog
                timeout=15,
                api_key_env="OPENAI_API_KEY"
            )
            
            # Cấu hình cho TEAM Code Analysis  
            # Sử dụng model mạnh hơn cho phân tích code phức tạp
            code_analysis_config = LLMConfiguration(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4-turbo",
                temperature=0.2,  # Chút ít creativity cho phân tích
                max_tokens=2000,  # Nhiều hơn cho phân tích chi tiết
                timeout=45,
                api_key_env="OPENAI_API_KEY"
            )
            
            # Cấu hình cho TEAM Synthesis & Reporting
            # Model tốt cho tóm tắt và sinh văn bản mạch lạc
            synthesis_config = LLMConfiguration(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4o",
                temperature=0.3,  # Creativity cao hơn cho báo cáo
                max_tokens=1500,  # Đủ cho báo cáo chi tiết
                timeout=30,
                api_key_env="OPENAI_API_KEY"
            )
            
            # Cấu hình mặc định cho TEAM LLM Services
            llm_services_config = LLMConfiguration(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4o-mini",
                temperature=0.2,
                max_tokens=1000,
                timeout=30,
                api_key_env="OPENAI_API_KEY"
            )
            
            default_configs = TeamLLMConfigs(
                interaction_tasking=interaction_config,
                code_analysis=code_analysis_config,
                synthesis_reporting=synthesis_config,
                llm_services_default=llm_services_config
            )
            
            self.logger.info("Tạo cấu hình LLM mặc định thành công")
            log_function_exit(self.logger, "get_default_llm_configs", result="success")
            
            return default_configs
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo cấu hình mặc định: {e}", exc_info=True)
            raise
    
    def get_user_configuration(self, user_id: str) -> UserConfiguration:
        """
        Lấy cấu hình của người dùng. Tạo mới nếu chưa tồn tại.
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            UserConfiguration của người dùng
        """
        log_function_entry(self.logger, "get_user_configuration", user_id=user_id)
        
        try:
            # Kiểm tra cache trước
            if user_id in self._config_cache:
                self.logger.debug(f"Trả về cấu hình từ cache cho user: {user_id}")
                return self._config_cache[user_id]
            
            # Đường dẫn file cấu hình
            config_file = self.config_dir / f"{user_id}.json"
            
            if config_file.exists():
                # Load từ file
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                user_config = UserConfiguration.from_dict(config_data)
                
                # Lưu vào cache
                self._config_cache[user_id] = user_config
                
                self.logger.info(f"Load cấu hình từ file cho user: {user_id}")
                log_function_exit(self.logger, "get_user_configuration", result="loaded_from_file")
                
                return user_config
            else:
                # Tạo cấu hình mới
                user_config = self._create_default_user_configuration(user_id)
                
                # Lưu vào file và cache
                self.save_user_configuration(user_config)
                
                self.logger.info(f"Tạo cấu hình mới cho user: {user_id}")
                log_function_exit(self.logger, "get_user_configuration", result="created_new")
                
                return user_config
                
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy cấu hình user: {e}", exc_info=True)
            
            # Fallback: trả về cấu hình mặc định
            return self._create_default_user_configuration(user_id)
    
    def save_user_configuration(self, user_config: UserConfiguration) -> bool:
        """
        Lưu cấu hình người dùng.
        
        Args:
            user_config: Cấu hình cần lưu
            
        Returns:
            True nếu lưu thành công
        """
        log_function_entry(self.logger, "save_user_configuration", user_id=user_config.user_id)
        
        try:
            # Cập nhật thời gian
            import datetime
            user_config.updated_at = datetime.datetime.now().isoformat()
            
            # Đường dẫn file cấu hình
            config_file = self.config_dir / f"{user_config.user_id}.json"
            
            # Lưu vào file
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(user_config.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Cập nhật cache
            self._config_cache[user_config.user_id] = user_config
            
            self.logger.info(f"Lưu cấu hình thành công cho user: {user_config.user_id}")
            log_function_exit(self.logger, "save_user_configuration", result="success")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu cấu hình: {e}", exc_info=True)
            log_function_exit(self.logger, "save_user_configuration", result="error")
            return False
    
    def update_llm_configuration(self, user_id: str, team_name: str, 
                                llm_config: LLMConfiguration) -> bool:
        """
        Cập nhật cấu hình LLM cho một TEAM cụ thể.
        
        Args:
            user_id: ID người dùng
            team_name: Tên TEAM (interaction_tasking, code_analysis, synthesis_reporting)
            llm_config: Cấu hình LLM mới
            
        Returns:
            True nếu cập nhật thành công
        """
        log_function_entry(self.logger, "update_llm_configuration", 
                          user_id=user_id, team_name=team_name)
        
        try:
            # Lấy cấu hình hiện tại
            user_config = self.get_user_configuration(user_id)
            
            # Validate team name
            valid_teams = ["interaction_tasking", "code_analysis", "synthesis_reporting", "llm_services_default"]
            if team_name not in valid_teams:
                raise ValueError(f"Team name không hợp lệ: {team_name}. Chỉ chấp nhận: {valid_teams}")
            
            # Validate LLM configuration
            if not self._validate_llm_configuration(llm_config):
                raise ValueError("Cấu hình LLM không hợp lệ")
            
            # Cập nhật cấu hình
            setattr(user_config.llm_configs, team_name, llm_config)
            
            # Lưu lại
            success = self.save_user_configuration(user_config)
            
            if success:
                self.logger.info(f"Cập nhật cấu hình LLM thành công cho team {team_name}, user {user_id}")
                log_function_exit(self.logger, "update_llm_configuration", result="success")
            else:
                self.logger.error(f"Lỗi khi lưu cấu hình đã cập nhật")
                log_function_exit(self.logger, "update_llm_configuration", result="save_error")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Lỗi khi cập nhật cấu hình LLM: {e}", exc_info=True)
            log_function_exit(self.logger, "update_llm_configuration", result="error")
            return False
    
    def get_llm_configuration_for_team(self, user_id: str, team_name: str) -> LLMConfiguration:
        """
        Lấy cấu hình LLM cho một TEAM cụ thể.
        
        Args:
            user_id: ID người dùng
            team_name: Tên TEAM
            
        Returns:
            LLMConfiguration cho TEAM đó
        """
        log_function_entry(self.logger, "get_llm_configuration_for_team", 
                          user_id=user_id, team_name=team_name)
        
        try:
            user_config = self.get_user_configuration(user_id)
            
            # Lấy cấu hình cho team
            if hasattr(user_config.llm_configs, team_name):
                config = getattr(user_config.llm_configs, team_name)
                log_function_exit(self.logger, "get_llm_configuration_for_team", result="success")
                return config
            else:
                # Fallback về cấu hình mặc định
                self.logger.warning(f"Không tìm thấy cấu hình cho team {team_name}, sử dụng mặc định")
                default_configs = self.get_default_llm_configs()
                log_function_exit(self.logger, "get_llm_configuration_for_team", result="fallback")
                return getattr(default_configs, team_name, default_configs.llm_services_default)
        
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy cấu hình LLM cho team: {e}", exc_info=True)
            
            # Fallback về mặc định
            default_configs = self.get_default_llm_configs()
            log_function_exit(self.logger, "get_llm_configuration_for_team", result="error_fallback")
            return default_configs.llm_services_default
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Lấy danh sách các model LLM có sẵn theo từng provider.
        
        Returns:
            Dictionary mapping provider -> list of models
        """
        return {
            "openai": [
                "gpt-4o",
                "gpt-4o-mini", 
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ],
            "azure_openai": [
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-35-turbo"
            ],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-haiku-20240307",
                "claude-3-opus-20240229"
            ],
            "local": [
                "llama2",
                "codellama",
                "mistral"
            ]
        }
    
    def _create_default_user_configuration(self, user_id: str) -> UserConfiguration:
        """Tạo cấu hình mặc định cho người dùng mới"""
        import datetime
        
        now = datetime.datetime.now().isoformat()
        
        return UserConfiguration(
            user_id=user_id,
            display_name=f"User {user_id}",
            llm_configs=self.get_default_llm_configs(),
            preferences={
                "language": "vi",
                "theme": "light",
                "verbose_output": False,
                "auto_confirm": False
            },
            created_at=now,
            updated_at=now
        )
    
    def _validate_llm_configuration(self, config: LLMConfiguration) -> bool:
        """Validate cấu hình LLM"""
        try:
            # Kiểm tra provider hợp lệ
            if not isinstance(config.provider, LLMProvider):
                return False
            
            # Kiểm tra model name
            if not config.model_name or not isinstance(config.model_name, str):
                return False
            
            # Kiểm tra temperature
            if not (0.0 <= config.temperature <= 2.0):
                return False
            
            # Kiểm tra max_tokens
            if not (1 <= config.max_tokens <= 8000):
                return False
            
            # Kiểm tra timeout
            if not (5 <= config.timeout <= 300):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi validate cấu hình LLM: {e}")
            return False
    
    def clear_cache(self):
        """Xóa cache cấu hình"""
        self._config_cache.clear()
        self.logger.info("Đã xóa cache cấu hình")
    
    def list_user_configurations(self) -> List[str]:
        """Lấy danh sách ID của tất cả user có cấu hình"""
        try:
            config_files = list(self.config_dir.glob("*.json"))
            user_ids = [f.stem for f in config_files]
            return user_ids
        except Exception as e:
            self.logger.error(f"Lỗi khi liệt kê cấu hình user: {e}")
            return [] 