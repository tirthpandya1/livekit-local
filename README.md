# LiveKit Local Development Environment

This repository contains a collection of projects to facilitate local development and experimentation with [LiveKit](https://livekit.io/) and [LiveKit Agents](https://docs.livekit.io/agents/).

## Project Structure

The repository is organized as a monorepo with the following key components:

*   **`agents-playground/`**: A Next.js application designed for quickly prototyping and interacting with server-side agents built with the [LiveKit Agents Framework](https://github.com/livekit/agents). It allows you to connect to LiveKit WebRTC sessions and process or generate audio, video, and data streams.
    *   See [`agents-playground/README.md`](livekit-local/agents-playground/README.md:1) for detailed setup and usage instructions.
*   **`livekit-server/`**: Contains the LiveKit server executable (`livekit-server.exe`) and utility scripts:
    *   `server_start.bat`: Script to start the local LiveKit server.
    *   `get_access_token.bat`: Script to generate access tokens for connecting to the LiveKit server.
*   **`my-first-agent/`**: An example of a basic Python-based LiveKit agent. This can serve as a starting point for building your own custom agents.
    *   Refer to the code and comments within this directory for understanding its functionality. You might need to set up a Python environment and install dependencies from `requirements.txt`.
*   **`voice-assistant-frontend/`**: A Next.js starter template for a web-based voice assistant that uses LiveKit Agents. It supports voice interactions, transcriptions, and virtual avatars.
    *   See [`voice-assistant-frontend/README.md`](livekit-local/voice-assistant-frontend/README.md:1) for detailed setup and usage instructions.
*   **`voice-pipeline-agent-python/`**: A Python-based voice agent that demonstrates a voice pipeline using LiveKit.
    *   See [`voice-pipeline-agent-python/README.md`](livekit-local/voice-pipeline-agent-python/README.md:1) for detailed setup, environment configuration, and execution instructions.

## Getting Started

To get started with this local development environment, follow these general steps:

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd livekit-local
    ```

2.  **Set up the LiveKit Server**:
    *   Navigate to the `livekit-server/` directory.
    *   Run `server_start.bat` to start your local LiveKit server.
    *   You will likely need to configure your agents and frontends to connect to `ws://localhost:7880` (or the appropriate URL if your server configuration differs).

3.  **Explore Individual Projects**:
    *   Each sub-directory (e.g., `agents-playground/`, `voice-assistant-frontend/`, `voice-pipeline-agent-python/`) contains its own `README.md` file with specific instructions for setup, dependencies, and running the project.
    *   Typically, you will need to:
        *   Install dependencies (e.g., `npm install`, `pnpm install`, `pip install -r requirements.txt`).
        *   Configure environment variables (often by copying an `.env.example` or `env.local.example` to `.env` or `.env.local` and filling in API keys and URLs).
        *   Run the development server or agent script.

## Detailed End-to-End Workflow

This section outlines the steps to run a complete local voice assistant demo using the `livekit-server`, `voice-pipeline-agent-python`, and `voice-assistant-frontend`. The `agents-playground` can then be used for further testing and debugging.

**Prerequisites:**
*   Ensure you have [Node.js](https://nodejs.org/), [Python](https://www.python.org/), `npm`, `pnpm`, and `pip` installed, as mentioned in the main "Prerequisites" section.
*   Clone this repository and navigate into the `livekit-local` directory if you haven't already.

---

**Step 1: Start the LiveKit Server**

The LiveKit server is the central hub for media and data relay.

1.  **Navigate to the server directory:**
    ```bash
    cd livekit-server
    ```
2.  **Start the server:**
    Run the batch file:
    ```bash
    server_start.bat
    ```
    This typically starts the server using the command `livekit-server.exe --dev --bind 0.0.0.0`.
    The server will listen on `ws://localhost:7880` (WebSocket) and `http://localhost:7881` (WebRTC over TCP, if enabled by default config). The default API key is `devkey` and secret is `secret` for development mode.

3.  **Generate an Access Token (Required by Frontends/Agents):**
    Client applications and agents need an access token to connect to the LiveKit server.
    *   **Using the provided script:**
        In the `livekit-server` directory, you can run:
        ```bash
        get_access_token.bat
        ```
        This script uses the LiveKit CLI (`lk`) with the default dev key/secret to generate a token for `room: test_room` and `identity: test_user`. The command inside is:
        `lk token create --api-key devkey --api-secret secret --join --room test_room --identity test_user --valid-for 24h`

    *   **Using LiveKit CLI directly (if installed and in PATH):**
        You can generate tokens with more specific permissions or identities using the `lk token create` command. For example:
        ```bash
        lk token create --api-key devkey --api-secret secret --join --room my-custom-room --identity my-user-identity --valid-for 1h
        ```
        Refer to the [LiveKit CLI documentation](https://docs.livekit.io/cli/) for more options.
        The generated token will be needed by the frontend applications to connect.

---

**Step 2: Start the Python Voice Agent (`voice-pipeline-agent-python`)**

This agent processes audio and interacts with AI services.

1.  **Navigate to the agent directory:**
    From the `livekit-local` root:
    ```bash
    cd voice-pipeline-agent-python
    ```
2.  **Set up Python Environment (if first time):**
    *   Create a virtual environment:
        ```bash
        python -m venv venv
        ```
    *   Activate the virtual environment:
        ```bash
        .\venv\Scripts\activate
        ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Download necessary agent files/models:**
    ```bash
    python agent.py download-files
    ```
5.  **Configure Environment Variables:**
    *   Ensure you have a `.env.local` file in the `livekit-local/voice-pipeline-agent-python/` directory. If not, copy `.env.example` (if present) or create one with the following content, replacing placeholder API keys with your actual keys:
        ```env
        LIVEKIT_URL=ws://localhost:7880
        LIVEKIT_API_KEY=devkey
        LIVEKIT_API_SECRET=secret

        # Replace with your actual API keys
        DEEPGRAM_API_KEY=YOUR_DEEPGRAM_API_KEY
        CARTESIA_API_KEY=YOUR_CARTESIA_API_KEY
        # OPENAI_API_KEY=YOUR_OPENAI_API_KEY (if using OpenAI directly instead of local Ollama)
        ```
        *Note: The provided `agent.py` is configured to use a local Ollama instance for LLM by default. If you intend to use OpenAI's API directly, you'll need to adjust `agent.py` and provide `OPENAI_API_KEY`.*

6.  **Run the Agent:**
    ```bash
    python agent.py dev
    ```
    The agent will connect to the local LiveKit server.

---

**Step 3: Start the Voice Assistant Frontend (`voice-assistant-frontend`)**

This Next.js application provides the user interface for interacting with the voice agent.

1.  **Navigate to the frontend directory:**
    From the `livekit-local` root:
    ```bash
    cd voice-assistant-frontend
    ```
2.  **Install Dependencies:**
    ```bash
    pnpm install
    ```
3.  **Configure Environment Variables:**
    *   Create or update the `.env.local` file in the `livekit-local/voice-assistant-frontend/` directory.
    *   **Important:** Ensure it points to your **local** LiveKit server and uses the correct development credentials. The default cloud configuration will not work with your local server and agent.
        ```env
        LIVEKIT_URL=ws://localhost:7880
        LIVEKIT_API_KEY=devkey
        LIVEKIT_API_SECRET=secret
        ```
4.  **Run the Frontend Development Server:**
    ```bash
    pnpm dev
    ```
5.  **Access the Frontend:**
    Open your browser and go to `http://localhost:3000`. You should be able to connect to a room and interact with the `voice-pipeline-agent-python`.

---

**Step 4: (Optional) Test with Agents Playground (`agents-playground`)**

The Agents Playground is useful for more direct interaction with agents, debugging, and prototyping.

1.  **Navigate to the playground directory:**
    From the `livekit-local` root:
    ```bash
    cd agents-playground
    ```
2.  **Install Dependencies:**
    ```bash
    npm install
    ```
3.  **Configure Environment Variables:**
    *   Ensure you have a `.env.local` file in `livekit-local/agents-playground/`. If not, copy `.env.example` to `.env.local`.
    *   **Important:** Modify `NEXT_PUBLIC_LIVEKIT_URL` to point to your local **insecure** WebSocket server:
        ```env
        LIVEKIT_API_KEY=devkey
        LIVEKIT_API_SECRET=secret
        NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880 # Ensure this is 'ws' not 'wss' for the default dev server

        # Other NEXT_PUBLIC_APP_CONFIG settings can be kept as default or customized
        NEXT_PUBLIC_APP_CONFIG="
        title: 'LiveKit Agents Playground'
        description: 'A virtual workbench for your multimodal AI agents.'
        github_link: 'https://github.com/livekit/agents-playground'
        video_fit: 'cover' # 'contain' or 'cover'
        settings:
          editable: true # Should the user be able to edit settings in-app
          theme_color: 'cyan'
          chat: true  # Enable or disable chat feature
          outputs:
            audio: true # Enable or disable audio output
            video: true # Enable or disable video output
          inputs:
            mic: true    # Enable or disable microphone input
            camera: true # Enable or disable camera input
            sip: true    # Enable or disable SIP input
        "
        ```
4.  **Run the Playground Development Server:**
    ```bash
    npm run dev
    ```
5.  **Access the Playground:**
    Open your browser and go to `http://localhost:3000` (or `http://localhost:3001` if port 3000 is already in use by the `voice-assistant-frontend`).
    You can then connect to a room (e.g., `test_room`) and your agent should join, allowing you to interact with it.

By following these steps, you can run the complete LiveKit voice agent setup locally for development and testing. Remember to start components in separate terminal windows/tabs.

## Prerequisites

Ensure you have the following installed:

*   [Node.js](https://nodejs.org/) (for Next.js frontends and the agents playground)
*   [Python](https://www.python.org/) (for Python-based agents)
*   `npm` and/or `pnpm` (package managers for Node.js projects)
*   `pip` (package manager for Python)

## Contributing

Contributions to improve this local development setup or any of its components are welcome. Please refer to the individual project `README.md` files for any specific contribution guidelines.

---

This `README.md` provides a high-level overview. For detailed information, please consult the `README.md` files within each respective project directory.