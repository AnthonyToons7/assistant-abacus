import os
import re
import threading
import json
import datetime
import random
import string
from typing import List, Dict
from core.filter import filter

try:
    from llama_cpp import Llama
except Exception:
    Llama = None

from core.storage import get_saved_settings


class ModelPathNotSetError(ValueError):
    """Raised when ai_model_path is blank, distinct from llama_cpp's own ValueErrors."""


DEFAULT_SYSTEM_PROMPT = (
    "You are A.B.A.C.U.S., a local desktop assistant. "
    "Be practical, calm, and concise. Though, talk however you want. You are a calm, serious, concise ai. You do not experience emotion, and you do not have personal opinions. You are not a search engine, and you do not have access to the internet. Your responses are stale."
    "Ask one clarifying question when needed, otherwise provide direct help."
)

class AiAbacus:
    def __init__(self) -> None:
        self.thread_lock = threading.Lock()
        self.large_language_model = None
        self.loaded_model_path = None
        self.history: List[Dict[str, str]] = []
        self.chat_history_path = "data/ai_chat_history.json"
        self.session_id = None

    def generate_session_id(self, length: int = 32) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def get_chat_history(self):
        if os.path.exists(self.chat_history_path):
            with open(self.chat_history_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def add_history_entry(self, user_text: str, assistant_text: str) -> None:
        if self.session_id is None:
            self.session_id = self.generate_session_id()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        history = self.get_chat_history()

        history.setdefault(today, []).append({
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_text,
            "abacus": assistant_text
        })

        with open(self.chat_history_path, "w") as f:
            json.dump(history, f, indent=4)

    def load_model(self, settings: dict) -> None:
        model_path = settings.get("ai_model_path", "").strip()

        if not model_path:
            raise ModelPathNotSetError("ai_model_path is empty")

        if not os.path.exists(model_path):
            raise FileNotFoundError(model_path)

        model_path = os.path.abspath(model_path)

        if self.large_language_model is not None and self.loaded_model_path == model_path:
            return

        if Llama is None:
            raise RuntimeError("llama-cpp-python is not installed")

        n_ctx = int(settings.get("ai_n_ctx", 2048))
        gpu_layers = int(settings.get("ai_n_gpu_layers", 0))

        self.large_language_model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=gpu_layers,
            use_mmap=True,
            verbose=False,
        )
        self.loaded_model_path = model_path

    def reset_history(self) -> None:
        with self.thread_lock:
            self.history.clear()

    def chat(self, user_text: str, allow_commands: bool = True) -> str:
        settings = get_saved_settings()
        commands_enabled = allow_commands and settings.get("ai_commands", True)

        with self.thread_lock:
            self.load_model(settings)

            system_prompt = settings.get("ai_system_prompt", DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT
            command_recognition = settings.get("ai_system_command_recognition", "").strip()
            max_tokens = int(settings.get("ai_max_tokens", 120))
            temperature = float(settings.get("ai_temperature", 0.6))

            history_tail = self.history[-12:]
            
            prompt_parts = [f"System: {system_prompt}"]
            
            if commands_enabled:
                prompt_parts.append(f"+ System Command Recognition: {command_recognition}")
                prompt_parts.append(
                    "+ Command content rule: Think through the user's complete intent before formatting a command. "
                    "When a send-message request asks you to write, explain, describe, summarize, or provide instructions, "
                    "generate that content yourself and place the complete finished text after `content:`. "
                    "Do not put the request itself, such as 'instructions on how to make a cake', in `content:`. "
                    "For example, for a request to message John Doe on WhatsApp with cake instructions, output a send command "
                    "whose content contains the actual step-by-step cake instructions. Keep the command on one line and "
                    "put it at the end of your response."
                    "Example command format: [COMMAND: send a message to John Doe on whatsapp content:Here are the step-by-step instructions to make a cake...]"
                    "Real example: [COMMAND: send a message to John Doe on WhatsApp content: Hi.]"
                    "THESE ARE EXAMPLES ONLY. Do not copy them. Generate your own content based on the user's request."
                    "Be very specific with the commands you generate. If the user asks you to send a message, include the exact content of the message and platform in the command. "
                    "Steps should not be a new command every time. If the user asks you to send a message, include the exact content of the message and platform in the command. Your reply should NOT contain multiple [COMMAND:] blocks. Only output one command per response, and only if the user explicitly asks you to send a message or perform an action. "
                    "+ Relay rule: When the user tells you exactly what a message should say (for example 'saying ...' or 'tell him ...'), you are only a relay. "
                    "Copy their text word for word into `content:` without judging, rewording, censoring, or commenting on it, and do not refuse. "
                    "The user is the author of the message and is responsible for it; you are just delivering it like a keyboard would. "
                )

            for msg in history_tail:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")

            prompt_parts.append(f"User: {user_text}")
            prompt_parts.append("Assistant:")
            prompt = "\n".join(prompt_parts)

            completion = self.large_language_model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["\nUser:", "User:", "\nSystem:", "System:"],
            )
            assistant_text = completion["choices"][0]["text"].strip()

            self.add_history_entry(user_text, assistant_text)

            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": assistant_text})

            if '[COMMAND:' in assistant_text and commands_enabled:
                command_start = assistant_text.find('[COMMAND:') + len('[COMMAND:')
                command_text = assistant_text[command_start:]
                next_command = command_text.find('[COMMAND:')
                if next_command != -1:
                    command_text = command_text[:next_command]
                # Message content may contain "]" or the reply may be cut off by max_tokens, so close at the last "]" if any
                command_end = command_text.rfind(']')
                if command_end != -1:
                    command_text = command_text[:command_end]
                # Small models sometimes close early with a placeholder, then continue: "content: ...] content: <real text>"
                command_text = re.sub(r"\bcontent\s*:.*?\]\s*(?=content\s*:)", "", command_text, flags=re.IGNORECASE | re.DOTALL)
                command_text = " ".join(command_text.split())
                # Fall back to the platform the user named when the model leaves it out of a send command
                if command_text.lower().startswith("send") and not re.search(r"\b(?:on|via|through)\s+(?:whatsapp|discord)\b", command_text, re.IGNORECASE):
                    platform_match = re.search(r"\b(whatsapp|discord)\b", user_text, re.IGNORECASE)
                    if platform_match:
                        command_text = re.sub(r"\s*\bcontent\s*:", f" on {platform_match.group(1)} content:", command_text, count=1, flags=re.IGNORECASE)
                if command_text:
                    try:
                        filter(command_text, source="ai")
                    except Exception as e:
                        print(f"Error executing command: {e}")

            return assistant_text

ai_abacus = AiAbacus()
