FROM python:3.13.2

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

RUN pip install pytest pytest-cov

RUN mkdir -p /app/docker

COPY docker/create_test_db.py /app/docker/