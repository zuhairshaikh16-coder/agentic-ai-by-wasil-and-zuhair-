"""
agent.py
--------
The core of the system. This implements the agent loop:

    THINK -> ACT -> OBSERVE -> repeat -> FINAL ANSWER

This version uses OpenRouter through the OpenAI-compatible API.
"""

import json

from openai import OpenAI

import config
from tools import TOOL_SCHEMAS, TOOL_REGISTRY
from memory import Memory


class Agent:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(
            api_key=api_key or config.API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        self.memory = Memory()

    def _call_model(self):
        """
        Send the current conversation history to OpenRouter.
        """

        messages = [
            {
                "role": "system",
                "content": config.SYSTEM_PROMPT,
            }
        ]

        messages.extend(self.memory.get_history())

        response = self.client.chat.completions.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )

        return response

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """
        ACT step:
        Find the requested tool in the registry and execute it.
        """

        if tool_name not in TOOL_REGISTRY:
            return f"Error: unknown tool '{tool_name}'"

        try:
            result = TOOL_REGISTRY[tool_name](**tool_input)
            return str(result)

        except Exception as e:
            return f"Error running tool '{tool_name}': {e}"

    def run(self, user_input: str, verbose: bool = True) -> str:
        """
        Run the complete agent loop for one user request.

        THINK
            The model decides what needs to happen.

        ACT
            The model requests a tool.

        OBSERVE
            The tool result is sent back to the model.

        FINAL ANSWER
            The model produces the final response.
        """

        # Add the user's request to memory
        self.memory.add_user_message(user_input)

        # Maximum number of agent iterations
        for iteration in range(config.MAX_ITERATIONS):

            # =========================================================
            # THINK
            # =========================================================

            response = self._call_model()

            message = response.choices[0].message

            # =========================================================
            # FINAL ANSWER
            # =========================================================

            if not message.tool_calls:

                final_text = message.content or ""

                if verbose:
                    print(
                        f"[iteration {iteration + 1}] "
                        "Final answer reached."
                    )

                # Store the assistant's final response
                self.memory.add_assistant_message(final_text)

                return final_text

            # =========================================================
            # MODEL REQUESTED ONE OR MORE TOOLS
            # =========================================================

            assistant_message = {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [],
            }

            for tool_call in message.tool_calls:

                assistant_message["tool_calls"].append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                )

            # Store the assistant's tool request in memory
            self.memory.add_assistant_message(
                assistant_message
            )

            # =========================================================
            # ACT + OBSERVE
            # =========================================================

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name

                # -----------------------------------------------------
                # Convert JSON tool arguments into Python dictionary
                # -----------------------------------------------------

                try:
                    tool_input = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError as e:

                    tool_input = {}

                    result = (
                        f"Error: invalid tool arguments: {e}"
                    )

                    if verbose:
                        print(
                            f"[iteration {iteration + 1}] "
                            f"Invalid arguments for "
                            f"{tool_name}: {tool_call.function.arguments}"
                        )

                else:

                    if verbose:
                        print(
                            f"[iteration {iteration + 1}] "
                            f"Calling tool: "
                            f"{tool_name}({tool_input})"
                        )

                    # -------------------------------------------------
                    # Execute the actual Python tool
                    # -------------------------------------------------

                    result = self._execute_tool(
                        tool_name,
                        tool_input,
                    )

                # -----------------------------------------------------
                # Save tool call for trace/debugging
                # -----------------------------------------------------

                self.memory.log_tool_call(
                    tool_name,
                    tool_input,
                    result,
                )

                # -----------------------------------------------------
                # OBSERVE
                #
                # Send the tool result back to the model.
                # -----------------------------------------------------

                self.memory.add_tool_message(
                    tool_call.id,
                    result,
                )

        # =============================================================
        # MAX ITERATIONS REACHED
        # =============================================================

        return (
            "I wasn't able to reach a final answer within "
            "the allowed number of steps. Try rephrasing "
            "the request or breaking it into smaller parts."
        )