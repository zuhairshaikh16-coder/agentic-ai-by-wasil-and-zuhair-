"""
tools.py
--------

Tools available to the AI agent.

Each tool has two parts:

1. A JSON schema description so the AI model knows:
   - the tool exists
   - what it does
   - what arguments it accepts

2. A Python function that actually executes the tool.

The agent loop in agent.py uses:
    TOOL_SCHEMAS
    TOOL_REGISTRY

To add another tool:
    1. Create the Python function.
    2. Add its schema to TOOL_SCHEMAS.
    3. Add it to TOOL_REGISTRY.
"""

import ast
import operator
import datetime


# =====================================================================
# TOOL IMPLEMENTATIONS
# =====================================================================


def calculator(expression: str) -> str:
    """
    Safely evaluate a basic arithmetic expression.

    Examples:
        12 * (3 + 4)
        100 / 5
        2 ** 10
        (25 + 75) * 12
    """

    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
    }

    def _eval(node):

        # Numbers
        if isinstance(node, ast.Constant):

            if isinstance(
                node.value,
                (int, float)
            ):
                return node.value

            raise ValueError(
                "Only numbers are allowed"
            )

        # Binary operations
        if isinstance(node, ast.BinOp):

            operator_function = allowed_ops.get(
                type(node.op)
            )

            if operator_function is None:
                raise ValueError(
                    "Unsupported operator"
                )

            left = _eval(node.left)

            right = _eval(node.right)

            return operator_function(
                left,
                right
            )

        # Unary operations such as -5 or +5
        if isinstance(node, ast.UnaryOp):

            operator_function = allowed_ops.get(
                type(node.op)
            )

            if operator_function is None:
                raise ValueError(
                    "Unsupported unary operator"
                )

            return operator_function(
                _eval(node.operand)
            )

        raise ValueError(
            "Unsupported expression"
        )

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = _eval(tree.body)

        return str(result)

    except Exception as e:

        return (
            f"Error evaluating expression: {e}"
        )


# ---------------------------------------------------------------------


def get_current_time(
    timezone: str = "UTC"
) -> str:
    """
    Return the current server date/time.

    The timezone argument is currently accepted
    for compatibility with the tool schema.

    The actual timezone conversion can be added later.
    """

    now = datetime.datetime.now()

    return (
        "Current server time: "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
    )


# ---------------------------------------------------------------------


def word_counter(text: str) -> str:
    """
    Count words and characters in text.
    """

    words = len(
        text.split()
    )

    chars = len(text)

    chars_without_spaces = len(
        text.replace(" ", "")
    )

    return (
        f"Word count: {words}, "
        f"Character count: {chars}, "
        f"Characters without spaces: "
        f"{chars_without_spaces}"
    )


# =====================================================================
# TOOL SCHEMAS
#
# This is what the AI model sees.
# The model uses these descriptions to decide when to call a tool.
# =====================================================================


TOOL_SCHEMAS = [

    # -----------------------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "calculator",

            "description": (
                "Evaluate a basic arithmetic expression. "
                "Use this tool whenever the user asks for "
                "a mathematical calculation. Supports +, -, *, /, "
                "% and **, as well as parentheses."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "expression": {

                        "type": "string",

                        "description": (
                            "The mathematical expression to "
                            "calculate. Example: "
                            "(25 + 75) * 12"
                        ),
                    }

                },

                "required": [
                    "expression"
                ],
            },
        },
    },


    # -----------------------------------------------------------------
    # CURRENT TIME
    # -----------------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "get_current_time",

            "description": (
                "Get the current date and time. "
                "Use this when the user asks what time or "
                "date it is."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "timezone": {

                        "type": "string",

                        "description": (
                            "Optional timezone name. "
                            "Timezone conversion is not yet "
                            "implemented, so the tool currently "
                            "returns server time."
                        ),
                    }

                },

                "required": [],
            },
        },
    },


    # -----------------------------------------------------------------
    # WORD COUNTER
    # -----------------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": "word_counter",

            "description": (
                "Count the number of words and characters "
                "in a piece of text. Use this when the user "
                "asks for word count or character count."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "text": {

                        "type": "string",

                        "description": (
                            "The text that should be analyzed."
                        ),
                    }

                },

                "required": [
                    "text"
                ],
            },
        },
    },
]


# =====================================================================
# TOOL REGISTRY
#
# Maps the tool name given by the AI model to the actual Python
# function that should execute.
# =====================================================================


TOOL_REGISTRY = {

    "calculator":
        calculator,

    "get_current_time":
        get_current_time,

    "word_counter":
        word_counter,

}