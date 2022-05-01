import logging
import coloredlogs

log = logging.getLogger('pipelines')

def conf_logging(lvl=logging.DEBUG, loggerName=None, config=None):
    """
    this function intends to be called once, in main function
    args:
        lvl: logging level for root logger
        loggerName: None to set root logger
        config: {"loggerName": lvl}
    """
    # set level for pipelines logger
    log.setLevel(lvl)

    if loggerName:
        loggers = [logging.getLogger(loggerName)]
    else:
        loggers = [
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict]
        # root logger
        loggers.append(logging.getLogger())

    # we do not touch level of loggers here
    for logger in loggers:
        logger.handlers.clear()

        fmt = '%(asctime)s - %(levelname)s - %(message)s'
        if lvl == logging.DEBUG:
            fmt = ('==> [%(asctime)s %(levelname)-7s (%(process)s) <%(name)s> '
                   ' %(pathname)s:%(lineno)d ]\n%(message)s\n')
        formatter = coloredlogs.ColoredFormatter(fmt)

        logger.propagate = False

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(lvl)

        logger.addHandler(ch)

    if not config:
        # default level settings
        config = {
        }

    for k, v in config.items():
        logging.getLogger(k).setLevel(v)


def deepmerge(base, update):
    for k, v in base.items():
        if k in update:
            if isinstance(update[k], dict):
                update[k] = deepmerge(v, update[k])
    base.update(update)
    return base
