from typing import Dict, Any, Optional
import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from ..core.config import settings


class AIService:
    def __init__(
        self,
        provider: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4"
    ):
        self.provider = provider
        self.base_url = base_url
        self.api_key = api_key or self._get_default_api_key(provider)
        self.model_name = model_name

    def _get_default_api_key(self, provider: str) -> str:
        if provider == "openai":
            return settings.OPENAI_API_KEY
        elif provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        return ""

    async def generate(self, prompt: str, context: Dict[str, Any], max_tokens: int = 2000) -> Dict[str, Any]:
        """Generate content using AI based on provider"""
        full_prompt = self.build_context_prompt(context, prompt)

        if self.provider == "openai":
            return await self._generate_openai(full_prompt, max_tokens)
        elif self.provider == "anthropic":
            return await self._generate_anthropic(full_prompt, max_tokens)
        else:
            return await self._generate_custom(full_prompt, max_tokens)

    async def _generate_openai(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using OpenAI API"""
        try:
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.model_name
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _generate_anthropic(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using Anthropic API"""
        try:
            client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
            response = await client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "content": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.model_name
            }
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def _generate_custom(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using custom API endpoint"""
        if not self.base_url:
            raise Exception("Custom provider requires base_url")

        try:
            # Smart URL handling: if base_url already contains the endpoint, use it directly
            if self.base_url.endswith('/chat/completions') or self.base_url.endswith('/completions'):
                api_url = self.base_url
            else:
                # Otherwise append the standard OpenAI endpoint
                api_url = f"{self.base_url.rstrip('/')}/v1/chat/completions"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )

                # Check for HTTP errors
                if response.status_code != 200:
                    error_detail = f"HTTP {response.status_code}: {response.text}"
                    raise Exception(error_detail)

                data = response.json()

                # Validate response structure
                if "choices" not in data or len(data["choices"]) == 0:
                    raise Exception(f"Invalid API response structure: {data}")

                return {
                    "content": data["choices"][0]["message"]["content"],
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "model": self.model_name
                }
        except httpx.TimeoutException:
            raise Exception("API request timeout (60s)")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Custom API error: {str(e)}")

    def build_context_prompt(self, context: Dict[str, Any], user_prompt: str) -> str:
        """Build context-aware prompt"""
        context_parts = []

        # Add novel info
        if "novel" in context:
            novel = context["novel"]
            context_parts.append(f"小说信息：\n标题：{novel.get('title')}\n类型：{novel.get('genre')}\n简介：{novel.get('synopsis')}\n")

        # Add characters
        if "characters" in context and context["characters"]:
            chars = "\n".join([f"- {c.get('name')}（{c.get('role')}）：{c.get('background', '')}"
                              for c in context["characters"]])
            context_parts.append(f"角色信息：\n{chars}\n")

        # Add world settings
        if "world" in context and context["world"]:
            world = context["world"]
            context_parts.append(f"世界观：\n时代：{world.get('era')}\n规则：{world.get('rules')}\n")

        # Add plot
        if "plot" in context and context["plot"]:
            plot = context["plot"]
            context_parts.append(f"情节大纲：\n{plot.get('key_events')}\n")

        # Add previous content
        if "previous_content" in context:
            context_parts.append(f"前文内容：\n{context['previous_content']}\n")

        full_context = "\n".join(context_parts)
        return f"{full_context}\n用户需求：{user_prompt}\n\n请基于以上信息生成内容："
