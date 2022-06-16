# Chatbot

<!-- <center>
<h2> ➡️ 🌐 <a href="http://implementation.cloud:9999/"> Hier direkt im Chat ausprobieren</a> oder auf <a href="https://www.amazon.de/gp/product/B09D3Q81PW">Amazon Alexa</a> installieren. ⬅️</h2>
</center> -->

<!--
Entwicklung eines Chatbots, mit dem NutzerInnen kommunizieren können (als Nutzer:innenschnittstelle zu tilt-Dokumenten).

Mögliche Anwendungen:
1.	AP2 Transparenz:
NutzerInnen können (Teile der) Transparenzinformationen (aus tilt Dokumenten) abfragen/angeboten bekommen

2.	AP3 Auskunft:
  a)	NutzerInnen kännen angeben, welche Infos sie bei einem Dienst anfragen wollen (in tilt steht, welche Daten gesammelt werden -> werden von Chatbot „angeboten“)
			-> (E-Mail) Anfrage wird automatisch generiert
  b)	Abfragen bei NutzerInnen, ob und welche Informationen gelöscht werden sollen -> (E-Mail) Löschanfrage wird automatisch generiert
  ->	Brücke zu unterstützten Auskunftsanfragen
-->

Development of a chatbot with which users can communicate (as a user interface to tilt documents).

Possible applications:
1. Transparency:
Users can request/get (parts of) transparency information (from tilt documents).

2. Data subject access requests:
  a) users can specify what info they want to request from a service (in tilt it says what data is collected -> are "offered" by chatbot) -> (email) request is generated automatically
  b) ask users if and which information should be deleted -> (email) deletion request is generated automatically
  -> bridge to supported information requests



<!-- ![](./docs/uebersicht.png) -->


## Requirements

* Python < 3.9.0
* Rasa == 2.8.14
* Download Tilt-Hub Credentials: `https://tubcloud.tu-berlin.de/f/1962491489`

## Setup (in German)

- Sicherstellen, dass alle Dokumente im tilt hub abrufbar sind: `python preprocessing.py`
- Request the TILTHUB .env file and set your environment variables via 'source tilthub-creds.txt'
- Neues Modell trainieren: `rasa train --data data --config config.yml --domain domain.yml --fixed-model-name "de-model"`
- Modell testen: Action Server starten mittels `rasa run actions --actions actions.actions` und `rasa shell --model models/de-model.tar.gz` oder `rasa shell --model models/de-model.tar.gz --debug`


## Webinterface
- im index.html die socket url anpassen z.B. `socketUrl: "http://localhost:80"` oder `socketUrl: "https://implementation.cloud`
- deutsch: Action Server starten mittels `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --cors "*" --debug`

## REST API

![](./docs/rest.png)

## Telegram
1. 	https version der Website erstellen: z.B. `ngrok http 5005` bei rasa x `ngrok http 80`
2.	In credentials.yml bei webhook the https url einfügen
3.	Action server und rasa starten: `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --connector telegram --cors "*" --debug --credentials credentials.yml`
5. 	in telegram "daskita_bot" suchen und Konversation starten

## Alexa
1.	https version der Website erstellen: z.B. `ngrok http 5005` bei rasa x `ngrop http 80`
2.	Action server und rasa starten: `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --connector alexa_connector.AlexaConnector --cors "*" --debug --credentials credentials.yml`
4.	auf der Amazon Alexa developer page: den endpoint mit der https url + `/webhooks/alexa_assistant/webhook` anpassen
5.	auf der Amazon Alexa developer page: Build klicken
6.	Konversation starten mit: `Alexa, starte datenschutz bot`

See also https://developer.amazon.com/alexa/console/ask.

## Hinzufügen einer neuen Datenschutzerklärung:
1. tilt Dokument in tilt hub hochladen
2. `preprocessing.py`ausführen
3. Model trainieren mit `rasa train`
4. Model bei Rasa X hochladen und aktivieren

## Nutzung Rasa X:
1. Request the TILTHUB .env file and set your environment variables via 'source tilthub-creds.txt'
1. Evtl. Action server image erneuern: `docker build . -f Dockerfile_action_image -t <account_username>/chatbot:<custom_image_tag>`
2. Evtl. neuen image tag im Ordner etc\rasa im file docker-compose.override.yml anpassen
3. In den Ordner etc\rasa navigieren und `docker-compose --env-file rasa-x.env up -d` ausführen
4. User hinzufügen mit `sudo python3 rasa_x_commands.py create --update admin me <PASSWORD>`
5. Auf https://implementation.cloud gehen, Rasa x Benutzeroberfläche starten und einloggen
6. Bot auf Website ist erreichbar unter https://implementation.cloud:9999

## Credits
- Development: Elias Grünewald, Flora Muscinelli, Michael Gebauer, and Nicola Leschke
