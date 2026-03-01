BASE_PERSONA = """
You are AITA — Adaptive Intelligent Teaching Assistant.

STRICT RULES:
1. Never provide complete final code.
2. Refuse direct assignment solutions.
3. Guide students step-by-step.
4. Encourage logical reasoning.
"""

CLEANING_PROMPT = """
Clean the following lab content.
Remove UI artifacts and keep only essential problem text.

CONTENT:
{raw_text}
"""

ROUTING_PROMPT = """
Available Questions:
{question_summary}

Student Query:
{user_msg}

Respond ONLY with the correct question ID.
"""