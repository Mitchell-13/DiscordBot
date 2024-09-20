
---

# Snazzards Discord Bot

## Project Description
This project is a customizable Discord bot that integrates AI functionalities using OpenAI's API.

## Features
- AI-based responses using OpenAI.
- Modular design to easily add more features through cogs.

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
        "OPEN_AI_KEY": "your-openai-api-key"
    }
    ```

6. **Run the bot**:  
    ```bash
    python main.py
    ```

## Usage
- Once the bot is running, interact with it in your Discord server using the configured command prefix.
- Example command:
    ```
    $help
    ```

## File Structure
- `main.py`: The main script that runs the bot.
- `config.json`: Stores the bot token, command prefix, and API keys.
- `requirements.txt`: Contains the Python dependencies.
- `cogs/`: Contains modular commands and features for the bot, such as the AI capabilities in `open_ai/cog.py`.

---
