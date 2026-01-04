"""Utility to concatenate WAV files with optional silence between segments."""

import wave
from pathlib import Path
from typing import List, Union
import struct


def concatenate_wav_files(
    input_files: List[Union[str, Path]],
    output_file: Union[str, Path],
    silence_ms: int = 0
) -> dict:
    """
    Concatenate multiple WAV files into a single WAV file.
    
    Args:
        input_files: List of input WAV file paths
        output_file: Output WAV file path
        silence_ms: Milliseconds of silence to insert between segments
        
    Returns:
        Dict with metadata about the merged file
    """
    if not input_files:
        raise ValueError("No input files provided")
    
    # Read first file to get audio parameters
    with wave.open(str(input_files[0]), 'rb') as first_wav:
        params = first_wav.getparams()
        sample_rate = params.framerate
        sample_width = params.sampwidth
        n_channels = params.nchannels
    
    # Calculate silence frames
    silence_frames = int(sample_rate * silence_ms / 1000.0)
    silence_bytes = b'\x00' * (silence_frames * sample_width * n_channels)
    
    total_frames = 0
    
    # Create output file and write all input files
    with wave.open(str(output_file), 'wb') as out_wav:
        out_wav.setparams(params)
        
        for i, input_file in enumerate(input_files):
            with wave.open(str(input_file), 'rb') as in_wav:
                # Verify parameters match
                if (in_wav.getframerate() != sample_rate or
                    in_wav.getsampwidth() != sample_width or
                    in_wav.getnchannels() != n_channels):
                    raise ValueError(f"Audio parameters mismatch in {input_file}")
                
                # Copy audio data
                frames = in_wav.readframes(in_wav.getnframes())
                out_wav.writeframes(frames)
                total_frames += in_wav.getnframes()
                
                # Add silence between segments (except after last)
                if i < len(input_files) - 1 and silence_ms > 0:
                    out_wav.writeframes(silence_bytes)
                    total_frames += silence_frames
    
    duration = total_frames / sample_rate
    
    return {
        "output_file": str(output_file),
        "total_segments": len(input_files),
        "duration_seconds": round(duration, 2),
        "sample_rate": sample_rate,
        "channels": n_channels,
        "sample_width": sample_width
    }
