from celery.utils.log import get_task_logger

from config.celery import app

LOG = get_task_logger(__name__)


@app.task(bind=True, name="common.tasks.do_something_task")
def do_something_task(self, arg1, arg2):
    LOG.info(f">>> Do something with {arg1 + arg2}... <<<")


@app.task(bind=True, name="common.tasks.periodic_task")
def periodic_task(self):
    LOG.info(">>> Periodic task... <<<")
