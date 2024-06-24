import logging
from loguru import logger


class ViconNexusUnityStreamPyException(Exception):
    pass


def process_return_value(ret_val, use_json=True):
    if use_json:
        return ret_val
    else:
        raise ViconNexusUnityStreamPyException("only json encoding supported.")


class _InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _setup_uvicorn_logger():
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # change handler for default uvicorn logger
    intercept_handler = _InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]


def _setup_logger():
    logging.basicConfig(handlers=[_InterceptHandler()], level=0)
