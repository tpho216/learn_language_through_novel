"""Piper TTS provider implementation."""

import wave
from pathlib import Path
from typing import Dict, Any, Optional
from piper.voice import PiperVoice

from .tts_provider import TTSProvider


class PiperTTSProvider(TTSProvider):
    """TTS provider using Piper (local neural TTS) via Python API."""

    # Voice mapping: use appropriate voices per language
    VOICE_MODELS = {
        # Chinese voices
        "zh_narrator": "zh_CN-huayan-medium",
        "zh_teacher": "zh_CN-huayan-medium", 
        "zh_character": "zh_CN-huayan-medium",
        
        # Vietnamese voices
        "vi_narrator": "vi_VN-vais1000-medium",
        "vi_teacher": "vi_VN-vais1000-medium",
        "vi_character": "vi_VN-vivos-x_low",
        
        # English voices
        "en_narrator": "en_US-lessac-medium",
        "en_teacher": "en_US-amy-medium",
        "en_character": "en_US-ryan-medium",
    }

    def __init__(self, piper_binary: str = "piper", models_dir: Optional[Path] = None):
        """
        Initialize Piper TTS provider.
        
        Args:
            piper_binary: Unused (kept for compatibility)
            models_dir: Directory containing piper models (defaults to ~/.local/share/piper-voices)
        """
        if models_dir is None:
            # Try standard locations
            models_dir = Path.home() / ".local" / "share" / "piper-voices"
            if not models_dir.exists():
                models_dir = Path.cwd()
        self.models_dir = models_dir

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: str = "narrator",
        lang: str = "zh",
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Synthesize speech using Piper Python API."""
        
        # Construct voice key
        voice_key = f"{lang}_{voice}"
        model_name = self.VOICE_MODELS.get(voice_key, "en_US-lessac-medium")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Construct full path to model file - check multiple locations
            model_path = self.models_dir / f"{model_name}.onnx"
            
            if not model_path.exists():
                # Try current directory as fallback
                model_path = Path.cwd() / f"{model_name}.onnx"
            
            if not model_path.exists():
                error_msg = (
                    f"Voice model not found: {model_name}.onnx\n"
                    f"Searched in: {self.models_dir} and {Path.cwd()}\n"
                    f"Download with:\n"
                    f"  mkdir -p ~/.local/share/piper-voices\n"
                    f"  cd ~/.local/share/piper-voices\n"
                    f"  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/.../.../{model_name}.onnx\n"
                    f"  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/.../.../{model_name}.onnx.json"
                )
                return {
                    "success": False,
                    "error": error_msg,
                    "text_length": len(text)
                }
            
            # Load voice with full path
            voice = PiperVoice.load(str(model_path), use_cuda=False)
            
            # Synthesize to WAV file
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(voice.config.sample_rate)
                
                # Synthesize returns an iterable of audio chunks
                for audio_chunk in voice.synthesize(text):
                    wav_file.writeframes(audio_chunk.audio_int16_bytes)
            
            # Extract audio metadata
            metadata = self._get_audio_metadata(output_path)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "model": model_name,
                "text_length": len(text),
                **metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Piper error: {str(e)}",
                "text_length": len(text)
            }

    def _get_audio_metadata(self, audio_path: Path) -> Dict[str, Any]:
        """Extract metadata from generated audio file."""
        try:
            with wave.open(str(audio_path), 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                
                return {
                    "duration_seconds": round(duration, 2),
                    "sample_rate": rate,
                    "channels": wf.getnchannels(),
                    "sample_width": wf.getsampwidth()
                }
        except Exception:
            return {
                "duration_seconds": 0,
                "sample_rate": 0,
                "channels": 0,
                "sample_width": 0
            }

    def get_available_voices(self, lang: Optional[str] = None) -> Dict[str, Any]:
        """Get available voices."""
        voices = {}
        for key, model in self.VOICE_MODELS.items():
            voice_lang, voice_name = key.split("_", 1)
            if lang is None or voice_lang == lang:
                voices[key] = {
                    "lang": voice_lang,
                    "voice": voice_name,
                    "model": model
                }
        return voices
