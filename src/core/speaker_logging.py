import logging


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "{}[%(levelname)-.1s %(asctime)s (%(filename)s:%(lineno)d)]{} %(message)s"
    datefmt = '%Y-%m-%d %H:%M:%S.%f'

    FORMATS = {
        logging.DEBUG: format.format(grey, reset),
        logging.INFO: format.format(grey, reset),
        logging.WARNING: format.format(yellow, reset),
        logging.ERROR: format.format(red, reset),
        logging.CRITICAL: format.format(bold_red, reset),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class BaseLoglevel:
    level = logging.WARNING


def get_logger() -> logging.Logger:
    logger = logging.getLogger("Speaker_app")
    logger.setLevel(BaseLoglevel.level)

    ch = logging.StreamHandler()
    ch.setLevel(BaseLoglevel.level)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    return logger


if __name__ == '__main__':
    BaseLoglevel.level = logging.INFO
    logger = get_logger()
    logger.error('hello')
