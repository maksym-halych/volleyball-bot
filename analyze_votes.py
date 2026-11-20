"""Count who voted in the volleyball polls over the last few months.

Telegram bots cannot read chat history, so this script logs in as a regular
user account (via a Telethon string session) and reads the voters of each
non-anonymous poll the bot posted in the topic.

Writes two CSV files to OUTPUT_DIR and, when run in GitHub Actions, a table to
the job summary.
"""

import asyncio
import csv
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import PollVoteRequiredError
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetPollVotesRequest
from telethon.tl.types import MessageMediaPoll, MessagePeerVote, MessagePeerVoteMultiple

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ["TG_SESSION"]
CHAT_ID = int(os.environ["CHAT_ID"])
THREAD_ID = int(os.environ["THREAD_ID"]) if os.environ.get("THREAD_ID") else None
MONTHS = int(os.environ.get("MONTHS") or 3)
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR") or "vote-report")

POLL_PREFIX = "Волейбол"
OPTIONS = ["Буду", "Не буду", "+1", "+2", "Стаю в чергу"]
PLAY_DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{4}")


def text_of(value) -> str:
    """Poll texts are TextWithEntities in newer layers and str in older ones."""
    return getattr(value, "text", value)


def display_name(user) -> str:
    if user is None:
        return "?"
    name = " ".join(filter(None, [user.first_name, user.last_name])) or "?"
    return f"{name} (@{user.username})" if user.username else name


async def fetch_votes(client, chat, message, poll):
    """Return {user_id: [option texts]} and {user_id: user} for one poll."""
    option_text = {a.option: text_of(a.text) for a in poll.answers}
    votes: dict[int, list[str]] = {}
    users = {}
    offset = None
    while True:
        result = await client(
            GetPollVotesRequest(peer=chat, id=message.id, limit=50, offset=offset)
        )
        users.update({u.id: u for u in result.users})
        for vote in result.votes:
            user_id = getattr(vote.peer, "user_id", None)
            if user_id is None:
                continue
            if isinstance(vote, MessagePeerVoteMultiple):
                chosen = vote.options
            elif isinstance(vote, MessagePeerVote):
                chosen = [vote.option]
            else:
                chosen = []
            votes[user_id] = [option_text.get(o, "?") for o in chosen]
        offset = result.next_offset
        if not offset:
            return votes, users


async def main():
    since = datetime.now(timezone.utc) - timedelta(days=30 * MONTHS)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        # A fresh string session has no cached entities; loading the dialogs
        # lets Telethon resolve the numeric CHAT_ID.
        await client.get_dialogs()
        chat = await client.get_input_entity(CHAT_ID)

        polls = []  # (play_date, votes)
        people = {}
        skipped = []
        async for message in client.iter_messages(chat, reply_to=THREAD_ID):
            if message.date < since:
                break
            media = message.media
            if not isinstance(media, MessageMediaPoll):
                continue
            question = text_of(media.poll.question)
            if not question.startswith(POLL_PREFIX):
                continue
            match = PLAY_DATE_RE.search(question)
            play_date = match.group() if match else f"{message.date:%d.%m.%Y}"
            try:
                votes, users = await fetch_votes(client, chat, message, media.poll)
            except PollVoteRequiredError:
                skipped.append(play_date)
                continue
            people.update(users)
            polls.append((play_date, votes))

    polls.reverse()  # oldest first
    stats: dict[int, Counter] = defaultdict(Counter)
    detail_rows = []
    for play_date, votes in polls:
        for user_id, chosen in votes.items():
            stats[user_id].update(chosen)
            detail_rows.append([play_date, display_name(people.get(user_id)), "; ".join(chosen)])

    total = len(polls)
    summary = sorted(
        stats.items(), key=lambda item: (-item[1]["Буду"], display_name(people.get(item[0])))
    )
    header = ["Учасник", *OPTIONS, "Буду, %"]
    summary_rows = [
        [
            display_name(people.get(user_id)),
            *(counts[o] for o in OPTIONS),
            f"{100 * counts['Буду'] / total:.0f}" if total else "0",
        ]
        for user_id, counts in summary
    ]

    with open(OUTPUT_DIR / "summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(summary_rows)
    with open(OUTPUT_DIR / "votes.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Дата гри", "Учасник", "Відповіді"])
        writer.writerows(detail_rows)

    lines = [
        f"## Голосування за {MONTHS} міс.",
        "",
        f"Опитувань: {total}"
        + (f" ({polls[0][0]} – {polls[-1][0]})" if polls else ""),
        "",
    ]
    if skipped:
        lines += [
            f"Пропущено {len(skipped)} опитувань ({', '.join(skipped)}): Telegram показує "
            "голоси лише тим, хто сам проголосував у опитуванні.",
            "",
        ]
    lines += ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(map(str, row)) + " |" for row in summary_rows]
    report = "\n".join(lines) + "\n"

    print(report)
    if step_summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(report)


if __name__ == "__main__":
    asyncio.run(main())
