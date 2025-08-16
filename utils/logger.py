import logging, json, time, uuid, os
from typing import Any

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def get_logger(name: str, logfile: str = None):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)
    if logfile:
        ensure_dir(logfile)
        fh = logging.FileHandler(logfile)
        fh.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fh)
    return logger

def jlog(logger, service: str, event: str, severity: str = "INFO", **meta: Any):
    entry = {
        "ts": time.time(),
        "service": service,
        "event": event,
        "severity": severity,
        "trace_id": str(uuid.uuid4()),
    }
    entry.update(meta)
    logger.info(json.dumps(entry))
