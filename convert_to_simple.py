#!/usr/bin/env python3
"""
Convert to ultra-simple SSML: one voice, alternating Chinese/Vietnamese plain text.
"""
import re
import sys
from pathlib import Path

def convert_to_simple(input_file: str, voice_name: str = "de-DE-SeraphinaMultilingualNeural"):
    """Extract text and create simple SSML."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all text from prosody tags (actual content)
    texts = []
    prosody_pattern = r'<prosody[^>]*>(.*?)</prosody>'
    matches = re.findall(prosody_pattern, content, re.DOTALL)
    
    for match in matches:
        text = match.strip()
        if text:
            texts.append(text)
    
    # Combine into simple paragraphs (ZH+VI pairs)
    combined_lines = []
    for i in range(0, len(texts), 2):
        zh_line = texts[i] if i < len(texts) else ""
        vi_line = texts[i+1] if i+1 < len(texts) else ""
        
        if zh_line and vi_line:
            combined_lines.append(f"{zh_line}\n{vi_line}")
        elif zh_line:
            combined_lines.append(zh_line)
        elif vi_line:
            combined_lines.append(vi_line)
    
    # Build ultra-simple SSML
    text_content = "\n\n".join(combined_lines)
    
    output = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="de-DE">
<voice name="{voice_name}">
{text_content}
</voice>
</speak>'''
    
    # Write output
    output_file = input_file.replace('.ssml', '_simple.ssml')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✓ Created: {output_file}")
    print(f"  Voice: {voice_name}")
    print(f"  Text pairs: {len(combined_lines)}")
    print(f"  Size: {len(output)} bytes")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_to_simple.py <input.ssml> [voice_name]")
        print("\nRecommended voices:")
        print("  - de-DE-SeraphinaMultilingualNeural (default)")
        print("  - en-US-AvaMultilingualNeural")
        print("  - en-US-AndrewMultilingualNeural")
        sys.exit(1)
    
    input_file = sys.argv[1]
    voice_name = sys.argv[2] if len(sys.argv) > 2 else "de-DE-SeraphinaMultilingualNeural"
    
    convert_to_simple(input_file, voice_name)
