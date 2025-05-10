from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import ChatContext, ChatMessage

from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

import json

load_dotenv()

# Initialize index with fallback
index = VectorStoreIndex([])

# Storage and documents configuration
THIS_DIR = Path(__file__).parent
PERSIST_DIR = THIS_DIR / "query-engine-storage"
DOCUMENTS_DIR = THIS_DIR / "data"

try:
    if not PERSIST_DIR.exists():
        # Ensure documents directory exists
        if not DOCUMENTS_DIR.exists():
            print(f"Warning: Documents directory {DOCUMENTS_DIR} does not exist.")
        else:
            # load the documents and create the index
            documents = SimpleDirectoryReader(DOCUMENTS_DIR).load_data()
            
            # Create index only if documents are available
            if documents:
                index = VectorStoreIndex.from_documents(documents)
                # store it for later
                index.storage_context.persist(persist_dir=PERSIST_DIR)
                print(f"Index created and stored in {PERSIST_DIR}")
    else:
        # load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print(f"Loaded existing index from {PERSIST_DIR}")
except Exception as e:
    print(f"Error initializing index: {e}")

# Query function for RAG
async def query_info(query: str) -> str:
    """Get more information about a specific topic"""
    query_engine = index.as_query_engine(use_async=True)
    try:
        res = await query_engine.aquery(query)
        print("Query result:", res)
        return str(res)
    except Exception as e:
        print(f"Error during query: {e}")
        return "Sorry, I couldn't find information about that."


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")


async def on_user_turn_completed(
    self, turn_ctx: ChatContext, new_message: ChatMessage,
) -> None:
    # RAG function definition omitted for brevity
    def my_rag_lookup(text: str) -> str:
        return ""
    rag_content = await my_rag_lookup(new_message.text_content())
    turn_ctx.add_message(
        role="assistant", 
        content=f"Additional information relevant to the user's next message: {rag_content}"
    )

async def entrypoint(ctx: agents.JobContext):
    # Simple lookup, but you could use a database or API here if needed
    metadata = json.loads(ctx.job.metadata)
    user_name = metadata.get("user_name", "User")

    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM.with_ollama(
            model="gemma3:4b",
            base_url="http://localhost:11434/v1",
        ),
        tts=cartesia.TTS(
            voice={"id": "694f9389-aac1-45b6-b726-9d9369183238"},
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        tools=[query_info],  # Add the query_info tool
    )

    initial_ctx = ChatContext()
    initial_ctx.add_message(
        role="assistant",
        content=f"The user's name is {user_name}."
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=initial_ctx),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))