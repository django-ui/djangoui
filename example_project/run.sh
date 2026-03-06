PORT=8000
python manage.py runserver 0:$PORT

#=> uvrun:
#uv run python manage.py runserver 0:${PORT}

#=> run:
#python manage.py runserver 0:${PORT}

#=> run_secure:
#OPTS=' --cert /tmp/cert'
#python manage.py runserver_plus 0:${PORT} ${OPTS}

#=> asgi:
#uvicorn --host 0.0.0.0  --workers 4 --port ${PORT}  djangoui.asgi:application --reload

