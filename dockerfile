FROM python:3.11-slim

WORKDIR /usr/src/app

COPY ./app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt --timeout=100 future

COPY . .

CMD ["streamlit", "run", "main.py"]

EXPOSE 8501
