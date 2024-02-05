import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def do_something_task(arg1, arg2):
    logger.info("Do something...")

    result = arg1 + arg2

    return result
