"""
应用配置模块
从环境变量加载应用配置，包括数据库连接、API密钥、CORS设置等
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类 - 从环境变量加载配置"""

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ai_novel.db"  # 数据库连接URL，默认使用SQLite

    # AI服务API密钥
    OPENAI_API_KEY: str = ""  # OpenAI API密钥
    ANTHROPIC_API_KEY: str = ""  # Anthropic API密钥
    CUSTOM_API_URL: str = ""  # 自定义API端点URL
    CUSTOM_API_KEY: str = ""  # 自定义API密钥

    # 跨域资源共享(CORS)配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]  # 允许的前端域名

    # 应用元信息
    APP_NAME: str = "AI Novel Platform"  # 应用名称
    DEBUG: bool = True  # 调试模式开关

    # Pydantic配置
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[2] / ".env",  # 根目录的.env文件
            Path(__file__).resolve().parents[1] / ".env",  # app目录的.env文件
        ),
        env_file_encoding="utf-8",  # 环境文件编码
        case_sensitive=True,  # 环境变量名大小写敏感
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, value: List[str] | str) -> List[str]:
        """
        验证和转换ALLOWED_ORIGINS字段
        支持逗号分隔的字符串格式和列表格式
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS源列表访问器 - 为了向后兼容旧代码"""
        return list(self.ALLOWED_ORIGINS)


# 创建全局配置实例
settings = Settings()
