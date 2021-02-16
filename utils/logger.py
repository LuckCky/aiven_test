import logging
import logging.handlers
import os


def init_sys_logger(name: str, level: int = logging.INFO):
    """
    Defines logger
    Args:
        name: string; name of logger
        level: logging level to set
    Returns: logger
    """
    _logger = logging.getLogger(name=name)
    path_to_log_file = './logs/' + name + '.log'
    if not os.path.exists('./logs'):
        os.makedirs('./logs')

    file_handler = logging.handlers.RotatingFileHandler(filename=path_to_log_file,
                                                        maxBytes=10485760,
                                                        backupCount=3)
    console_handler = logging.StreamHandler()

    log_formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s: line-[ %(lineno)d ]: %(message)s',
                                      datefmt='%d/%m/%Y %H:%M:%S')
    file_handler.setFormatter(log_formatter)
    console_handler.setFormatter(log_formatter)

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    _logger.setLevel(level)

    return _logger
