"""
Parser for Google Gemini conversation exports.

Handles multiple formats:
- JSON from Chrome extensions (Gemini Chat Exporter, etc.)
- HTML from Google Docs exports
- JSON from Google Takeout (if available)

Structure: Varies significantly by export method
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

import sys
sys.path.append(str(Path(__file__).parent.parent))
from models import RawConversation, Message
from parsers.base_parser import ConversationParser


class GeminiParser(ConversationParser):
    """
    Parser for Google Gemini conversation exports.

    Supports multiple formats:

    Format 1: Extension JSON Export
    {
      "conversation_id": "gemini-conv-123",
      "title": "Conversation Title",
      "date": "2025-10-15",
      "messages": [
        {
          "role": "user" or "model",
          "content": "Message content",
          "timestamp": "2025-10-15T14:30:00Z"
        }
      ]
    }

    Format 2: Simplified JSON
    {
      "id": "conversation-id",
      "messages": [
        {"role": "user", "text": "content"},
        {"role": "model", "text": "content"}
      ]
    }

    Format 3: HTML (from Google Docs export)
    Parsed using BeautifulSoup to extract conversation structure
    """

    def detect_format(self) -> bool:
        """
        Detect if file is a Gemini export.

        Checks for:
        - JSON with 'messages' array and 'model' role (Gemini uses 'model', not 'assistant')
        - HTML with Gemini conversation patterns
        """
        try:
            # Check if it's HTML first
            with open(self.file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('<!DOCTYPE') or first_line.startswith('<html'):
                    return True  # Assume HTML is Gemini export

            # Try JSON
            try:
                data = self._load_json()
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                # Try JSONL
                try:
                    data = self._load_jsonl()
                    if not data:
                        return False
                    data = data[0] if isinstance(data, list) else data
                except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                    return False

            # Handle array of conversations
            if isinstance(data, list):
                if not data:
                    return False
                sample = data[0]
            else:
                sample = data

            # Check for Gemini-specific structure
            # Gemini uses "model" instead of "assistant"
            has_messages = "messages" in sample
            if has_messages:
                messages = sample.get("messages", [])
                if messages and isinstance(messages, list):
                    first_msg = messages[0]
                    # Gemini uses 'model' role
                    has_model_role = first_msg.get("role") == "model" or any(
                        msg.get("role") == "model" for msg in messages
                    )
                    return has_model_role

            return False

        except Exception:
            return False

    def parse(self) -> List[RawConversation]:
        """
        Parse Gemini conversation export file.

        Returns:
            List of RawConversation objects
        """
        # Detect format type
        with open(self.file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            is_html = first_line.startswith('<!DOCTYPE') or first_line.startswith('<html')

        if is_html:
            return self._parse_html()
        else:
            return self._parse_json()

    def _parse_json(self) -> List[RawConversation]:
        """Parse JSON or JSONL format."""
        # Try JSON first, then JSONL
        try:
            data = self._load_json()
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            try:
                data = self._load_jsonl()
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                raise ValueError("File is neither valid JSON nor JSONL")

        # Handle both single conversation and array
        if isinstance(data, dict):
            conversations_data = [data]
        else:
            conversations_data = data

        conversations = []
        for conv_data in conversations_data:
            try:
                conversation = self._parse_single_conversation(conv_data)
                if conversation and conversation.messages:
                    conversations.append(conversation)
            except Exception as e:
                print(f"Warning: Failed to parse conversation {conv_data.get('id', 'unknown')}: {e}")
                continue

        return conversations

    def _parse_html(self) -> List[RawConversation]:
        """
        Parse HTML format (from Google Docs export).

        Note: Basic implementation without BeautifulSoup dependency.
        Uses regex to extract conversation patterns.
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract title (from <title> tag or first heading)
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Gemini Conversation"

        # Try to extract messages using common HTML patterns
        # This is a simplified approach - real HTML parsing would use BeautifulSoup
        messages = []

        # Pattern 1: Look for alternating user/assistant blocks
        # Common in Google Docs exports with bold labels like "You:" and "Gemini:"
        user_pattern = r'(?:You|User):\s*(.+?)(?=(?:Gemini|Model|Assistant):|$)'
        model_pattern = r'(?:Gemini|Model|Assistant):\s*(.+?)(?=(?:You|User):|$)'

        user_matches = re.findall(user_pattern, html_content, re.DOTALL | re.IGNORECASE)
        model_matches = re.findall(model_pattern, html_content, re.DOTALL | re.IGNORECASE)

        # Interleave user and model messages
        for i in range(max(len(user_matches), len(model_matches))):
            if i < len(user_matches):
                content = self._clean_html_text(user_matches[i])
                if content:
                    messages.append(Message(
                        role="user",
                        content=content,
                        timestamp=datetime.now(),
                        metadata={"source": "html_export"}
                    ))

            if i < len(model_matches):
                content = self._clean_html_text(model_matches[i])
                if content:
                    messages.append(Message(
                        role="assistant",
                        content=content,
                        timestamp=datetime.now(),
                        metadata={"source": "html_export"}
                    ))

        if not messages:
            # Fallback: extract all <p> tags as messages
            p_matches = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
            for i, content in enumerate(p_matches):
                clean_content = self._clean_html_text(content)
                if clean_content and len(clean_content) > 10:  # Skip very short content
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append(Message(
                        role=role,
                        content=clean_content,
                        timestamp=datetime.now(),
                        metadata={"source": "html_export", "paragraph_index": i}
                    ))

        if not messages:
            return []

        # Create single conversation from HTML
        conversation = RawConversation(
            external_id=self._generate_id_from_title(title),
            source="Google",
            title=self._truncate_title(title),
            create_time=datetime.now(),
            messages=messages,
            metadata={
                "platform": "Gemini",
                "format": "html",
                "original_title": title
            }
        )

        return [conversation]

    def _parse_single_conversation(self, data: Dict[str, Any]) -> Optional[RawConversation]:
        """
        Parse a single Gemini conversation from JSON data.

        Args:
            data: Conversation JSON object

        Returns:
            RawConversation object or None if parsing fails
        """
        # Extract ID (try multiple possible fields)
        external_id = (
            data.get("conversation_id") or
            data.get("id") or
            data.get("chat_id") or
            self._generate_id_from_title(data.get("title", ""))
        )

        # Extract title
        title = data.get("title") or data.get("name") or "Untitled Gemini Conversation"

        # Extract timestamps
        date_str = data.get("date") or data.get("timestamp") or data.get("created_at")
        create_time = self._parse_flexible_timestamp(date_str)

        # Extract messages
        messages_data = data.get("messages") or data.get("chat_messages") or []
        messages = self._parse_messages(messages_data)

        if not messages:
            return None

        # Truncate title if too long
        title = self._truncate_title(title)

        return RawConversation(
            external_id=external_id,
            source="Google",
            title=title,
            create_time=create_time,
            messages=messages,
            metadata={
                "platform": "Gemini",
                "format": "json",
                "original_title": data.get("title", "")
            }
        )

    def _parse_messages(self, messages_data: List[Dict[str, Any]]) -> List[Message]:
        """Parse list of messages from Gemini format."""
        messages = []
        for msg_data in messages_data:
            message = self._parse_single_message(msg_data)
            if message:
                messages.append(message)
        return messages

    def _parse_single_message(self, msg_data: Dict[str, Any]) -> Optional[Message]:
        """
        Parse a single message from Gemini format.

        Gemini uses 'model' instead of 'assistant' for the AI role.
        """
        # Extract role
        role = msg_data.get("role") or msg_data.get("sender", "user")

        # Normalize role: Gemini uses 'model', we use 'assistant'
        if role == "model":
            role = "assistant"
        elif role not in ["user", "assistant", "system"]:
            role = "user"  # Default

        # Skip system messages
        if role == "system":
            return None

        # Extract content (try multiple possible fields)
        content = (
            msg_data.get("content") or
            msg_data.get("text") or
            msg_data.get("message") or
            ""
        )

        if not content or not str(content).strip():
            return None

        # Extract timestamp
        timestamp = self._parse_flexible_timestamp(
            msg_data.get("timestamp") or msg_data.get("created_at") or msg_data.get("time")
        )

        # Extract metadata
        metadata = {
            "message_id": msg_data.get("id", ""),
            "original_role": msg_data.get("role", "")
        }

        return Message(
            role=role,
            content=str(content).strip(),
            timestamp=timestamp,
            metadata=metadata
        )

    def _parse_flexible_timestamp(self, timestamp: Any) -> datetime:
        """
        Parse timestamp with multiple format support.

        Handles:
        - ISO format: "2025-10-15T14:30:00Z"
        - Date only: "2025-10-15"
        - Unix timestamp: 1678015311
        - None/missing
        """
        if timestamp is None:
            return datetime.now()

        if isinstance(timestamp, datetime):
            return timestamp

        try:
            timestamp_str = str(timestamp)

            # Try Unix timestamp
            if timestamp_str.isdigit():
                return datetime.fromtimestamp(int(timestamp_str))

            # Try ISO format
            if 'T' in timestamp_str:
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str[:-1]
                return datetime.fromisoformat(timestamp_str)

            # Try date only (YYYY-MM-DD)
            if '-' in timestamp_str and len(timestamp_str) >= 10:
                return datetime.fromisoformat(timestamp_str[:10])

        except (ValueError, TypeError):
            pass

        return datetime.now()

    def _clean_html_text(self, html: str) -> str:
        """
        Remove HTML tags and clean up text.

        Basic implementation without BeautifulSoup.
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)

        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def _generate_id_from_title(self, title: str) -> str:
        """
        Generate a conversation ID from title (for exports without IDs).

        Uses sanitized title + timestamp.
        """
        sanitized = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())
        sanitized = re.sub(r'-+', '-', sanitized)[:50]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"gemini-{sanitized}-{timestamp}"
