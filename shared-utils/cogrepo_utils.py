#!/usr/bin/env python3
"""
Shared utilities for working with CogRepo data across projects
Common functions for conversation searching, date formatting, and data processing
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

def load_conversations(repo_path: str) -> List[Dict[str, Any]]:
    """Load conversations from a COGREPO JSONL file"""
    conversations = []
    
    if not Path(repo_path).exists():
        raise FileNotFoundError(f"Repository file not found: {repo_path}")
    
    with open(repo_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                convo = json.loads(line)
                conversations.append(convo)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipped malformed JSON at line {line_num}: {e}")
                continue
    
    return conversations

def search_conversation_text(convo: Dict[str, Any], query: str) -> bool:
    """Search for query in conversation text fields"""
    searchable_fields = [
        convo.get('raw_text', ''),
        convo.get('generated_title', ''),
        convo.get('summary_abstractive', ''),
        ' '.join(convo.get('tags', []))
    ]
    
    full_text = ' '.join(searchable_fields).lower()
    return query.lower() in full_text

def search_conversations(conversations: List[Dict[str, Any]], 
                        search_terms: List[str] = None,
                        custom_query: str = None) -> List[Dict[str, Any]]:
    """Search conversations for matching terms or custom query"""
    results = []
    
    for convo in conversations:
        if custom_query:
            if search_conversation_text(convo, custom_query):
                results.append(convo)
        elif search_terms:
            for term in search_terms:
                if search_conversation_text(convo, term):
                    results.append(convo)
                    break
    
    return results

def format_conversation_date(timestamp_str: str) -> str:
    """Format conversation timestamp for display"""
    try:
        dt = datetime.strptime(timestamp_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return timestamp_str

def sort_conversations_by_date(conversations: List[Dict[str, Any]], 
                              reverse: bool = False) -> List[Dict[str, Any]]:
    """Sort conversations by timestamp"""
    return sorted(conversations, 
                  key=lambda x: x.get('timestamp', ''), 
                  reverse=reverse)

def get_conversation_summary(convo: Dict[str, Any], max_length: int = 150) -> str:
    """Get a truncated summary of a conversation"""
    summary = convo.get('summary_abstractive', '')
    if not summary:
        # Fall back to raw text if no summary
        summary = convo.get('raw_text', '')[:max_length*2]  # Get more text to truncate
    
    if len(summary) > max_length:
        return summary[:max_length] + "..."
    return summary

def save_conversations_json(conversations: List[Dict[str, Any]], 
                           output_path: str,
                           indent: int = 2) -> None:
    """Save conversations to a JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=indent, ensure_ascii=False)

def print_conversation_summary(convo: Dict[str, Any], index: int = None) -> None:
    """Print a formatted summary of a single conversation"""
    date = format_conversation_date(convo.get('timestamp', 'Unknown date'))
    title = convo.get('generated_title', 'Untitled')
    source = convo.get('source', 'Unknown')
    tags = ', '.join(convo.get('tags', [])[:5])
    
    prefix = f"{index}. " if index is not None else ""
    print(f"\n{prefix}[{date}] - {source}")
    print(f"   Title: {title}")
    if tags:
        print(f"   Tags: {tags}")
    
    summary = get_conversation_summary(convo)
    if summary:
        print(f"   Summary: {summary}")

def get_default_repo_path() -> str:
    """Get the default repository path - checks multiple locations"""
    import os
    
    # Try environment variable first
    if 'COGREPO_PATH' in os.environ:
        return os.environ['COGREPO_PATH']
    
    # Try relative paths from current working directory
    possible_paths = [
        # If running from a project directory
        "../cogrepo/data/enriched_repository.jsonl",
        # If running from RR Coding Experiments root
        "cogrepo/data/enriched_repository.jsonl",
        # If running from scripts directory
        "../../cogrepo/data/enriched_repository.jsonl",
        # Fallback to original location (legacy)
        "/Users/newuser/Desktop/COGREPO_FINAL_20250816/enriched_repository.jsonl",
        # Current RR Coding Experiments location
        "/Users/newuser/Desktop/RR Coding Experiments/cogrepo/data/enriched_repository.jsonl"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    # Return first option as default if none found
    return possible_paths[0]