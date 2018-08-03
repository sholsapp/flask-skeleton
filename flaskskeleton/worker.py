import logging
import threading
import time


log = logging.getLogger(__name__)


#: A function that takes no arguments and does nothing.
no_op = lambda: time.time()


class BackgroundWorker(threading.Thread):
    """A background worker.

    :param int interval: The number of seconds to wait before re-running the work
      function.
    :param callable func: A function that takes no arguments that when called
      performs the work that the background worker should perform.

    """

    def __init__(self, interval=60, func=no_op):
        threading.Thread.__init__(self)
        self.interval = interval
        self.running = True
        self.func = func

    def stop(self):
        """Stop the execution thread."""
        self.running = False

    def run(self):
        """Start the execution thread."""
        while self.running:
            ret = self.func()
            log.info('Worker function returns: %s', ret)
            time.sleep(self.interval)
