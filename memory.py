"""
memory.py
---------
Memory for the agent.

The OpenRouter/OpenAI-compatible API is stateless, so we keep the
conversation history and send it back with every model request.

This module also keeps a lightweight log of tool calls for debugging.
"""


class Memory:
    def __init__(self):
        # Full message history sent to the model
        self.messages = []

        # Human-readable trace of tool usage
        self.tool_call_log = []

    def add_user_message(self, content):
        """Add a user message to the conversation."""
        self.messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

    def add_assistant_message(self, content):
        """Add an assistant message to the conversation."""

        if isinstance(content, dict):
            # Used when the assistant requests a tool.
            self.messages.append(content)

        else:
            # Used for normal assistant responses.
            self.messages.append(
                {
                    "role": "assistant",
                    "content": content,
                }
            )

    def add_tool_message(self, tool_call_id, content):
        """Add a tool result to the conversation."""

        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": str(content),
            }
        )

    def log_tool_call(self, tool_name, tool_input, tool_result):
        """Record a tool call for debugging."""

        self.tool_call_log.append(
            {
                "tool": tool_name,
                "input": tool_input,
                "result": tool_result,
            }
        )

    def get_history(self):
        """Return the complete conversation history."""

        return self.messages

    def print_trace(self):
        """Print a readable summary of every tool call."""

        if not self.tool_call_log:
            print("(no tools were used)")
            return

        for i, entry in enumerate(self.tool_call_log, 1):
            print(
                f"  {i}. {entry['tool']}({entry['input']}) "
                f"-> {entry['result']}"
            )