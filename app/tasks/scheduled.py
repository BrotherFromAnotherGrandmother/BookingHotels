from app.tasks.celery_app import celery_worker as celery


@celery.task(name='periodic_task')
def periodic_task():
    print('12345')
