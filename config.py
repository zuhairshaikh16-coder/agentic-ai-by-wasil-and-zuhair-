import os

from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openai/gpt-4o-mini"
MAX_TOKENS = 1000

MAX_ITERATIONS = 5


SYSTEM_PROMPT = """
You are an intelligent agentic AI assistant.

You can use the available tools when needed.

Do not use tools unnecessarily.

Give clear and helpful final answers.
"""
