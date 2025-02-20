import g4f
import httpx as httpx
from g4f.errors import RetryProviderError
from openai import OpenAI, RateLimitError


class ChatGptService:
    """Класс работы с ChatGPT"""
    client: OpenAI = None
    message_list: list = None

    def __init__(self, token):
        token = "sk-proj-" + token[:3:-1] if token.startswith('gpt:') else token
        self.client = OpenAI(http_client=httpx.Client(proxy="http://18.199.183.77:49232"), api_key=token)
        self.message_list = []

    async def send_message_list(self) -> str:
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.message_list,
                max_tokens=4000,
                temperature=0.9,
            )
        except RateLimitError:
            return self._free_gpt()
        message = completion.choices[0].message
        self.message_list.append(message)
        return message.content

    def _free_gpt(self) -> str:
        try:
            response = self._response_free_gpt()
        except RetryProviderError:
            try:
                response = self._response_free_gpt()
            except Exception as e:
                return f"Произошла ошибка: {e}"
        return response

    def _response_free_gpt(self) -> str:
        return g4f.ChatCompletion.create(model='gpt-4o', messages=self.message_list, stream=False)

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()
