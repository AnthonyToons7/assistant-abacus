import schedule
import time

from services.BrowserService import yoink_browser_history
from services.CalendarService import check_reminders

# to_loop = {
#     "history": [
#         "function": "yoink_browser_history",
#         "interval": 360
#     ],
#     "schedule": [
#         "function": "check_reminders",
#         "interval": 10
#     ]
# }

def loop_list():
    print("Starting loops...")
#     for key, value in to_loop.items():
#         schedule.every(value["interval"]).seconds.do(value["function"])

# def scheduler_loop():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
