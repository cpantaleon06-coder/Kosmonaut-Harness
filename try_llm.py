from harness._llm_client import chat
from harness._tools import TOOLS

message = chat(
    [{"role": "user", "content": "Create a file named a.txt that contains the word hello."}],
    TOOLS,
)
print("text:", message.content)
print("tool calls:", message.tool_calls)
