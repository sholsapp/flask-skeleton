import argparse
import logging
import os
import sys
from datetime import datetime

from apscheduler.schedulers.gevent import GeventScheduler
from configobj import ConfigObj

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def tick():
    """Print the current time.

    This is an example job that runs on a schedule to demonstrate
    the APScheduler integration.

    """
    print("Tick! The time is: %s" % datetime.now())


def main():
    """Initialize and start the worker process.

    Parses command line arguments to load a ConfigObj configuration file,
    configures the APScheduler scheduler with a SQLAlchemy job store, and
    blocks until interrupted.

    The configuration file should contain a ``[worker]`` section with a
    ``database_uri`` key.

    :raises SystemExit: If the configuration file cannot be loaded.
    """

    parser = argparse.ArgumentParser(description="flask-skeleton worker")
    parser.add_argument(
        "-c", "--config",
        default=os.path.join(os.path.dirname(__file__), "..", "config", "dev.config"),
        help="Path to the ConfigObj configuration file.",
    )
    args = parser.parse_args()

    try:
        config = ConfigObj(args.config, configspec=f"{args.config}spec")
    except OSError:
        print(f"Failed to load the configuration file at {args.config}.")
        sys.exit(1)

    url = config["worker"]["database_uri"]
    tick_interval = int(config["worker"]["tick_interval"])

    scheduler = GeventScheduler()

    scheduler.add_jobstore("sqlalchemy", url=url)

    scheduler.add_job(
        tick, "interval", seconds=tick_interval, id="example_job", replace_existing=True
    )

    # g is the greenlet that runs the scheduler loop.
    g = scheduler.start()

    print("Press Ctrl+{0} to exit".format("Break" if os.name == "nt" else "C"))

    # Execution will block here until Ctrl+C is pressed.
    try:
        g.join()
    except (KeyboardInterrupt, SystemExit):
        pass
