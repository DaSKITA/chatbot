FROM rasa/rasa-sdk:2.2.0

WORKDIR /app
USER root
COPY requirements-actions.txt /app/
RUN pip install -r requirements-actions.txt
RUN python -m pip install --upgrade pip
COPY .  /app/actions
VOLUME /app
