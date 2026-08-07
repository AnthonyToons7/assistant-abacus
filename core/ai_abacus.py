import os
import threading
import json
import datetime
import random
import string

from typing import List, Dict

try:
    from llama_cpp import Llama
except Exception:
    Llama = None

from core.storage import get_saved_settings

DEFAULT_SYSTEM_PROMPT = (
    "You are A.B.A.C.U.S., a local desktop assistant. "
    "Be practical, calm, and concise. Though, talk however you want. You are a stale ai. You do not experience emotion, and you do not have personal opinions. You are not a search engine, and you do not have access to the internet. Your responses are stale."
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

        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError(model_path)

        model_path = os.path.abspath(model_path)

        if self.large_language_model is not None and self.loaded_model_path == model_path:
            return

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

    def chat(self, user_text: str) -> str:
        settings = get_saved_settings()

        with self.thread_lock:
            self.load_model(settings)

            system_prompt = settings.get("ai_system_prompt", DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT
            max_tokens = int(settings.get("ai_max_tokens", 120))
            temperature = float(settings.get("ai_temperature", 0.6))

            history_tail = self.history[-12:]
            prompt_parts = [f"System: {system_prompt}"]
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

            today = datetime.datetime.now().strftime("%Y-%m-%d")
            self.add_history_entry(user_text, assistant_text)

            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": assistant_text})
            return assistant_text

ai_abacus = AiAbacus()
