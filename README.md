# LiveKit Local Development Environment

This repository contains a collection of projects to facilitate local development and experimentation with [LiveKit](https://livekit.io/) and [LiveKit Agents](https://docs.livekit.io/agents/).

## Project Structure

The repository is organized as a monorepo with the following key components:

*   **`agents-playground/`**: A Next.js application designed for quickly prototyping and interacting with server-side agents built with the [LiveKit Agents Framework](https://github.com/livekit/agents). It allows you to connect to LiveKit WebRTC sessions and process or generate audio, video, and data streams.
    *   See [`agents-playground/README.md`](agents-playground/README.md:1) for detailed setup and usage instructions.
*   **`livekit-server/`**: Contains the LiveKit server executable (`livekit-server.exe`) and utility scripts:
    *   `server_start.bat`: Script to start the local LiveKit server.
    *   `get_access_token.bat`: Script to generate access tokens for connecting to the LiveKit server.
*   **`my-first-agent/`**: An example of a basic Python-based LiveKit agent. This can serve as a starting point for building your own custom agents.
    *   Refer to the code and comments within this directory for understanding its functionality. You might need to set up a Python environment and install dependencies from `requirements.txt`.
*   **`voice-assistant-frontend/`**: A Next.js starter template for a web-based voice assistant that uses LiveKit Agents. It supports voice interactions, transcriptions, and virtual avatars.
    *   See [`voice-assistant-frontend/README.md`](voice-assistant-frontend/README.md:1) for detailed setup and usage instructions.
*   **`voice-pipeline-agent-python/`**: A Python-based voice agent that demonstrates a voice pipeline using LiveKit.
    *   See [`voice-pipeline-agent-python/README.md`](voice-pipeline-agent-python/README.md:1) for detailed setup, environment configuration, and execution instructions.
*   **`Orpheus-FastAPI/`**: A high-performance Text-to-Speech (TTS) server with an OpenAI-compatible API. It offers multilingual support, emotion tags, and is optimized for RTX GPUs. It's typically started using the `orpheus_start.sh` script which manages Docker containers for the TTS engine.
    *   See [`Orpheus-FastAPI/README.md`](Orpheus-FastAPI/README.md:1) for detailed setup and usage instructions.
*   **`local-voice-ai/`**: A full-stack, Dockerized AI voice assistant. It integrates Speech-to-Text (STT), Large Language Models (LLM), and Text-to-Speech (TTS) capabilities, powered by LiveKit. The core agent logic is in `agent/myagent.py`.
    *   See [`local-voice-ai/README.md`](local-voice-ai/README.md:1) for detailed setup and usage instructions.

## Getting Started

To get started with this local development environment, follow these general steps:

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-name> # e.g., livekit-local-agent-setup
    ```

2.  **Set up the LiveKit Server**:
    *   Navigate to the `livekit-server/` directory.
    *   Run `server_start.bat` to start your local LiveKit server.
    *   You will likely need to configure your agents and frontends to connect to `ws://localhost:7880` (or the appropriate URL if your server configuration differs).

3.  **Explore Individual Projects**:
    *   Each sub-directory (e.g., `agents-playground/`, `voice-assistant-frontend/`, `Orpheus-FastAPI/`, `local-voice-ai/`) contains its own `README.md` file with specific instructions for setup, dependencies, and running the project.
    *   Typically, you will need to:
        *   Install dependencies (e.g., `npm install`, `pnpm install`, `pip install -r requirements.txt`).
        *   Configure environment variables (often by copying an `.env.example` or `env.local.example` to `.env` or `.env.local` and filling in API keys and URLs).
        *   Run the development server or agent script.

## Running with Docker Compose

For a fully containerized setup, you can use the provided Docker Compose files to launch the entire application stack (LiveKit Server, Orpheus-FastAPI, Faster Whisper, Ollama, Local Voice AI Agent, and Frontend) with a single command.

You can use the provided `./start.sh` script to simplify launching the stack. This script supports a `--build` or `-b` argument to force rebuilding Docker images (useful for the first run or after code changes), otherwise it uses cached images for faster startup.

**Prerequisites:**
*   Ensure you have [Docker](https://www.docker.com/get-started) and Docker Compose installed.
*   Ensure your system meets the requirements for the chosen Docker Compose file (especially GPU support for `docker-compose.yml`).

**Steps:**

1.  **Copy the environment example file:**
    Create a `.env` file at the root of the repository by copying the example:
    ```bash
    cp .env.example .env
    # On Windows CMD
    # copy .env.example .env
    ```
    Review and adjust the variables in the newly created `.env` file if necessary (e.g., API keys, model names).

2.  **Choose the appropriate Docker Compose file:**
    *   Use `docker-compose.yml` if you have a CUDA-compatible GPU and Docker is configured to use it.
    *   Use `docker-compose-cpu.yml` for CPU-only environments.

3.  **Launch the stack:**
    Open a terminal at the root of the repository and run the appropriate command.

    *   **Initial Build (or when Dockerfiles/context change):**
        Use the `--build` flag to build the images. This is necessary for the first time or after making changes to the Dockerfiles or the files they copy (like requirements.txt).

        *   **For GPU (using `docker-compose.yml`):**
            ```bash
            docker compose -f docker-compose.yml up --build
            ```

        *   **For CPU (using `docker-compose-cpu.yml`):**
            ```bash
            docker compose -f docker-compose-cpu.yml up --build
            ```
        This command will download necessary base images (LiveKit, Ollama, Faster Whisper, Llama.cpp, Curl), build the custom images, and start all services. This may take some time on the first run.

    *   **Subsequent Runs (using cached images):**
        For faster startup when no Dockerfile or build context changes have occurred, omit the `--build` flag. Docker Compose will use cached images.

        *   **For GPU (using `docker-compose.yml`):**
            ```bash
            docker compose -f docker-compose.yml up
            ```

        *   **For CPU (using `docker-compose-cpu.yml`):**
            ```bash
            docker compose -f docker-compose-cpu.yml up
            ```

4.  **Access the Frontend:**
    Once all services are running, open your browser and go to `http://localhost:3000`.

**Important Notes:**
*   The internal URLs used by the `local-voice-ai/agent/myagent.py` for STT, LLM, and TTS services will need to be updated to point to the service names defined in the Docker Compose file (e.g., `http://stt-api:8000/v1`, `http://ollama:11434/v1`, `http://orpheus-tts-api:5005/v1`). This update is not automatically handled by this Docker Compose setup and needs to be done manually in the agent's code or via environment variables if the agent supports it.
*   To stop the services, press `Ctrl+C` in the terminal where `docker compose up` is running, and then run:
    ```bash
    docker compose -f <your_chosen_compose_file>.yml down
    ```
    Add `-v` to remove volumes (like Ollama data) if needed.

---

## Workflow for Local Voice AI with Orpheus TTS

This section outlines the steps to run a complete local voice assistant demo using the LiveKit server, Orpheus-FastAPI for TTS, the local-voice-ai agent, and a frontend.

**Prerequisites:**
*   Ensure you have [Node.js](https://nodejs.org/), [Python](https://www.python.org/), `npm`, `pnpm`, `pip`, and [Docker](https://www.docker.com/get-started) installed.
*   Clone this repository and navigate into its root directory if you haven't already.
*   Ensure your system meets the requirements for `Orpheus-FastAPI` (especially if using GPU, CUDA-compatible GPU is recommended) and `local-voice-ai`.

---

**Step 1: Start LiveKit Server and Get Access Token**

The LiveKit server is the central hub for media and data relay.

1.  **Navigate to the server directory:**
    (From the repository root)
    ```bash
    cd livekit-server
    ```
2.  **Start the server:**
    Run the batch file:
    ```bash
    server_start.bat
    ```
    This typically starts the server using the command `livekit-server.exe --dev --bind 0.0.0.0` (as seen in [`livekit-server/server_start.bat`](livekit-server/server_start.bat:1)). The server will listen on `ws://localhost:7880`.

3.  **Generate an Access Token:**
    Client applications and agents need an access token to connect to the LiveKit server.
    *   In a **new terminal window/tab**, navigate to the `livekit-server` directory and run:
        ```bash
        get_access_token.bat
        ```
        This script (contents: `lk token create --api-key devkey --api-secret secret --join --room test_room --identity test_user --valid-for 24h` from [`livekit-server/get_access_token.bat`](livekit-server/get_access_token.bat:1)) generates a token. **Copy this token** for use in Step 4.

---

**Step 2: Start Faster Whisper STT + Orpheus TTS Servers**

These servers handle Speech-to-Text and Text-to-Speech processing.

1.  **Navigate to the Orpheus-FastAPI directory:**
    (From the repository root)
    ```bash
    cd Orpheus-FastAPI
    ```
2.  **Start the Docker containers:**
    Execute the script (ensure Docker Desktop is running):
    ```bash
    ./orpheus_start.sh
    ```
    This script (typically `docker compose -f docker-compose-gpu.yml up` as per [`Orpheus-FastAPI/orpheus_start.sh`](Orpheus-FastAPI/orpheus_start.sh:1)) will spin up the necessary Docker containers for STT (Faster Whisper) and TTS (Orpheus). Ensure Docker is running and your system is configured for GPU use if using the GPU compose file. This might take some time on the first run as images are downloaded.

---

**Step 3 (New): Start Ollama LLM Service**

This service provides the Large Language Model.

1.  **Open a new terminal window/tab.**
2.  **Run the Ollama model:**
    (Ensure Docker Desktop is running if you intend to use Ollama via Docker, or that Ollama is installed locally)
    ```bash
    ollama run llama3.2:3b --keepalive -1m
    ```
    This command will download the `llama3.2:3b` model if it's not already present and then start serving it. The `--keepalive -1m` flag attempts to keep the model loaded in memory. This service typically runs on `http://localhost:11434`.

---

**Step 4: Start the Local Voice AI Agent**

**Step 5: Start Frontend and Connect**

This agent connects to LiveKit and orchestrates the STT, LLM, and TTS services.

1.  **Navigate to the local-voice-ai agent directory:**
    (From the repository root)
    ```bash
    cd local-voice-ai/agent
    ```
2.  **Set up Python Environment (if first time):**
    *   It's highly recommended to use a Python virtual environment.
        ```bash
        python -m venv venv
        # On Windows
        .\venv\Scripts\activate
        # On macOS/Linux
        # source venv/bin/activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
        (Refer to [`local-voice-ai/README.md`](local-voice-ai/README.md:1) for full setup, including potential Docker setup for the agent itself if preferred).
3.  **Configure Environment Variables:**
    *   Ensure you have a `.env` file in the `local-voice-ai/agent/` directory (you can copy from `.env.example` if it exists or create one).
    *   Key variables for local LiveKit server connection:
        ```env
        LIVEKIT_URL=ws://localhost:7880
        LIVEKIT_API_KEY=devkey
        LIVEKIT_API_SECRET=secret
        ```
    *   The agent [`myagent.py`](local-voice-ai/agent/myagent.py:1) is configured by default to use STT at `http://localhost:8000/v1` (from Orpheus-FastAPI's STT service) and TTS at `http://localhost:5005/v1` (Orpheus TTS). Ensure these ports match your `Orpheus-FastAPI` setup.
4.  **Run the Agent:**
    ```bash
    python myagent.py dev
    ```
    The agent will attempt to connect to the LiveKit server room (e.g., `test_room` if using the default token from `get_access_token.bat`).

---

**Step 4: Start Frontend and Connect**

You can use either the Agents Playground or the Voice Assistant Frontend.

1.  **Start Agents Playground:**
    *   Navigate to `agents-playground/` (from the repository root).
    *   Install dependencies (if first time): `npm install`.
    *   Configure `.env.local` (copy from `.env.example` if needed). Ensure these values:
        ```env
        LIVEKIT_API_KEY=devkey
        LIVEKIT_API_SECRET=secret
        NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
        ```
    *   Run the development server: `npm run dev`.
    *   Open the playground in your browser (usually `http://localhost:3000` or `http://localhost:3001` if port 3000 is in use).
    *   In the playground UI, input the LiveKit Server URL: `ws://localhost:7880` and the **Access Token** you copied in Step 1. Select a room name (e.g., `test_room`).

2.  **Alternative: Voice Assistant Frontend (if issues with Playground or preferred):**
    *   If Agents Playground is running on port 3000, stop it.
    *   Navigate to `voice-assistant-frontend/` (from the repository root).
    *   Follow setup instructions in [`voice-assistant-frontend/README.md`](voice-assistant-frontend/README.md:1):
        *   Install dependencies (if first time): `pnpm install`.
        *   Configure `.env.local` (copy from `.env.example` if needed). Ensure these values:
            ```env
            LIVEKIT_URL=ws://localhost:7880
            LIVEKIT_API_KEY=devkey
            LIVEKIT_API_SECRET=secret
            ```
    *   Run the development server: `pnpm dev`.
    *   Open the frontend in your browser (usually `http://localhost:3000`).
    *   This frontend typically uses the environment variables to establish a connection. You might need to ensure the room name matches what the agent and token expect (e.g., `test_room`). The token from Step 1 is implicitly used via the API key/secret for server-side token generation in this frontend's default setup. If it prompts for a token directly, use the one from Step 1.

---

**Troubleshooting Notes:**
*   Ensure all services (LiveKit, Orpheus-FastAPI containers, Python agent, Frontend) are running in separate terminal windows/tabs.
*   Check terminal outputs for errors in each component.
*   Verify Docker Desktop is running and has sufficient resources.
*   Confirm firewall settings are not blocking local connections between services (e.g., to ports 7880, 8000, 5005, 11434).
*   Consult individual project `README.md` files for more detailed setup and troubleshooting.

---


## Prerequisites
*   Ensure all services (LiveKit, Orpheus-FastAPI containers, Python agent, Frontend) are running in separate terminal windows/tabs.
*   Check terminal outputs for errors in each component.
*   Verify Docker Desktop is running and has sufficient resources.
*   Confirm firewall settings are not blocking local connections between services (e.g., to ports 7880, 8000, 5005, 11434).
*   Consult individual project `README.md` files for more detailed setup and troubleshooting.

## Prerequisites

Ensure you have the following installed:

*   [Node.js](https://nodejs.org/) (for Next.js frontends and the agents playground)
*   [Python](https://www.python.org/) (for Python-based agents)
*   `npm` and/or `pnpm` (package managers for Node.js projects)
*   `pip` (package manager for Python)
*   [Docker](https://www.docker.com/get-started) (for `Orpheus-FastAPI` and `local-voice-ai` components)

## Contributing

Contributions to improve this local development setup or any of its components are welcome. Please refer to the individual project `README.md` files for any specific contribution guidelines.

---

This `README.md` provides a high-level overview. For detailed information, please consult the `README.md` files within each respective project directory.