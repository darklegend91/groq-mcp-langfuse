import asyncio
import sys

from app.llm.groq_local import ask_local

question = ' '.join(sys.argv[1:]) or 'What is 17 + 25?'
print(asyncio.run(ask_local(question)))
# Run it from the product root with python -m scripts.run_local_agent "What is 17 + 25?" (add an empty scripts/__init__.py if your Python version needs it).
