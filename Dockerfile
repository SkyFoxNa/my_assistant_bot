FROM python:3.11

WORKDIR /my_assistant_bot

COPY . .

MAINTAINER Artem

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]