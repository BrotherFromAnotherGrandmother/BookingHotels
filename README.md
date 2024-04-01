# API для сайта по бронированию отелей
<img width="1089" alt="image" src="https://github.com/BrotherFromAnotherGrandmother/BookingHotels/assets/101392966/071301ca-0199-4d75-bb6b-fafd2f1b998e">


# Hotels

Запуск celery = celery -A app.tasks.celery_app:celery_worker worker --loglevel=INFO

Запуск flower = celery -A app.tasks.celery_app:celery_worker flower = celery -A путь_до_воркера:переменная_воркера flower

Запуск beat_schedule = celery --app=app.tasks.celery_app:celery_worker worker -l INFO -B


#  

#  

#  
