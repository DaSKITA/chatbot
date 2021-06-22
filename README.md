# Chatbot
Entwicklung eines Chatbots, mit dem NutzerInnen kommunizieren können (als NutzerInnenschnittstelle zu tilt-Dokumenten).

Mögliche Anwendungen: 
1.	AP2 Transparenz: 
NutzerInnen können (Teile der) Transparenzinformationen (aus tilt Dokumenten) abfragen/angeboten bekommen 

2.	AP3 Auskunft: 
  a)	NutzerInnen kännen angeben, welche Infos sie bei einem Dienst anfragen wollen (in tilt steht, welche Daten gesammelt werden -> werden von Chatbot „angeboten“) 
			-> (E-Mail) Anfrage wird automatisch generiert      
  b)	Abfragen bei NutzerInnen, ob und welche Informationen gelöscht werden sollen -> (E-Mail) Löschanfrage wird automatisch generiert
  ->	Brücke zu unterstützten Auskunftsanfragen



(weitere Anwendungen möglich)

![](./docs/uebersicht.png)


Der Chatbot ist mit Rasa Open Source programmiert. Er nutzt tilt-hub als Datenbank, um tilt-Dokumente auszulesen. Ausgespielt wird der Bot über eine Website und Messenger-Dienste.


## Setup 

- Sicherstellen, dass alle Dokumente im tilt hub abrufbar sind: `python preprocessing.py`
- Neues Modell trainieren: 
	- deutsch: `rasa train --data data/de/ --config config.yml --domain domain.yml --fixed-model-name "de-model"`
	- englisch: `rasa train --data data/en/ --config config_en.yml -domain domain_en.yml --fixed-model-name "en-model"`

- Modell testen: 
	- deutsch: Action Server starten mittels `rasa run actions --actions actions.actions` und `rasa shell --model models/de-model.tar.gz` oder `rasa shell --model models/de-model.tar.gz --debug`
	- englisch: Action Server starten mittels `rasa run actions --actions actions.actions_en` und `rasa shell --model models/en-model.tar.gz` oder `rasa shell --model models/en-model.tar.gz --debug`

## Webinterface
- im index.html die socket url anpassen z.B. `socketUrl: "http://localhost:80"` oder `socketUrl: "https://implementation.cloud`
- deutsch: Action Server starten mittels `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --cors "*" --debug`
- englisch: Action Server starten mittels `rasa run actions --actions actions.actions_en` und `rasa run --model models/en-model.tar.gz --enable-api --cors "*" --debug`

## REST API

![](./docs/rest.png)

## Telegram
1. 	https version der Website erstellen: z.B. `ngrok http 5005` bei rasa x `ngrok http 80`
2.	In credentials.yml bei webhook the https url einfügen
3.	Action server und rasa starten: 
	- deutsch: `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --connector telegram --cors "*" --debug --credentials credentials.yml`
	- englisch: `rasa run actions --actions actions.actions_en` und `rasa run --model models/en-model.tar.gz --enable-api --connector telegram --cors "*" --debug --credentials credentials.yml`
5. 	in telegram "daskita_bot" suchen und Konversation starten

## Alexa
1.	https version der Website erstellen: z.B. `ngrok http 5005` bei rasa x `ngrop http 80`
2.	Action server und rasa starten: 
	- deutsch: `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --connector alexa_connector.AlexaConnector --cors "*" --debug --credentials credentials.yml`
	- englisch: `rasa run actions --actions actions.actions_en` und `rasa run --model models/en-model.tar.gz --enable-api --connector alexa_connector.AlexaConnector --cors "*" --debug --credentials credentials.yml`
4.	auf der Amazon Alexa developer page: den endpoint mit der https url + `/webhooks/alexa_assistant/webhook` anpassen
5.	auf der Amazon Alexa developer page: Build klicken
6.	Konversation starten mit: `Alexa, starte datenschutz bot`

## Nutzung Rasa X:
1. Evtl. Action server image erneuern: `docker build . -f Dockerfile_action_image -t <account_username>/chatbot:<custom_image_tag>`
2. Evtl. neuen image tag im Ordner etc\rasa im file docker-compose.override.yml anpassen
3. In den Ordner etc\rasa navigieren und `docker-compose up -d` ausführen
4. User hinzufügen mit `sudo python3 rasa_x_commands.py create --update admin me <PASSWORD>`
5. Auf https://implementation.cloud gehen, Rasa x Benutzeroberfläche starten und einloggen
