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

![uebersicht](https://user-images.githubusercontent.com/33124461/109649763-a3c90500-7b5c-11eb-94fa-526d7496e016.png)


Der Chatbot ist mit Rasa Open Source programmiert. Er nutzt tilt hub als Datenbank, um tilt-Dokumente auszulesen. Ausgespielt wird der Bot über eine Website und Messenger Dienste (Messenger Dienste sind noch nicht hinzugefügt).

Nutzung:

Neues Modell trainieren: "rasa train"

Modell testen: Action Server starten: "rasa run actions" und "rasa shell" oder "rasa shell --debug"

Bot auf Webseite nutzen: Action Server starten: "rasa run actions" und "rasa run -m models --enable-api --cors "*" --debug"
