# volleyball-bot

Telegram bot that posts a volleyball attendance poll to a group chat.

## Setup

1. Install [uv](https://docs.astral.sh/uv/). Dependencies are installed into `.venv` automatically on first run.
2. Copy the example env file and fill in your values:

   ```bash
   cp .env.example .env
   ```

   | Variable    | Description                    |
   |-------------|--------------------------------|
   | `BOT_TOKEN` | Telegram bot token             |
   | `CHAT_ID`   | Chat ID the poll is posted to  |
   | `THREAD_ID` | Optional forum topic ID; leave unset for private chats |

## Run

```bash
uv run --env-file .env python run.py
```

Or with make:

```bash
make run
```

Run `make` (or `make help`) to list available commands.

## Scheduled run

The [Send volleyball poll](.github/workflows/send-poll.yml) GitHub Actions workflow posts the poll every Thursday at 13:00 UTC. It reads `BOT_TOKEN`, `CHAT_ID` and `THREAD_ID` from the repository's Actions secrets. It can also be started manually from the Actions tab, but the script only posts on Thursdays.
