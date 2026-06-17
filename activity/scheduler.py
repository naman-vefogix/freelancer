import threading
from .utils import flush_to_db

def start_scheduler():
    def run():
        flush_to_db()
        # reschedule itself every 5 minutes
        timer = threading.Timer(300, run)
        timer.daemon = True
        timer.start()

    timer = threading.Timer(300, run)
    timer.daemon = True
    timer.start()
    print("Scheduler started ehh — flushing every 5 minutes")