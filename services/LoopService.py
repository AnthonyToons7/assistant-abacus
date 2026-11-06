import schedule
import time
import threading

from services.BrowserService import yoink_browser_history
from services.CalendarService import check_reminders
from services.WhatsAppAutoReplyService import check_and_autoreply

def loop_list():
    schedule.every(360).seconds.do(yoink_browser_history)
    schedule.every(10).seconds.do(check_reminders)
    schedule.every(30).seconds.do(check_and_autoreply)

    threading.Thread(target=scheduler_loop, daemon=True).start()

def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)
