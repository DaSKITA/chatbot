FROM rasa/rasa:2.3.2-full

USER root

WORKDIR /app
COPY . /app
COPY ./data /app/data

RUN  rasa train -c ./config.yml -d ./domain.yml --data ./data --debug 

VOLUME /

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug" ]