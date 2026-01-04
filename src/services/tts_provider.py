"""Abstract TTS provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: str = "default",
        lang: str = "zh",
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Path where audio file should be saved
            voice: Voice identifier (provider-specific)
            lang: Language code (zh, vi, en, etc.)
            style: Speaking style (neutral, slow, explanatory, natural)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with synthesis metadata (duration, sample_rate, etc.)
        """
        pass

    @abstractmethod
    def get_available_voices(self, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available voices for this provider.
        
        Args:
            lang: Optional language filter
            
        Returns:
            Dict mapping voice names to voice metadata
        """
        pass
