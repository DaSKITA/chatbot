FROM rasa/rasa:2.2.0

USER root

WORKDIR /app
COPY . /app
COPY ./data /app/data

RUN  rasa train -c ./config.yml -d ./domain.yml --data ./data --debug

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug" ]
