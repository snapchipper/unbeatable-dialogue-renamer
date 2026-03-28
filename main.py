#!/usr/bin/env python3
"""
Audio File Organizer for Dialogue
Organizes audio files by chapter and node, renaming them based on dialogue metadata.
No external dependencies required - uses only Python stdlib.
"""

import json
import shutil
from pathlib import Path


def sanitize_filename(text, max_length=10):
    """Remove spaces and punctuation from text, limit to max_length."""
    # Remove all non-alphanumeric characters
    cleaned = ''.join(c for c in text if c.isalnum() or c.isspace())
    # Remove spaces
    cleaned = cleaned.replace(' ', '')
    # Limit to max_length
    return cleaned[:max_length]


def load_all_dialogues(base_dir):
    """Load all dialogue JSON files and return a hash -> (chapter, node, speaker, line, order) mapping."""
    dialogue_map = {}
    
    json_files = [
        'C0Dialogue.json', 'C1Dialogue.json', 'C2Dialogue.json',
        'C3Dialogue.json', 'C4Dialogue.json'
    ]
    
    for json_filename in json_files:
        json_path = base_dir / json_filename
        if not json_path.exists():
            continue
        
        chapter = json_filename.replace('Dialogue.json', '')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                dialogue_data = json.load(f)
            
            # dialogue_data structure: {node_name: {hash: {speaker, line, order}}}
            for node_name, entries in dialogue_data.items():
                for hash_key, entry in entries.items():
                    dialogue_map[hash_key] = {
                        'chapter': chapter,
                        'node': node_name,
                        'speaker': entry.get('speaker', 'Unknown'),
                        'line': entry.get('line', ''),
                        'order': entry.get('order', 0)
                    }
        except Exception as e:
            print(f"Warning: Could not load {json_filename}: {e}")
    
    return dialogue_map


def get_audio_files(audio_dir):
    """Get all audio files from the audio directory."""
    if not audio_dir.exists():
        return []
    
    # Look for common audio formats
    audio_extensions = {'.wav', '.mp3', '.ogg', '.flac', '.aac', '.m4a'}
    audio_files = []
    
    for file_path in audio_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            audio_files.append(file_path)
    
    return sorted(audio_files)


def organize_audio_files(base_dir):
    """Main function to organize audio files."""
    audio_dir = base_dir / 'audio'
    
    if not audio_dir.exists():
        print(f"Error: audio folder not found at {audio_dir}")
        return
    
    # Get all audio files
    audio_files = get_audio_files(audio_dir)
    
    if not audio_files:
        print("⚠️  WARNING: No audio files found in the audio folder!")
        return
    
    print(f"Found {len(audio_files)} audio file(s) to process")
    
    # Load all dialogues
    dialogue_map = load_all_dialogues(base_dir)
    print(f"Loaded {len(dialogue_map)} dialogue entries")
    
    # Create Unused folder
    unused_dir = audio_dir / 'Unused'
    unused_dir.mkdir(exist_ok=True)
    
    processed = 0
    unmatched = 0
    
    # Process each audio file
    for audio_file in audio_files:
        # Extract hash from filename (without extension)
        file_hash = audio_file.stem
        
        if file_hash in dialogue_map:
            entry = dialogue_map[file_hash]
            
            # Use node name with order prefix for folder
            node_name = entry['node']
            
            # Create chapter and node directories
            chapter_dir = audio_dir / entry['chapter'] / node_name
            chapter_dir.mkdir(parents=True, exist_ok=True)
            
            # Format new filename
            order_str = f"{entry['order']:02d}"  # Double digit order
            speaker = entry['speaker']
            line_cleaned = sanitize_filename(entry['line'])
            
            new_filename = f"{order_str}_{speaker}_{line_cleaned}{audio_file.suffix}"
            new_path = chapter_dir / new_filename
            
            # Move and rename file
            try:
                shutil.move(str(audio_file), str(new_path))
                print(f"✓ {audio_file.name} → {entry['chapter']}/{node_name}/{new_filename}")
                processed += 1
            except Exception as e:
                print(f"✗ Failed to move {audio_file.name}: {e}")
        else:
            # Move to Unused
            new_path = unused_dir / audio_file.name
            try:
                shutil.move(str(audio_file), str(new_path))
                print(f"⊘ {audio_file.name} → Unused/ (not found in dialogue files)")
                unmatched += 1
            except Exception as e:
                print(f"✗ Failed to move {audio_file.name} to Unused: {e}")
    
    print(f"\n{'='*60}")
    print(f"Processed: {processed} files organized")
    print(f"Unmatched: {unmatched} files moved to Unused")
    print(f"Total: {processed + unmatched} files processed")


def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    
    print("Audio File Organizer")
    print("=" * 60)
    print(f"Working directory: {script_dir}\n")
    
    organize_audio_files(script_dir)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
