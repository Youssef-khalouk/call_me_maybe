

from llm_sdk import Small_LLM_Model
import numpy as np
import json

class My_Model:
    def __init__(self) -> None:
        self.model = Small_LLM_Model()
        self.vocab_path = self.model.get_path_to_vocab_file()
        self.top_tokens: list[int] = []

        with open(self.vocab_path, "r", encoding="utf-8") as file:
            self.vocabulary: dict[str, int] = json.loads(file.read())
        
        self.id_to_token: dict[int, str] = {}
        for key, value in self.vocabulary.items():
            self.id_to_token[value] = key
    
    @staticmethod
    def _split(prompt: str) -> list[str]:
        return prompt.replace(" ", " Ġ").split()
  
    def decode(self, token_id: str) -> str:
        if token_id == 5267:
            return "?\n"
        word = self.id_to_token.get(token_id, "")
        word = word.replace("Ġ", " ")
        return word

    def encode(self, prompt: str) -> list[int]:
        words: list[str] = self._split(prompt)
        tokens: list[int] = []

        for word in words:
            start = 0
            while start < len(word):
                found = False
                for end in range(len(word), start, -1):
                    piece = word[start:end]
                    token_id = self.vocabulary.get(piece)
                    if token_id is not None:
                        tokens.append(token_id)
                        start = end
                        found = True
                        break
                if not found:
                    start += 1
        return tokens

    def get_logits(self, tokens_array: list[int]) -> any:
        return self.model.get_logits_from_input_ids(tokens_array)

    def get_next_token_id(self, tokens_array: list[int]) -> int:
        self.top_tokens = np.argpartition(self.get_logits(tokens_array), -2)
        return self.top_tokens[-1]

    def get_second_logit(self) -> int | None:
        if len(self.top_tokens) >= 2:
            return self.top_tokens[-2]
        return None

    def get_next_token(self, prompt: str) -> str:
        token_id = self.get_next_token_id(self.encode(prompt))
        return self.decode(token_id)

    def get_second_token(self) -> str:
        if len(self.top_tokens) >= 2:
            return self.decode(self.top_tokens[-2])
        return ""


    


model = My_Model()

prompt = "User: hi Assistant: hi, how can i help you? User: hello how are you? Assistant: "
while True:

    prompt += model.get_next_token(prompt)
    print(prompt)

    if "User:" in prompt[-8:]:
        break
