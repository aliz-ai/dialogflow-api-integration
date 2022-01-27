FROM python:3.9.5-slim

WORKDIR /chatbot/

EXPOSE 5000

ADD setup.py config.yaml sa-key.json /chatbot/
ADD src/ /chatbot/src/

RUN mkdir -p /chatbot/ \
  && apt-get update && apt-get -y install gcc build-essential \
  && pip install -U pip setuptools \
  && pip install /chatbot

ENV GOOGLE_APPLICATION_CREDENTIALS /chatbot/sa-key.json
ENV PORT 5000
CMD chatbot --port ${PORT} --host 0.0.0.0
