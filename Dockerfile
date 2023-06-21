
FROM python:alpine3.17

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

WORKDIR /code/app

EXPOSE 80 
EXPOSE 443

CMD ["python", "main.py"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]