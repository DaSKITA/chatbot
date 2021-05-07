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
	- deutsch: `rasa train --data data/de/ --config config/de/config.yml --domain config/de/domain.yml --fixed-model-name "de-model"`
	- englisch: `rasa train --data data/en/ --config config/en/config.yml -domain config/en/domain.yml --fixed-model-name "en-model"`

- Modell testen: 
	- deutsch: Action Server starten mittels `rasa run actions --actions actions.actions_de` und `rasa shell --model models/de-model.tar.gz` oder `rasa shell --model models/de-model.tar.gz --debug`
	- englisch: Action Server starten mittels `rasa run actions --actions actions.actions_en` und `rasa shell --model models/en-model.tar.gz` oder `rasa shell --model models/en-model.tar.gz --debug`

## Webinterface
- deutsch: Action Server starten mittels `rasa run actions --actions actions.actions_de` und `rasa run --model models/de-model.tar.gz --enable-api --cors "*" --debug`
- englisch: Action Server starten mittels `rasa run actions --actions actions.actions_en` und `rasa run --model models/en-model.tar.gz --enable-api --cors "*" --debug`

## REST API

![](./docs/rest.png)

## Telegram
1. 	https version der Website erstellen: z.B. `ngrok http 5005`
2.	In credentials.yml bei webhook the https url einfügen
3.	Action server und rasa starten: 
	- deutsch: `rasa run actions --actions actions.actions_de` und `rasa run --model models/de-model.tar.gz --enable-api --connector telegram --cors "*" --debug --credentials credentials.yml`
	- englisch: `rasa run actions --actions actions.actions_en` und `rasa run --model models/en-model.tar.gz --enable-api --connector telegram --cors "*" --debug --credentials credentials.yml`
5. 	in telegram "daskita_bot" suchen und Konversation starten

## Alexa
1.	https version der Website erstellen: z.B. `ngrok http 5005`
2.	Action server und rasa starten: 
	- deutsch: `rasa run actions --actions actions.actions_de` und `rasa run --model models/de-model.tar.gz --enable-api --connector alexa_connector.AlexaConnector --cors "*" --debug --credentials credentials.yml`
	- englisch: `rasa run actions --actions actions.actions_en` und `rasa run --model models/en-model.tar.gz --enable-api --connector alexa_connector.AlexaConnector --cors "*" --debug --credentials credentials.yml`
4.	auf der Amazon Alexa developer page: den endpoint mit der https url + `/webhooks/alexa_assistant/webhook` anpassen
5.	auf der Amazon Alexa developer page: Build klicken
6.	Konversation starten mit: `Alexa, start privacy bot`
