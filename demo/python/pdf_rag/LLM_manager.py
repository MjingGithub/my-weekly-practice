# !/usr/bin/env python3
from llama_index.core import Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")


class LLMManager:
    def __init__(self):
        Settings.llm = OpenAILike(
            model="qwen-max",
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=api_key,
            context_window=128000,
            is_chat_model=True,
            is_function_calling_model=False,
            temperature=0.5,
        )
        Settings.embed_model = DashScopeEmbedding(
            model_name="text-embedding-v2"
        )

    @staticmethod
    def get_llm():
        return Settings.llm
