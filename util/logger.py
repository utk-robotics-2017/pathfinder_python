import __main__
import logging
import logging.handlers
import os
import sys
import time
# import atexit
from .colors import color

logger = None


def Logger():
    global logger

    if logger is not None:
        return logger
    else:
        if hasattr(__main__, '__file__'):
            name = __main__.__file__[:-3]  # remove '.py'
        else:
            name = 'unknown'
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        fmt = '%(relativeCreated)6d - %(threadName)s - %(filename)s - %(levelname)s - %(message)s'
        # create file handler which logs even debug messages
        logfn = '{0:s}_{1:d}.log'.format(name, int(time.time()))
        # logfn = '/var/log/spine/{0:s}_{1:d}.log'.format(name, int(time.time()))

        class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
            def _open(self):
                prevumask = os.umask(0o000)
                rtv = logging.handlers.RotatingFileHandler._open(self)
                os.umask(prevumask)
                return rtv
        fh_ = GroupWriteRotatingFileHandler(logfn, maxBytes=1024 * 1024 * 5, backupCount=10)
        fh_.setLevel(logging.DEBUG)
        fh = logging.handlers.MemoryHandler(1024 * 1024 * 10, logging.ERROR, fh_)

        formatter = logging.Formatter(fmt)
        fh_.setFormatter(formatter)

        # create console handler with a higher log level
        class RepeatedMessageSteamHandler(logging.StreamHandler):
            repeated = False
            repeat_times = 0

            def __init__(self, *args, **kwargs):
                logging.StreamHandler.__init__(self, *args, **kwargs)

            def emit(self, record):
                global new_message
                try:
                    if hasattr(record, 'repeated') and record.repeated:
                        if self.repeated:
                            self.repeat_times += 1
                            record.msg += " x%(repeat_times)d"
                            record.args = {'repeat_times': self.repeat_times}
                            self.stream.write("\x1b[80D\x1b[1A\x1b[K")
                        else:
                            self.repeat_times = 1
                            self.repeated = True
                    else:
                        self.repeated = False
                    msg = self.format(record)
                    self.stream.write(msg + "\n")
                    self.stream.flush()
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    self.handleError(record)

        ch = RepeatedMessageSteamHandler()
        ch.setLevel(logging.INFO)

        class AnsiColorFormatter(logging.Formatter):
            def __init__(self, msgfmt=None, datefmt=None):
                self.formatter = logging.Formatter(msgfmt)

            def format(self, record):
                s = self.formatter.format(record)

                if record.levelname == 'CRITICAL':
                    s = color(s, fg='red', style='negative')
                elif record.levelname == 'ERROR':
                    s = color(s, fg='red')
                elif record.levelname == 'WARNING':
                    s = color(s, fg='yellow')
                elif record.levelname == 'DEBUG':
                    s = color(s, fg='blue')
                elif record.levelname == 'INFO':
                    pass

                return s
        ch.setFormatter(AnsiColorFormatter(fmt))

        # add the handlers to logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        def my_excepthook(excType, excValue, traceback, logger=logging):
            logger.error("Logging an uncaught exception", exc_info=(excType, excValue, traceback))
        sys.excepthook = my_excepthook
        return logger
