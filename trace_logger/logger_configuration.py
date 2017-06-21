# -* coding: utf-8 -*-

import os
LOG_ROOT = os.path.abspath(os.path.dirname(__file__))
TRACE_LOG = "trace_log"

log_conf = {
    "version": 1,
    'disable_existing_loggers': False,
    "formatters": {
        "log_form": {
            "format": "%(message)s"
        }
    },
    "filters": {},
    "handlers": {
        TRACE_LOG: {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_ROOT, "../logs/tracelogger.log"),
            "formatter": "log_form",
            "when": "midnight",
        }
    },
    "loggers": {
        TRACE_LOG: {
            "handlers": [TRACE_LOG],
            "level": "INFO",
        }
    },
}