FROM rasa/rasa:2.2.0

USER root

WORKDIR /app
COPY . /app
COPY ./data /app/data

RUN  rasa train -c config.yml -d domain.yml --data ./data/ --fixed-model-name "de-model" --debug

CMD [ "run","-m","/app/models/de-model.tar.gz","--enable-api","--cors","*","--debug" ]
