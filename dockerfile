FROM python:3.11-slim

WORKDIR /usr/src/

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --timeout=100

COPY . .

CMD ["streamlit", "run", "app.py"]

EXPOSE 8501
