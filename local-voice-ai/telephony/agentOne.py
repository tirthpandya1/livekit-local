import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, get_job_context
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero, groq
from livekit.agents import ChatContext, ChatMessage
from sentence_transformers import SentenceTransformer
import faiss
import asyncio
from functools import partial
from livekit import api
import json

load_dotenv()

logger = logging.getLogger("agentOne") # Changed logger name
logger.setLevel(logging.INFO)

# Add FileHandler to the logger
log_file_path = Path(__file__).parent / "agentOne.log"
file_handler = logging.FileHandler(log_file_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# load a small embedding model once
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# load all your docs
docs = []
# Adjusted docs_dir path to be relative to this file's parent's parent then agent/docs
# This assumes docs are in livekit-local/local-voice-ai/agent/docs
docs_dir_path = Path(__file__).parent.parent / "agent" / "docs"

if docs_dir_path.exists():
    for fn in os.listdir(docs_dir_path):
        with open(docs_dir_path / fn, encoding="utf-8") as f:
            docs.append(f.read())

# embed and build FAISS index
if docs:
    embs = embed_model.encode(docs, show_progress_bar=False)
    dim = embs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embs)
else:
    dim = embed_model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatL2(dim)
    logger.warning(f"No documents found in {docs_dir_path}. RAG will return empty context.")

async def rag_lookup(query: str) -> str:
    """Perform RAG lookup for a given query"""
    loop = asyncio.get_running_loop()

    q_emb = await loop.run_in_executor(None, lambda: embed_model.encode([query]))
    D, I = await loop.run_in_executor(None, lambda: index.search(q_emb, min(3, index.ntotal)))

    ctx = ""
    if index.ntotal > 0:
        ctx = "\n\n---\n\n".join(docs[i] for i in I[0])

    logger.info(f"RAG content: {ctx}") # Changed print to logger.info

    return ctx

# Reused LocalAgent class from myagent.py
class LocalAgent(Agent):
    def __init__(self) -> None:
        stt = openai.STT(
            base_url="http://localhost:8000/v1",
            model="Systran/faster-whisper-large-v3",
            detect_language=True
            )
        llm = openai.LLM(
            base_url="http://localhost:11434/v1",
            model="llama3.2:3b"
            )
        tts = groq.TTS(
            base_url="http://localhost:5005/v1",
            voice="ऋतिका"
            )
        vad_inst = silero.VAD.load()
        super().__init__(
            instructions="""
                You are a helpful agent.
                Never ever use emojis. Everything you say should be in plain text, since it will be spoken out loud.
                Keep your responses short and concise. Never more than a sentence or two. The User will either speak in Hindi, English or a combination of both
            """,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad_inst
        )

        # Metrics logging (copied from myagent.py)
        def llm_metrics_wrapper(metrics):
            import asyncio
            asyncio.create_task(self.on_llm_metrics_collected(metrics))
        llm.on("metrics_collected", llm_metrics_wrapper)

        def stt_metrics_wrapper(metrics):
            import asyncio
            asyncio.create_task(self.on_stt_metrics_collected(metrics))
        stt.on("metrics_collected", stt_metrics_wrapper)

        def eou_metrics_wrapper(metrics):
            import asyncio
            asyncio.create_task(self.on_eou_metrics_collected(metrics))
        stt.on("eou_metrics_collected", eou_metrics_wrapper)

        def tts_metrics_wrapper(metrics):
            import asyncio
            asyncio.create_task(self.on_tts_metrics_collected(metrics))
        tts.on("metrics_collected", tts_metrics_wrapper)

        def vad_metrics_wrapper(event):
            import asyncio
            asyncio.create_task(self.on_vad_event(event))
        vad_inst.on("metrics_collected", vad_metrics_wrapper)

    async def on_llm_metrics_collected(self, metrics):
        logger.info(f"LLM Metrics: {{" +
            f"\'type\': {metrics.type}, " +
            f"\'label\': {metrics.label}, " +
            f"\'request_id\': {metrics.request_id}, " +
            f"\'timestamp\': {metrics.timestamp if isinstance(metrics.timestamp, (int, float)) else metrics.timestamp.isoformat() if metrics.timestamp else None}, " +
            f"\'duration\': {metrics.duration}, " +
            f"\'ttft\': {getattr(metrics, 'ttft', None)}, " +
            f"\'cancelled\': {getattr(metrics, 'cancelled', None)}, " +
            f"\'completion_tokens\': {getattr(metrics, 'completion_tokens', None)}, " +
            f"\'prompt_tokens\': {getattr(metrics, 'prompt_tokens', None)}, " +
            f"\'total_tokens\': {getattr(metrics, 'total_tokens', None)}, " +
            f"\'tokens_per_second\': {getattr(metrics, 'tokens_per_second', None)}" +
            "}}")

    async def on_stt_metrics_collected(self, metrics):
        logger.info(f"STT Metrics: {{" +
            f"\'type\': {metrics.type}, " +
            f"\'label\': {metrics.label}, " +
            f"\'request_id\': {metrics.request_id}, " +
            f"\'timestamp\': {metrics.timestamp if isinstance(metrics.timestamp, (int, float)) else metrics.timestamp.isoformat() if metrics.timestamp else None}, " +
            f"\'duration\': {metrics.duration}, " +
            f"\'speech_id\': {getattr(metrics, 'speech_id', None)}, " +
            f"\'error\': {str(getattr(metrics, 'error', None)) if getattr(metrics, 'error', None) else None}, " +
            f"\'streamed\': {getattr(metrics, 'streamed', None)}, " +
            f"\'audio_duration\': {getattr(metrics, 'audio_duration', None)}" +
            "}}")

    async def on_eou_metrics_collected(self, metrics):
        logger.info(f"EOU Metrics: {{" +
            f"\'type\': {metrics.type}, " +
            f"\'label\': {metrics.label}, " +
            f"\'timestamp\': {metrics.timestamp if isinstance(metrics.timestamp, (int, float)) else metrics.timestamp.isoformat() if metrics.timestamp else None}, " +
            f"\'end_of_utterance_delay\': {getattr(metrics, 'end_of_utterance_delay', None)}, " +
            f"\'transcription_delay\': {getattr(metrics, 'transcription_delay', None)}, " +
            f"\'speech_id\': {getattr(metrics, 'speech_id', None)}, " +
            f"\'error\': {str(getattr(metrics, 'error', None)) if getattr(metrics, 'error', None) else None}" +
            "}}")

    async def on_tts_metrics_collected(self, metrics):
        logger.info(f"TTS Metrics: {{" +
            f"\'type\': {metrics.type}, " +
            f"\'label\': {metrics.label}, " +
            f"\'request_id\': {metrics.request_id}, " +
            f"\'timestamp\': {metrics.timestamp if isinstance(metrics.timestamp, (int, float)) else metrics.timestamp.isoformat() if metrics.timestamp else None}, " +
            f"\'ttfb\': {getattr(metrics, 'ttfb', None)}, " +
            f"\'duration\': {metrics.duration}, " +
            f"\'audio_duration\': {getattr(metrics, 'audio_duration', None)}, " +
            f"\'cancelled\': {getattr(metrics, 'cancelled', None)}, " +
            f"\'characters_count\': {getattr(metrics, 'characters_count', None)}, " +
            f"\'streamed\': {getattr(metrics, 'streamed', None)}, " +
            f"\'speech_id\': {getattr(metrics, 'speech_id', None)}, " +
            f"\'error\': {str(getattr(metrics, 'error', None)) if getattr(metrics, 'error', None) else None}" +
            "}}")

    async def on_vad_event(self, event):
        pass # Changed None to pass

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage,
    ) -> None:
        rag_content = await rag_lookup(new_message.text_content)
        if rag_content:
            turn_ctx.add_message(
                role="user",
                content=f"Additional information relevant to the user\'s next message: {rag_content}"
            )
            logger.info(f"Added RAG content to chat context: {rag_content}")

# Added from LiveKit Telephony Docs
async def hangup_call():
    ctx = get_job_context()
    if ctx is None:
        logger.warning("Not running in a job context, cannot hang up.")
        return
    
    logger.info(f"Hanging up call for room: {ctx.room.name}")
    try:
        await ctx.api.room.delete_room(
            api.DeleteRoomRequest(
                room=ctx.room.name,
            )
        )
        logger.info(f"Successfully deleted room: {ctx.room.name}")
    except Exception as e:
        logger.error(f"Error hanging up call: {e}")


async def entrypoint(ctx: JobContext):
    logging.info(f"Agent connected for job: {ctx.job.id}, room: {ctx.room.name}")
    # Example: Accessing metadata
    metadata = json.loads(ctx.job.metadata) if ctx.job.metadata else {}
    phone_number_to_dial = metadata.get("phone_number")
    participant_identity = metadata.get("participant_identity", phone_number_to_dial)

    if not phone_number_to_dial:
        logging.error("No phone_number provided in metadata")
        return

    logging.info(
        f"Received dial_info: phone_number={phone_number_to_dial}, participant_identity={participant_identity}"
    )

    sip_trunk_id = "ST_mvPx65tTBegY"  # Use the SIP trunk ID created earlier
    sip_dispatch_rule_id = (
        "SR_yourDispatchRuleId"  # Replace with your dispatch rule if needed
    )

    try:
        logging.info(
            f"Attempting to dial {phone_number_to_dial} using trunk {sip_trunk_id} with identity {participant_identity}"
        )
        # Create a SIP participant (outbound call)
        # Note: `create_sip_participant` will automatically join the participant to the current room.
        await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
            sip_trunk_id=sip_trunk_id,
            # sip_dispatch_rule_id=sip_dispatch_rule_id, # Optional: if you have specific dispatch rules
            room_name=ctx.room.name,
            participant_identity=participant_identity, # Identity for the SIP participant in the LiveKit room
            outbound_number=phone_number_to_dial, # E.164 format
            # outbound_sip_uri="sip:user@example.com" # Alternatively, specify a direct SIP URI
            # dtmf_relay=sip.DTMFRelay.RFC2833, # Optional: DTMF relay method
        ))
        logging.info(f"Successfully initiated call to {phone_number_to_dial}")

        # The agent's job is done after initiating the call for this simple example.
        # In a real agent, you would likely have more logic here to interact with the call.

    except api.TwirpError as e:
        logging.error(f"Error creating SIP participant: {e.message}, SIP status: {e.meta.get('sip_status_code')} {e.meta.get('sip_reason_phrase')}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if ctx: # Check if ctx is not None
            logging.info("Shutting down job context.")
            await ctx.shutdown() # Shutdown the job context


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="my-telephony-agent", # Required for explicit dispatch
        job_memory_warn_mb=1500
    )) 