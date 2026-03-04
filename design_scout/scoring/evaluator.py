"""AI scoring evaluator"""

import base64
import json
import os
from pathlib import Path
from typing import Dict, Optional, List
import httpx

from .prompts import SCORING_PROMPT, SCORING_SYSTEM_PROMPT


async def evaluate(screenshot_path: str) -> Optional[Dict]:
    """Evaluate a single screenshot using AI vision.
    
    Args:
        screenshot_path: Path to screenshot image
        
    Returns:
        Dict with score breakdown and comment, or None if failed
    """
    # Check for API keys
    api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Warning: No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return mock_evaluation()
    
    # Use OpenAI if available, otherwise Anthropic
    if os.environ.get('OPENAI_API_KEY'):
        return await evaluate_openai(screenshot_path)
    else:
        return await evaluate_anthropic(screenshot_path)


async def evaluate_openai(screenshot_path: str) -> Optional[Dict]:
    """Evaluate using OpenAI Vision API."""
    api_key = os.environ.get('OPENAI_API_KEY')
    
    # Read and encode image
    image_data = encode_image(screenshot_path)
    if not image_data:
        return None
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": SCORING_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": SCORING_PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500
                },
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON response
            return parse_score_response(content)
            
        except Exception as e:
            print(f"OpenAI evaluation error: {e}")
            return None


async def evaluate_anthropic(screenshot_path: str) -> Optional[Dict]:
    """Evaluate using Anthropic Claude Vision API."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    # Read and encode image
    image_data = encode_image(screenshot_path)
    if not image_data:
        return None
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "system": SCORING_SYSTEM_PROMPT,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_data
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": SCORING_PROMPT
                                }
                            ]
                        }
                    ]
                },
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['content'][0]['text']
            
            return parse_score_response(content)
            
        except Exception as e:
            print(f"Anthropic evaluation error: {e}")
            return None


def encode_image(image_path: str) -> Optional[str]:
    """Encode image to base64."""
    try:
        path = Path(image_path)
        if not path.exists():
            print(f"Image not found: {image_path}")
            return None
        
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def parse_score_response(content: str) -> Optional[Dict]:
    """Parse AI response to extract scores."""
    try:
        # Try to extract JSON from response
        # Handle case where response might have markdown code blocks
        content = content.strip()
        if content.startswith('```'):
            # Remove markdown code blocks
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1])
        
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"Failed to parse score response: {content[:100]}...")
        return None


def mock_evaluation() -> Dict:
    """Return mock evaluation when no API key is available."""
    return {
        "visual_appeal": 15,
        "layout": 15,
        "modernity": 15,
        "professionalism": 15,
        "total_score": 60,
        "comment": "Mock evaluation - set OPENAI_API_KEY or ANTHROPIC_API_KEY for real scoring"
    }


async def evaluate_batch(screenshot_paths: List[str]) -> Dict[str, Optional[Dict]]:
    """Evaluate multiple screenshots.
    
    Args:
        screenshot_paths: List of paths to screenshot images
        
    Returns:
        Dict mapping path to evaluation result
    """
    import asyncio
    
    async def evaluate_single(path: str) -> tuple:
        result = await evaluate(path)
        return (path, result)
    
    tasks = [evaluate_single(path) for path in screenshot_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    output = {}
    for result in results:
        if isinstance(result, tuple):
            path, evaluation = result
            output[path] = evaluation
    
    return output
