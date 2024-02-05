from celery import shared_task


@shared_task
def do_something_task(arg1, arg2):
    print("Do something...")
    result = arg1 + arg2

    return result
