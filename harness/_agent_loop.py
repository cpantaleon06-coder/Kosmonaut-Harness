import json

from ._execute_tools import execute_tool
from ._llm_client import chat
from ._tools import TOOLS

MAX_STEPS = 25

SYSTEM_PROMPT = (
    "You are a coding agent. You work inside a Linux container, in the folder /workspace. "
    "Python 3.12 is installed. Use the tools to create files and run commands. "
    "Always run your code to check that it works. "
    "When the task is finished, reply with a short summary and do not call any more tools."
)


def run_agent(task: str, container_id: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for step in range(MAX_STEPS):
        message = chat(messages, TOOLS)
        messages.append(message)

        if not message.tool_calls:
            return message.content or ""

        for call in message.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            print(f"[step {step + 1}] {name} {args}")

            result = execute_tool(name, args, container_id)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return "Stopped: the agent reached the step limit before finishing."