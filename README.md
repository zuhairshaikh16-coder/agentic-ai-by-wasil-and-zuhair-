# Basic Agentic AI

A minimal but complete "agentic AI" built in Python on top of the Claude API.
It demonstrates the core pattern every agent framework is built on: a loop
of **Think → Act → Observe**, repeated until the task is done.

## What makes this "agentic" (vs. a normal chatbot)?

A plain chatbot takes your message and replies with text. That's it.

An **agent** can also:
- Decide, on its own, that it needs to *do something* (call a tool/function)
  rather than just talk.
- Actually execute that action.
- Look at the result of that action and decide what to do next — possibly
  calling more tools, possibly answering directly.
- Repeat this cycle multiple times without you intervening, until it's
  confident it has a final answer.

That decision-making loop is the entire difference. This project implements
it in the smallest form that's still "real."

## File structure

```
agentic-ai/
├── config.py       # Settings: model, system prompt, iteration limit, API key
├── tools.py        # The agent's "hands": tool schemas + implementations
├── memory.py        # Conversation history + tool-call trace log
├── agent.py         # The core Think -> Act -> Observe loop
├── main.py           # CLI you run to chat with the agent
├── requirements.txt  # Dependencies
└── README.md          # This file
```

## How it works, step by step

1. **You send a message** (`main.py` reads it, passes it to `Agent.run()`).
2. **`memory.py`** stores it in the running conversation history. This
   history is what gets sent to the model on *every* call — the API itself
   is stateless, so "memory" is really just "replay the whole transcript
   each time."
3. **`agent.py`** sends the full history to Claude, along with:
   - The **system prompt** (its personality/rules, from `config.py`)
   - The **tool schemas** (from `tools.py`) — JSON descriptions of what
     tools exist and what arguments they take. The model itself decides,
     based on these descriptions, whether it needs a tool at all.
4. Claude replies with either:
   - Plain text → the agent treats this as the **final answer** and stops.
   - A `tool_use` block → the agent has asked to call a specific tool with
     specific arguments.
5. If a tool was requested, **`agent.py`** looks it up in
   `tools.TOOL_REGISTRY` and actually executes the corresponding Python
   function (this is the "Act" step — the only step where real code runs
   outside the model).
6. The tool's return value is fed back into the conversation as an
   observation. Claude sees this result on the next loop iteration and
   decides: answer now, or call another tool?
7. This repeats until either Claude gives a final text answer, or
   `config.MAX_ITERATIONS` is hit (a safety limit so a confused agent can't
   loop forever).

This is the same loop used (with more bells and whistles) by LangChain
agents, AutoGPT, and Claude's own native tool-use feature — there's no
hidden magic, just this cycle plus more tools and better prompting.

## The built-in tools

| Tool | What it does |
|---|---|
| `calculator` | Safely evaluates arithmetic expressions (uses Python's `ast` module instead of `eval()`, so it can't execute arbitrary code) |
| `get_current_time` | Returns the current date/time |
| `word_counter` | Counts words/characters in a string |

These are intentionally simple so you can see the pattern clearly. In a
real system you'd swap these for things like: web search, database
queries, file read/write, sending emails, calling other APIs, etc.

## How to add your own tool

You only ever touch `tools.py` — the agent loop never changes.

```python
# 1. Write the function (must return a string)
def get_weather(city: str) -> str:
    return f"It's sunny in {city}."  # replace with a real API call

# 2. Describe it so the model knows it exists
TOOL_SCHEMAS.append({
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"}
        },
        "required": ["city"],
    },
})

# 3. Register it so the agent can find it
TOOL_REGISTRY["get_weather"] = get_weather
```

That's the entire extension mechanism.

## Running it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python main.py
```

Example session:

```
You: What's 15% of 240, and how many words are in "the quick brown fox"?
[iteration 1] Calling tool: calculator({'expression': '240 * 0.15'})
[iteration 1] Calling tool: word_counter({'text': 'the quick brown fox'})
[iteration 2] Final answer reached.

Agent: 15% of 240 is 36. "the quick brown fox" has 4 words.
```

Type `trace` at any point to see a log of every tool call made in the
session; type `exit` to quit.

## Key design decisions (and why)

- **Safety limit on iterations** (`MAX_ITERATIONS`): without this, a
  confused agent can call tools forever, burning time and money. Every
  production agent needs this guardrail.
- **`ast`-based calculator instead of `eval()`**: `eval()` on
  model-controlled input is a real code-execution vulnerability. Any tool
  that touches shell commands, file paths, or SQL needs the same care —
  validate/sandbox, don't trust blindly.
- **Errors become strings, not exceptions**: if a tool fails, the agent
  gets a text error message it can reason about and recover from, instead
  of the whole program crashing.
- **Config separated from logic**: changing the model, prompt, or
  iteration limit never requires touching the control-flow code.

## Where to take this next

This is a "basic" agent on purpose. Natural next steps, roughly in order
of complexity:
1. **Persistent memory** — save `memory.py`'s history to disk/a database
   so the agent remembers past sessions.
2. **Real tools** — web search, file system access, calling external APIs.
3. **Planning** — have the model write out a multi-step plan before
   executing, instead of deciding one step at a time.
4. **Multi-agent** — have specialized agents (e.g. "researcher,"
   "writer") hand off work to each other.
5. **Human-in-the-loop** — pause and ask for confirmation before
   executing sensitive tools (e.g. sending an email, deleting a file).
