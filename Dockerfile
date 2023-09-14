FROM python:latest

COPY requirements.txt /usr/src/app/requirements.txt
# COPY .env /usr/src/app/.env
COPY source/* /usr/src/app

WORKDIR /usr/src/app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./telegram_bot.py"]
