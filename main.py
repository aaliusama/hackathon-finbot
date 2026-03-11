import os

import chainlit as cl
import dotenv
from openai.types.responses import ResponseTextDeltaEvent

from agents import Runner, SQLiteSession
from finance_agent import finance_agent

dotenv.load_dotenv()

# Authentication
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if username == os.getenv("CHAINLIT_USERNAME", "ali") and password == os.getenv("CHAINLIT_PASSWORD", "usama"):
        return cl.User(identifier=username)
    else:
        return None


WELCOME = """Hi! I'm **FinBot**, your personal finance assistant.

I can help with:
- **Budget analysis** — tell me your income and expenses
- **Investment projections** — compound interest calculations
- **Savings goals** — how long to reach your target
- **Financial tips** — debt, saving, investing advice
- **Crypto prices** — live Bitcoin, Ethereum, Solana and more

Try asking:
> *"I earn $5k/month: rent $1500, food $400, transport $300, entertainment $300, savings $500, other $200 — how's my budget?"*
> *"If I invest $10,000 at 7% for 20 years, how much will I have?"*
> *"What's the current Bitcoin price?"*
> *"How do I pay off debt faster?"*
"""


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("session", SQLiteSession("finbot_history"))
    await cl.Message(content=WELCOME).send()


@cl.on_message
async def on_message(message: cl.Message):
    session = cl.user_session.get("session")

    result = Runner.run_streamed(finance_agent, message.content, session=session)

    msg = cl.Message(content="")
    async for event in result.stream_events():
        # Stream text to screen
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(token=event.data.delta)

        # Show tool calls as collapsible steps
        elif (
            event.type == "raw_response_event"
            and hasattr(event.data, "item")
            and hasattr(event.data.item, "type")
            and event.data.item.type == "function_call"
            and len(event.data.item.arguments) > 0
        ):
            with cl.Step(name=event.data.item.name, type="tool") as step:
                step.input = event.data.item.arguments

    await msg.update()
