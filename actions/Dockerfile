FROM rasa/rasa-sdk:2.2.0

WORKDIR /app
USER root
RUN python -m pip install --upgrade pip
RUN pip install tilt pytz
COPY .  /app/actions
VOLUME /app
