FROM python:3.11.8-bookworm

WORKDIR /app

COPY requirements.txt .
#RUN pip install -r requirements.txt

COPY bin /app/bin/
COPY tests /app/tests/

CMD ["bin/run]
