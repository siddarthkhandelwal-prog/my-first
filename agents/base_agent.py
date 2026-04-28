import anthropic
from config import ANTHROPIC_API_KEY, MODEL, COMPANY_NAME, COMPANY_CONTEXT


class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation_history = []

    def _build_system(self) -> str:
        return f"""You are {self.name}, the {self.role} at {COMPANY_NAME}.

Company Context:
{COMPANY_CONTEXT}

Your Role:
{self.system_prompt}

Always respond in a structured, professional manner. Be specific, data-driven, and actionable.
Today's date: {self._today()}"""

    def _today(self) -> str:
        from datetime import date
        return date.today().strftime("%B %d, %Y")

    def chat(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=self._build_system(),
            messages=self.conversation_history,
        )
        reply = response.content[0].text
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self.conversation_history = []
