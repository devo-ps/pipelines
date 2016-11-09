import logging

log = logging.getLogger('pipelines')

def conf_logging():
    logger = logging.getLogger('pipelines')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger.propagate = False

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)

def deepmerge(base, update):
    for k, v in base.items():
        if k in update:
            if isinstance(update[k], dict):
                update[k] = deepmerge(v, update[k])
    base.update(update)
    return base
