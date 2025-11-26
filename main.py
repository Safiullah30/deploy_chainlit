
import os
import chainlit as cl
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, RunConfig

# ------------------------
# Load environment variables
# ------------------------
load_dotenv()
set_tracing_disabled(True)

# ------------------------
# Setup OpenAI/Gemini Client
# ------------------------
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta"
)

mymodel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

config = RunConfig(   # 👈 confiq ki spelling galat thi
    model=mymodel,
    model_provider=client,
    tracing_disabled=True
)

# ------------------------
# Agent (Advanced Instructions)
# ------------------------
agent = Agent(
    name="helpful agent",
    instructions="You are a helpful assistant."
)

# ------------------------
# Chat Handlers
# ------------------------
@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content="👋 Welcome to helpful assistance!"
    ).send()

# @cl.on_message
# async def handle_message(message: cl.Message):
#     # Purani history nikal lo
#     history = cl.user_session.get("history")

#     # User ka new message save karo
#     history.append({"role": "user", "content": message.content})

#     # Sirf latest user input bhejna hai
#     result = await Runner.run(
#         agent,
#         input=message.content,
#         run_config=config,   # 👈 yaha bhi spelling fix
#     )

#     # Agent ka jawab
#     response = result.final_output or "⚠ Sorry, I couldn't process that. Please try again."

#     # Response bhi history mai save kar do
#     history.append({"role": "assistant", "content": response})
#     cl.user_session.set("history", history)

#     # User ko reply bhej do
#     await cl.Message(content=response).send()

@cl.on_message
async def handle_message(message: cl.Message):
    # Purani history lo
    history = cl.user_session.get("history")

    # User ka naya message add karo
    history.append({"role": "user", "content": message.content})

    # Conversation ko ek string mai convert karo
    conversation = ""
    for msg in history:
        role = msg["role"].capitalize()
        content = msg["content"]
        conversation += f"{role}: {content}\n"

    # Ab agent ko poori conversation bhejna hai
    result = await Runner.run(
        agent,
        input=conversation,   # 👈 yahan poori history di
        run_config=config,
    )

    # Agent ka jawab
    response = result.final_output or "⚠ Sorry, I couldn't process that. Please try again."

    # History update karo
    history.append({"role": "assistant", "content": response})
    cl.user_session.set("history", history)

    # User ko reply bhejo
    await cl.Message(content=response).send()
