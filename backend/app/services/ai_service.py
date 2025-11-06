from typing import Dict, Any, Optional, List
import hashlib
import json

import httpx

from ..core.config import settings

# Import optional dependencies
try:
    import redis  # type: ignore
except ImportError:
    redis = None

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
except ImportError:
    RecursiveCharacterTextSplitter = None

if redis is not None and settings.AI_CACHE_ENABLED:
    try:
        _redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        # Proactively verify connectivity; if it fails, disable caching gracefully
        try:
            _redis_client.ping()
        except Exception:  # noqa: BLE001
            _redis_client = None
    except Exception:  # noqa: BLE001
        _redis_client = None
else:
    _redis_client = None


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

    async def generate(self, prompt: str, context: Dict[str, Any], max_tokens: int = 2000, temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate content using AI based on provider"""
        full_prompt = self.build_context_prompt(context, prompt)
        # Development-friendly fallback: if running in DEBUG and no valid key/base_url provided,
        # return a deterministic mock response so that frontend flows remain testable without errors.
        # This does NOT run in production (DEBUG=False) and does not replace real providers when keys exist.
        try:
            from ..core.config import settings as _settings
        except Exception:
            _settings = settings

        def _is_placeholder(val: Optional[str]) -> bool:
            if not val:
                return True
            return val.strip().lower().startswith("your-")

        if getattr(_settings, "DEBUG", False):
            if self.provider in ("openai", "anthropic") and _is_placeholder(self.api_key):
                # Return mock content with context echo for visibility
                return {
                    "content": f"[DEV-MOCK:{self.provider}]\nModel: {self.model_name}\nPrompt: {prompt[:160]}...\n(Provide real API key to generate actual content.)",
                    "tokens_used": 0,
                    "model": self.model_name,
                }
            if self.provider not in ("openai", "anthropic") and not self.base_url:
                return {
                    "content": f"[DEV-MOCK:custom]\nNo base_url provided. Echo prompt preview: {prompt[:160]}...",
                    "tokens_used": 0,
                    "model": self.model_name,
                }
        cache_key = None
        if _redis_client:
            cache_input = f"{self.provider}:{self.model_name}:{prompt}".encode("utf-8")
            cache_key = hashlib.md5(cache_input).hexdigest()
            try:
                cached_value = _redis_client.get(cache_key)
            except Exception:  # noqa: BLE001
                cached_value = None
                # Disable cache for this process to avoid repeated connection errors
                try:
                    _redis_client.close()
                except Exception:
                    pass
                globals().update({"_redis_client": None})
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    pass

        if self.provider == "openai":
            result = await self._generate_openai(full_prompt, max_tokens, temperature)
        elif self.provider == "anthropic":
            result = await self._generate_anthropic(full_prompt, max_tokens, temperature)
        elif self.provider == "ollama":
            result = await self._generate_ollama(full_prompt, max_tokens, temperature)
        else:
            result = await self._generate_custom(full_prompt, max_tokens, temperature)

        if _redis_client and cache_key:
            try:
                _redis_client.setex(cache_key, 86400, json.dumps(result))
            except Exception:  # noqa: BLE001
                pass

        return result

    async def _generate_openai(self, prompt: str, max_tokens: int, temperature: Optional[float]) -> Dict[str, Any]:
        """Generate using OpenAI API"""
        try:
            try:
                from openai import AsyncOpenAI  # type: ignore
            except ImportError as e:
                raise Exception("OpenAI SDK is not installed. Set provider to 'custom' or install openai.") from e

            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature if temperature is not None else 0.7
            )
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.model_name
            }
        except Exception as e:
            raise Exception(f"OpenAI API error while generating content: {str(e)}") from e

    async def _generate_anthropic(self, prompt: str, max_tokens: int, temperature: Optional[float]) -> Dict[str, Any]:
        """Generate using Anthropic API"""
        try:
            try:
                from anthropic import AsyncAnthropic  # type: ignore
            except ImportError as e:
                raise Exception("Anthropic SDK is not installed. Set provider to 'custom' or install anthropic.") from e

            client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
            response = await client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature if temperature is not None else 0.7
            )
            return {
                "content": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.model_name
            }
        except Exception as e:
            raise Exception(f"Anthropic API error while generating content: {str(e)}") from e

    async def _generate_custom(self, prompt: str, max_tokens: int, temperature: Optional[float]) -> Dict[str, Any]:
        """Generate using custom API endpoint"""
        if not self.base_url:
            raise Exception("Custom provider requires base_url")

        try:
            # Smart URL handling: support both chat/completions and completions endpoints
            base = self.base_url.rstrip('/')
            if base.endswith('/chat/completions'):
                api_url = base
                use_chat = True
            elif base.endswith('/completions'):
                api_url = base
                use_chat = False
            else:
                api_url = f"{base}/v1/chat/completions"
                use_chat = True

            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": self.model_name,
                    "max_tokens": max_tokens,
                    "temperature": temperature if temperature is not None else 0.7,
                }
                if use_chat:
                    payload["messages"] = [{"role": "user", "content": prompt}]
                else:
                    payload["prompt"] = prompt

                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

                response = await client.post(api_url, json=payload, headers=headers)

                # Check for HTTP errors
                if response.status_code != 200:
                    error_detail = f"HTTP {response.status_code}: {response.text}"
                    raise Exception(error_detail)

                data = response.json()

                def _extract_content(d: dict) -> str | None:
                    choices = d.get("choices") or []
                    if not choices:
                        return None
                    c0 = choices[0]
                    if not isinstance(c0, dict):
                        return None
                    # Chat style
                    msg = c0.get("message")
                    if isinstance(msg, dict):
                        mc = msg.get("content")
                        if isinstance(mc, str):
                            return mc
                        if isinstance(mc, list):
                            # e.g. [{type: 'text', text: '...'}]
                            texts = []
                            for item in mc:
                                if isinstance(item, dict) and "text" in item:
                                    texts.append(str(item["text"]))
                                elif isinstance(item, str):
                                    texts.append(item)
                            if texts:
                                return "\n".join(texts)
                    # Text completions style
                    if isinstance(c0.get("text"), str):
                        return c0["text"]
                    return None

                content = _extract_content(data)

                # If no choices/content, try alternate endpoint once
                if not content:
                    alt_api = None
                    alt_payload = None
                    if use_chat:
                        alt_api = f"{base}/v1/completions"
                        alt_payload = {
                            "model": self.model_name,
                            "prompt": prompt,
                            "max_tokens": max_tokens,
                            "temperature": temperature if temperature is not None else 0.7,
                        }
                    else:
                        alt_api = f"{base}/v1/chat/completions"
                        alt_payload = {
                            "model": self.model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": max_tokens,
                            "temperature": temperature if temperature is not None else 0.7,
                        }
                    resp2 = await client.post(alt_api, json=alt_payload, headers=headers)
                    if resp2.status_code == 200:
                        data2 = resp2.json()
                        content = _extract_content(data2)
                        if content:
                            data = data2

                if not content:
                    raise Exception(f"Invalid API response structure or empty choices: {data}")

                usage = data.get("usage", {})
                tokens_used = usage.get("total_tokens") or (
                    (usage.get("prompt_tokens") or 0) + (usage.get("completion_tokens") or 0)
                )

                return {"content": content, "tokens_used": tokens_used or 0, "model": self.model_name}
        except httpx.TimeoutException:
            raise Exception("API request timeout (60s)")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Custom API error while generating content: {str(e)}") from e

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
