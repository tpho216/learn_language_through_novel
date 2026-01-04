"""OpenAI TTS provider implementation."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from .tts_provider import TTSProvider


class OpenAITTSProvider(TTSProvider):
    """TTS provider using OpenAI's TTS API."""

    # Voice mapping: semantic_name -> openai_voice
    VOICE_MAPPING = {
        "narrator": "onyx",
        "teacher": "nova",
        "character": "alloy",
        "male": "onyx",
        "female": "nova",
    }

    # OpenAI TTS models
    MODELS = {
        "standard": "tts-1",
        "hd": "tts-1-hd"
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "standard"):
        """
        Initialize OpenAI TTS provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model quality ("standard" or "hd")
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = self.MODELS.get(model, self.MODELS["standard"])
        self.base_url = "https://api.openai.com/v1/audio/speech"

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: str = "narrator",
        lang: str = "zh",
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Synthesize speech using OpenAI TTS."""
        
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured"
            }
        
        # Map semantic voice to OpenAI voice
        openai_voice = self.VOICE_MAPPING.get(voice, "alloy")
        
        # Adjust speed based on style
        speed = 1.0
        if style == "slow":
            speed = 0.8
        elif style == "natural":
            speed = 1.1
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": text,
                        "voice": openai_voice,
                        "speed": speed,
                        "response_format": "mp3"
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"OpenAI API error: {response.status_code} - {response.text}",
                        "text_length": len(text)
                    }
                
                # Save audio to file
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                # Estimate duration (OpenAI doesn't provide it directly)
                # Rough estimate: ~150 words per minute for normal speech
                words = len(text.split())
                estimated_duration = (words / 150) * 60 / speed
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "model": self.model,
                    "voice": openai_voice,
                    "text_length": len(text),
                    "estimated_duration_seconds": round(estimated_duration, 2),
                    "format": "mp3"
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "OpenAI TTS request timeout",
                "text_length": len(text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "text_length": len(text)
            }

    def get_available_voices(self, lang: Optional[str] = None) -> Dict[str, Any]:
        """Get available voices (OpenAI voices are language-agnostic)."""
        return {
            "narrator": {"voice": "onyx", "description": "Deep, authoritative male voice"},
            "teacher": {"voice": "nova", "description": "Clear, warm female voice"},
            "character": {"voice": "alloy", "description": "Neutral, versatile voice"},
            "male": {"voice": "onyx", "description": "Male voice"},
            "female": {"voice": "nova", "description": "Female voice"},
        }
