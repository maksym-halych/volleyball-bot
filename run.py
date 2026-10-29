import json
import os
from datetime import datetime, timedelta
from enum import IntEnum

import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
THREAD_ID = os.environ.get("THREAD_ID")


class weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def main():
    current_date = datetime.now()
    if current_date.weekday() != weekday.THURSDAY:
        print("Wrong current day")
        return

    play_date = current_date + timedelta(4)
    play_time = "20:30"
    question = f"Волейбол {play_date:%d.%m.%Y} {play_time} \U0001f600"
    parameters = {
        "chat_id": CHAT_ID,
        "question": question,
        "options": json.dumps(["Буду", "Не буду", "+1", "+2", "Стаю в чергу"]),
        "is_anonymous": False,
        "allows_multiple_answers": True,
    }

    if THREAD_ID:
        parameters["message_thread_id"] = THREAD_ID

    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"
    resp = requests.get(base_url, data=parameters)
    print(resp.text)


if __name__ == "__main__":
    main()
