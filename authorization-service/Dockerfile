FROM tiangolo/uvicorn-gunicorn-fastapi

WORKDIR /code

# RUN apt-get install python3.11-dev -y
RUN apt-get install libpq-dev -y

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 80

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
