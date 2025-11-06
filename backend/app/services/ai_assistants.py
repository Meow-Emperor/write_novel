"""
AI Assistant Role System

专业化 AI 助手角色系统，参考 Arboris 的设计理念：
- Conceptualizer: 概念化助手，头脑风暴
- Blueplanner: 蓝图规划助手
- Outliner: 大纲补充助手
- Novelist: 小说写作助手
- Extractor: 内容压缩助手
- Evaluator: 质量评估助手
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..services.ai_service import AIService


class BaseAssistant(ABC):
    """AI助手基类"""

    role: str = "base"
    name: str = "基础助手"
    description: str = "AI助手基类"
    system_prompt: str = ""

    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "gpt-4",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature
        self.ai_service = AIService(
            provider=provider,
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
        )

    @abstractmethod
    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        """构建提示词"""
        pass

    async def process(
        self, context: Dict[str, Any], user_input: str, max_tokens: int = 2000
    ) -> str:
        """处理用户输入，生成响应"""
        prompt = self.build_prompt(context, user_input)
        result = await self.ai_service.generate(
            prompt=prompt,
            context=context,
            max_tokens=max_tokens,
            temperature=self.temperature,
        )
        return result.get("content", "")

    def get_info(self) -> Dict[str, str]:
        """获取助手信息"""
        return {
            "role": self.role,
            "name": self.name,
            "description": self.description,
        }


# ============= 6种专业助手 =============


class ConceptualizerAssistant(BaseAssistant):
    """概念化助手：头脑风暴，收集创意"""

    role = "conceptualizer"
    name = "概念化助手"
    description = "擅长头脑风暴和创意收集，帮助你从模糊的想法中提炼核心概念"

    system_prompt = """你是一个创意概念化助手，擅长：
1. 头脑风暴 - 从用户的模糊想法中激发更多创意
2. 概念提炼 - 将零散的想法整合为清晰的概念
3. 主题探索 - 挖掘概念背后的深层主题
4. 可能性拓展 - 探索不同的创作方向

你的回复应该：
- 提出启发性问题
- 提供多个创意方向
- 保持开放和探索性
- 避免过早限制创作空间
"""

    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        novel_info = context.get("novel", {})
        return f"""{self.system_prompt}

## 小说信息
标题: {novel_info.get('title', '未命名')}
类型: {novel_info.get('genre', '未指定')}
简介: {novel_info.get('description', '暂无')}

## 用户输入
{user_input}

请围绕用户的想法进行头脑风暴，提供3-5个不同的创意方向，每个方向包含：
1. 核心概念
2. 可能的情节线索
3. 需要进一步探索的问题

以清晰的结构化格式输出。"""


class BlueplannerAssistant(BaseAssistant):
    """蓝图规划助手：结构化世界观和大纲"""

    role = "blueplanner"
    name = "蓝图规划助手"
    description = "将创意概念转化为结构化的蓝图，包括世界观设定、角色体系、情节框架"

    system_prompt = """你是一个蓝图规划助手，擅长：
1. 结构化思考 - 将创意组织成清晰的框架
2. 世界观设计 - 构建完整自洽的世界设定
3. 逻辑检查 - 确保设定之间的一致性
4. 框架搭建 - 为后续写作提供坚实基础

你的回复应该：
- 结构化、系统化
- 注重内在逻辑
- 考虑可扩展性
- 提供实用的蓝图
"""

    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        novel_info = context.get("novel", {})
        characters = context.get("characters", [])
        world = context.get("world", {})

        return f"""{self.system_prompt}

## 当前状态
小说: {novel_info.get('title', '未命名')}
类型: {novel_info.get('genre', '未指定')}
已有角色: {len(characters)}个
世界观完整度: {'已设定' if world else '待设定'}

## 规划目标
{user_input}

请提供一个结构化的蓝图，包含：
1. 世界观要素（时代背景、世界规则）
2. 角色体系（主要角色及其关系）
3. 情节框架（主线、支线结构）
4. 关键节点（重要转折点）

以JSON或结构化Markdown格式输出，便于后续使用。"""


class OutlinerAssistant(BaseAssistant):
    """大纲助手：补充和完善章节大纲"""

    role = "outliner"
    name = "大纲助手"
    description = "专注于章节大纲的规划和细化，确保情节流畅和节奏合理"

    system_prompt = """你是一个大纲规划助手，擅长：
1. 章节规划 - 合理划分章节，控制节奏
2. 情节承接 - 确保前后章节衔接自然
3. 节奏把控 - 平衡张弛有度的叙事节奏
4. 伏笔设计 - 布置伏笔和回收线索

你的回复应该：
- 逻辑清晰
- 注重承转
- 考虑节奏
- 标注关键点
"""

    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        novel_info = context.get("novel", {})
        plots = context.get("plots", [])
        characters = context.get("characters", [])

        return f"""{self.system_prompt}

## 小说信息
标题: {novel_info.get('title', '未命名')}
类型: {novel_info.get('genre', '未指定')}
主线情节: {len(plots)}条
主要角色: {', '.join([c.get('name', '') for c in characters[:5]])}

## 大纲需求
{user_input}

请提供章节大纲，包含：
1. 章节标题
2. 章节概要（2-3句话）
3. 关键情节点
4. 角色发展
5. 与前后章节的关联

按清晰的结构输出。"""


class NovelistAssistant(BaseAssistant):
    """小说家助手：生成章节内容，提供多个版本"""

    role = "novelist"
    name = "小说家助手"
    description = "专业的内容写作助手，能够生成高质量的章节内容，并提供多个版本供选择"

    system_prompt = """你是一个专业小说家助手，擅长：
1. 场景描写 - 生动具体的环境和氛围营造
2. 对话写作 - 自然流畅的人物对话
3. 心理刻画 - 细腻的人物内心活动
4. 情节推进 - 紧凑有力的故事发展

写作原则：
- 展示而非告知（Show, don't tell）
- 细节生动，避免空泛
- 对话符合人物性格
- 保持叙事节奏
"""

    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        novel_info = context.get("novel", {})
        characters = context.get("characters", [])

        character_info = "\n".join(
            [
                f"- {c.get('name', '未命名')}: {c.get('personality', '')}"
                for c in characters[:5]
            ]
        )

        return f"""{self.system_prompt}

## 小说设定
标题: {novel_info.get('title', '未命名')}
类型: {novel_info.get('genre', '未指定')}
基调: {novel_info.get('description', '')}

## 主要角色
{character_info}

## 写作要求
{user_input}

请根据以上信息撰写章节内容。注意：
1. 保持风格与小说类型一致
2. 角色言行符合设定
3. 情节推进自然流畅
4. 细节描写生动具体

字数约2000-3000字。"""

    async def process_multiple_versions(
        self, context: Dict[str, Any], user_input: str, num_versions: int = 2
    ) -> List[str]:
        """生成多个版本"""
        versions = []
        styles = ["detailed", "concise"]  # 可以有不同的风格

        for i in range(num_versions):
            style = styles[i % len(styles)]
            modified_input = f"{user_input}\n\n[风格要求: {style}]"
            version = await self.process(context, modified_input, max_tokens=3000)
            versions.append(version)

        return versions


class ExtractorAssistant(BaseAssistant):
    """压缩助手：压缩章节内容为摘要，优化上下文传递"""

    role = "extractor"
    name = "内容压缩助手"
    description = "将章节内容压缩为简洁的摘要，保留关键信息，优化AI上下文使用"

    system_prompt = """你是一个内容压缩助手，擅长：
1. 关键信息提取 - 识别核心情节和重要细节
2. 简洁总结 - 用最少的文字表达完整意思
3. 结构化输出 - 便于后续使用的格式
4. 保真度控制 - 不遗漏关键信息

压缩原则：
- 保留情节关键点
- 记录角色状态变化
- 标注伏笔和线索
- 省略冗余描写
"""

    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        return f"""{self.system_prompt}

## 需要压缩的内容
{user_input}

请将以上内容压缩为简洁的摘要，包含：
1. 核心情节（2-3句话）
2. 角色状态变化
3. 重要对话或决定
4. 伏笔和待解决问题

用200-300字概括。"""


class EvaluatorAssistant(BaseAssistant):
    """评估助手：分析内容质量，提供改进建议"""

    role = "evaluator"
    name = "质量评估助手"
    description = "客观评估内容质量，指出优缺点，提供具体的改进建议"

    system_prompt = """你是一个文学评论和质量评估助手，擅长：
1. 客观分析 - 从多个维度评估内容
2. 优缺点识别 - 既肯定优点也指出问题
3. 具体建议 - 提供可操作的改进方案
4. 鼓励创作 - 保持建设性和鼓励性

评估维度：
- 情节完整性和逻辑性
- 角色塑造和一致性
- 语言质量和文笔
- 节奏把控
- 读者体验
"""

    def build_prompt(self, context: Dict[str, Any], user_input: str) -> str:
        return f"""{self.system_prompt}

## 需要评估的内容
{user_input}

请从以下维度进行评估：

1. **总体评分** (1-10分)
   - 情节: ?/10
   - 角色: ?/10
   - 文笔: ?/10
   - 节奏: ?/10

2. **优点** (2-3点)
   列出内容的亮点

3. **需要改进的地方** (2-3点)
   指出具体问题

4. **改进建议** (具体可行)
   针对每个问题提供解决方案

请保持客观、具体、建设性。"""


# ============= 助手工厂 =============


class AssistantFactory:
    """AI助手工厂类"""

    _assistants = {
        "conceptualizer": ConceptualizerAssistant,
        "blueplanner": BlueplannerAssistant,
        "outliner": OutlinerAssistant,
        "novelist": NovelistAssistant,
        "extractor": ExtractorAssistant,
        "evaluator": EvaluatorAssistant,
    }

    @classmethod
    def create(
        cls,
        role: str,
        provider: str = "openai",
        model_name: str = "gpt-4",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ) -> BaseAssistant:
        """创建指定角色的助手"""
        assistant_class = cls._assistants.get(role)
        if not assistant_class:
            raise ValueError(f"Unknown assistant role: {role}")

        return assistant_class(
            provider=provider,
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
        )

    @classmethod
    def list_assistants(cls) -> List[Dict[str, str]]:
        """列出所有可用的助手"""
        assistants = []
        for role, assistant_class in cls._assistants.items():
            instance = assistant_class()
            assistants.append(instance.get_info())
        return assistants
