# OpenAI/Piper Discord Bot

## Project Description
This project is a customizable Discord bot that integrates AI functionalities using OpenAI's API and Piper text-to-speech. Due to dependencies, this will not work on Windows Machines.

## Features
- AI-based responses using OpenAI.
- Text-to-speech using Piper TTS.
- Modular design to easily add more features through cogs.
- Restricted Codex workflow command: `$codexchange <request>` for approved users.
- Supports full AI PR workflow by dispatching a GitHub Actions workflow in your target repo.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Mitchell-13/DiscordBot.git
    ```

2. **Navigate to the project directory:**
    ```bash
    cd DiscordBot
    ```

3. **Install dependencies:**
    Install the required Python libraries using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create a Discord Bot**:  
    Before proceeding, you will need to create a bot on the [Discord Developer Portal](https://discord.com/developers/applications) and retrieve the bot token. This token will be used in the `config.json` file.

5. **Configuration**:  
    - Update the `config.json` file with your bot’s token, desired command prefix, and OpenAI API key.
    - Example `config.json` structure:
    ```json
    {
        "client_token": "your-discord-bot-token",
        "command_prefix": "$",
        "OPEN_AI_KEY": "your-openai-api-key",
        "GITHUB_TOKEN": "github-personal-access-token",
        "GITHUB_REPO": "owner/repository",
        "GITHUB_CHANGE_WORKFLOW_ID": "codex-pr-worker.yml",
        "GITHUB_CHANGE_WORKFLOW_REF": "main",
        "GITHUB_CHANGE_REQUEST_LABELS": ["ai-change"],
        "CODEX_ALLOWED_USERS": [123456789012345678],
        "CODEX_REVIEWER_DISCORD_ID": 123456789012345678
    }
    ```

6. **Full workflow setup in the target website repo (required for actual code changes):**
   - Copy `.github/workflows/codex-pr-worker-template.yml` from this repository into your website repo as `.github/workflows/codex-pr-worker.yml`.
   - Replace the placeholder “Run Codex edit step” section with your real Codex/OpenAI code-edit automation.
   - In the website repo, add required repository secrets:
     - `OPENAI_API_KEY` (or whichever key your workflow uses for AI edits)
     - `DISCORD_WEBHOOK_URL` (Discord webhook used to ping you when PR is opened)
   - Ensure your bot’s `GITHUB_TOKEN` has permissions to dispatch workflows in `GITHUB_REPO` (typically repo scope / actions:write for fine-grained tokens).

7. **Piper TTS Setup**:  
   - Download the Piper TTS model files and place them in a folder called `tts_voices/`.
   - The model files should be named `model.onnx` and `model.onnx.json`.
   - Ensure that both the `.onnx` and `.json` files are present in the `tts_voices/` directory.

8. **Run the bot**:  
 ```bash
 python main.py
 ```

## Usage
- Once the bot is running, interact with it in your Discord server using the configured command prefix.
- Example command:
 ```
 $help
 ```
- Restricted Codex workflow command:
 ```
 $codexchange Update the About page copy and add a CTA button
 ```

Behavior of `$codexchange`:
- If `GITHUB_CHANGE_WORKFLOW_ID` is set: dispatches the workflow in your target repo (full workflow path).
- If `GITHUB_CHANGE_WORKFLOW_ID` is missing: falls back to creating a labeled GitHub issue.

## File Structure
- `main.py`: The main script that runs the bot.
- `config.json`: Stores the bot token, command prefix, and API keys.
- `requirements.txt`: Contains the Python dependencies.
- `cogs/`: Contains modular commands and features for the bot, such as the AI capabilities in `open_ai/cog.py`.
- `.github/workflows/codex-pr-worker-template.yml`: Template workflow for AI edit -> PR -> Discord reviewer ping.
- `tts_voices/`: Contains the Piper TTS model files (`model.onnx` and `model.onnx.json`).
