import logging


def get_logger(path: str = None):
    # https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-log-to-stdout
    log_file = path if path else 'songdb.log'
    log_format = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    log = logging.getLogger()

    log_file_handle = logging.FileHandler(log_file)
    log_file_handle.setFormatter(log_format)
    log.addHandler(log_file_handle)

    log_console_handle = logging.StreamHandler()
    log_console_handle.setFormatter(log_format)
    log.addHandler(log_console_handle)

    return log
