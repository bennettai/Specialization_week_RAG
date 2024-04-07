FROM python:3.11-slim

WORKDIR /usr/src/app

COPY ./app/requirements.txt ./app/

RUN pip install --no-cache-dir -r ./app/requirements.txt --timeout=100

COPY ./app/ ./app/

CMD ["streamlit", "run", "app.py"]

EXPOSE 8501
