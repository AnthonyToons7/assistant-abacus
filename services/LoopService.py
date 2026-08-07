import schedule
import time
import threading

from services.BrowserService import yoink_browser_history
from services.CalendarService import check_reminders

def loop_list():
    schedule.every(360).seconds.do(yoink_browser_history)
    schedule.every(10).seconds.do(check_reminders)

    threading.Thread(target=scheduler_loop, daemon=True).start()

def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)
