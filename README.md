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

## Vote report

Bots cannot read chat history, so [analyze_votes.py](analyze_votes.py) reads past polls as a regular Telegram user account and reports who voted for each option.

1. Get `api_id` and `api_hash` at <https://my.telegram.org> → API development tools.
2. On your own computer, run `make session` (or `uv run python make_session.py`), log in with your phone number (`TG_PHONE` in `.env`, or typed when asked) and the code Telegram sends, and copy the printed session string. It grants full access to the account: keep it secret.
3. Add the Actions secrets `TG_API_ID`, `TG_API_HASH` and `TG_SESSION` (`CHAT_ID` and `THREAD_ID` are reused).
4. Run the [Analyze poll votes](.github/workflows/analyze-votes.yml) workflow from the Actions tab and choose how many months to analyze.

The table appears in the run's summary; `summary.csv` and `votes.csv` are attached as the `vote-report` artifact. Telegram only shows a poll's voters to accounts that voted in it, so polls the account did not vote in are skipped and listed in the report.
