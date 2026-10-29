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
    current_day = current_date.weekday()
    monday_time = "18:50"
    saturday_time = "14:50"
    if current_day == weekday.THURSDAY:
        play_date = current_date + timedelta(4)
        play_time = monday_time
        parameters = {
        "chat_id" : CHAT_ID,
        "question" : "Волейбол " + play_date.strftime("%d.%m.%Y") + " " + play_time + " \U0001F600",
        "options" : json.dumps(["Буду","Не буду","+1", "+2", "Стаю в чергу"]),
        "is_anonymous" : False,
        "allows_multiple_answers": True
        }
    elif current_day == weekday.TUESDAY:
        play_time = saturday_time
        play_date = current_date + timedelta(4)
        parameters = {
        "chat_id" : CHAT_ID,
        "question" : "Волейбол " + play_date.strftime("%d.%m.%Y") + " " + play_time + " \U0001F600",
        "options" : json.dumps(["Буду","Буду на 14:00", "Не буду","+1", "+2", "Стаю в чергу"]),
        "is_anonymous" : False,
        "allows_multiple_answers": True
        }
    else:
        print("Wrong current day")
        return

    if THREAD_ID:
        parameters["message_thread_id"] = THREAD_ID


    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"
    resp = requests.get(base_url, data = parameters)
    print(resp.text)

if __name__ == "__main__":
    main()
