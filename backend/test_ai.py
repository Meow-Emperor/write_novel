#!/usr/bin/env python3
"""Test AI services including Ollama integration."""
from __future__ import annotations

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import AIService

async def test_ai_providers():
    """Test different AI providers."""
    
    # Test OpenAI (mock if no key)
    print("Testing OpenAI provider...")
    openai_service = AIService(provider="openai", model_name="gpt-3.5-turbo")
    try:
        result = await openai_service.generate(
            prompt="Write a short story opening",
            context={},
            max_tokens=100
        )
        print(f"OpenAI result: {result['content'][:100]}...")
    except Exception as e:
        print(f"OpenAI error: {e}")
    
    # Test Anthropic (mock if no key)
    print("\nTesting Anthropic provider...")
    anthropic_service = AIService(provider="anthropic", model_name="claude-3-sonnet-20240229")
    try:
        result = await anthropic_service.generate(
            prompt="Write a short story opening",
            context={},
            max_tokens=100
        )
        print(f"Anthropic result: {result['content'][:100]}...")
    except Exception as e:
        print(f"Anthropic error: {e}")
    
    # Test Ollama
    print("\nTesting Ollama provider...")
    ollama_service = AIService(provider="ollama", model_name="llama2")
    try:
        result = await ollama_service.generate(
            prompt="Write a short story opening",
            context={},
            max_tokens=100
        )
        print(f"Ollama result: {result['content'][:100]}...")
    except Exception as e:
        print(f"Ollama error: {e}")
    
    # Test text splitting
    print("\nTesting text splitting...")
    long_text = "This is a very long text that should be split into multiple chunks for processing. " * 20
    chunks = openai_service.split_text(long_text, chunk_size=200, chunk_overlap=50)
    print(f"Text split into {len(chunks)} chunks")
    print(f"First chunk: {chunks[0][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_ai_providers())