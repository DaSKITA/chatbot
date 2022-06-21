# Transparency Information Bot (TIBO)

Development of a conversational AI with which users can communicate (as a user interface to tilt documents).

Possible applications:
1. Transparency:
Users can request/get (parts of) transparency information (from tilt documents).
Our user study shows, that TIBO purifies textual privacy policies and achieves the goal of making transparency information more accessible for users.

2. Data subject access requests:
  a) users can specify what info they want to request from a service (in tilt it says what data is collected -> are "offered" by chatbot) -> (email) request is generated automatically
  b) ask users if and which information should be deleted -> (email) deletion request is generated automatically
  -> bridge to supported information requests

The following figure shows the general architecture of TIBO.
![](./docs/tibo.png)

## Requirements

* Python < 3.9.0
* Rasa == 2.8.14
* Tilt-Hub running (see https://anonymous.4open.science/r/tilt-hub)
* Tilt-Hub Credentials 

## Setup

### Tilt hub
- Make sure that a Tilt-Hub instance is accessible `python preprocessing.py`
- Request the TILTHUB .env file and set your environment variables via 'source tilthub-creds.txt'

### Rasa Action Server
- Train a new model with the following command: `rasa train --data data --config config.yml --domain domain.yml --fixed-model-name "de-model"` (as most available Tilt documents are in German, the given command trains a German model)
- Test your model by starting the action server with the following comment: `rasa run actions --actions actions.actions` and `rasa shell --model models/de-model.tar.gz` or `rasa shell --model models/de-model.tar.gz --debug`

### Applications

#### A. Web Server/Chatbot
- set the socket url in index.html, e.g. `socketUrl: "http://localhost:80"`
- start action server (if not already done): `rasa run actions --actions actions.actions` and `rasa run --model models/de-model.tar.gz --enable-api --cors "*" --debug`

#### B. Alexa Skill
For accessing TIBO via the Alexa Skill, it is required to have an instance of the web server (chatbot) up and running (see above).
Afterwards, you can stick to the following steps:

1.	create a https version of the website: z.B. `ngrok http 5005` 
2.	start the action server with rasa: `rasa run actions --actions actions.actions` und `rasa run --model models/de-model.tar.gz --enable-api --connector alexa_connector.AlexaConnector --cors "*" --debug --credentials credentials.yml`
4.	go to the Amazon Alexa developer page: adjust endpoint with https url + `/webhooks/alexa_assistant/webhook`
5.	on the Amazon Alexa developer page: click on Build 
6.	Start conversation: `Alexa, starte Datenschutz Bot`

See also https://developer.amazon.com/alexa/console/ask.


## Rasa Action Server

The rasa server can be reached can be reached at your domain under port 5005.

### Classification Model

The conversational AI, implemented wwith rasa open source, is based on a classification model (called rasa NLU) that takes an users message and maps that to a predefined intent. 
These intents are mapped to a response (which is also called an action) by rasa core.
You can find the predefined actions in the domain.yml (German) or domain_en.yml (English).
If you want to extend the list of actions, please see also to https://rasa.com/docs/rasa/responses.

For more information on developing and training rasa models, please refer to: https://rasa.com/docs/rasa/2.x/reference/rasa/train/

### REST API
You can access rasa core via a REST API, which can be reached at `your_domain:5005/webhooks/rest/webhook`.
Particularly, you can send and receive messages or train the classification model via the API. 
The following figure gives an example of an API call: 
![](./docs/rest.png)

You can find an API specification here: https://rasa.com/docs/rasa/pages/http-api. 

## Application Examples
In general, we use the REST API to interact with TIBO.
We implemented to application examples, a chatbot window and an Alexa Skill.

### Web Server/Chatbot Window
The chatbot window can be embedded into any website. 
An exemplified website is provided and can be reached at your specified socket url.

### Alexa Skill
Please refer to the previous chapter to get information on the setup.
Once the Skill is installed on your Alexa device, you can start a conversation with TIBO.

## Credits
- Development: XXX
