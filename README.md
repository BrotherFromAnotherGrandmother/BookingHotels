# Hotels

Запуск celery = celery -A app.tasks.celery_app:celery_worker worker --loglevel=INFO

Запуск flower = celery -A app.tasks.celery_app:celery_worker flower = celery -A путь_до_воркера:переменная_воркера flower

Запуск beat_schedule = celery --app=app.tasks.celery_app:celery_worker worker -l INFO -B


#  

#  

#  