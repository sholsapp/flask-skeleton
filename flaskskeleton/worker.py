import os
from datetime import datetime

from apscheduler.schedulers.gevent import GeventScheduler


def tick():
    print("Tick! The time is: %s" % datetime.now())


def main():

    scheduler = GeventScheduler()

    url = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")

    scheduler.add_jobstore("sqlalchemy", url=url)

    scheduler.add_job(tick, "interval", seconds=3, id="example_job", replace_existing=True)

    # g is the greenlet that runs the scheduler loop.
    g = scheduler.start()

    print("Press Ctrl+{0} to exit".format("Break" if os.name == "nt" else "C"))

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        g.join()
    except (KeyboardInterrupt, SystemExit):
        pass
