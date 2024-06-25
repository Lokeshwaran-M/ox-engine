from typing import List, Dict, Union

from transformers import AutoTokenizer


class Prompt:

    def __init__(self, model_src, max_available_tokens: int = 3000):
        self.tokenizer = AutoTokenizer.from_pretrained(model_src)
        self.max_available_tokens = max_available_tokens

    def count_token(self, content: str):
        return len(self.tokenizer.tokenize(content)) + 2

    def pad_token(self, content: str, num_tokens: int):
        return self.tokenizer.decode(
            self.tokenizer.encode(content, max_length=num_tokens)
        )

    def encode(self, content: str):
        return self.tokenizer.encode(content)

    def process(self, query, context=None, instruction=None):

        instruction = (
            instruction
            or "you are a task based ai assistent ox-ai based on user Query and context in you should provide a response which contain your replay to the user query and use context if its given [if the query is some kind of task then the task will be handled by external tool and based on external_tool_status give response if there is no status ignore it"
        )

        context = context or "None"
        tokens_avilable = (
            self.max_available_tokens
            - self.count_token(query)
            - self.count_token(instruction)
        )
        context = (
            context[:tokens_avilable] if len(context) > tokens_avilable else context
        )

        input_pmt = f"""
        [instruction]: {instruction}
        context : {context}
        query : {query}
        [response]:"""
        return input_pmt

    def final_out(self, messages: List[Dict]):
        return self.tokenizer.apply_chat_template(messages, tokenize=False)
