import requests
import time
from datetime import datetime, timedelta

BOT_TOKEN = "8738640416:AAFf4jrMdu1a7zySHuqSgLtwe8TOYyPpQTY"
CHAT_ID = "5039557587"

VENUE_ID = 2

seen_slots = set()
first_run = True


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def is_weekend(date_obj):
    return date_obj.weekday() in [5, 6]  # Saturday + Sunday


def is_valid_time(time_slot):
    return "06:00" <= time_slot <= "09:00"


def check_slots():
    global seen_slots, first_run

    today = datetime.now()

    for i in range(14):
        date_obj = today + timedelta(days=i)

        if not is_weekend(date_obj):
            continue

        date = date_obj.strftime("%Y-%m-%d")

        url = f"https://adminbooking.gopichandacademy.com/API/Get/Calender?venue_id={VENUE_ID}&date={date}"
        response = requests.get(url)
        data = response.json()

        for court_key in data.get("Result", {}):
            court = data["Result"][court_key]
            court_name = court.get("court_name")

            for slot in court.get("court_available_slots", []):
                parts = slot.split("|")

                if len(parts) < 3:
                    continue

                time_slot, available, price = parts

                if not is_valid_time(time_slot):
                    continue

                unique_id = f"{date}-{court_name}-{time_slot}"

                if available == "1":
                    if first_run:
                        seen_slots.add(unique_id)
                    elif unique_id not in seen_slots:
                        seen_slots.add(unique_id)

                        send_telegram(
                            f"🚨 Weekend Slot Available!\n🏸 Court: {court_name}\n📅 {date}\n⏰ {time_slot}"
                        )

    first_run = False


def main():
    while True:
        check_slots()
        time.sleep(300)


if __name__ == "__main__":
    main()

