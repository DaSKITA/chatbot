# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import json
import requests
from tilt import tilt
import pytz
import ast
import json
from countrygroups import EUROPEAN_UNION
from deep_translator import GoogleTranslator

from graphqlclient import GraphQLClient
url='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8082/'


#fill services slot 
class ActionSetSlotValueRequest(Action):
    def name(self) -> Text:
        return "action_fill_service_slot"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value_service_company = tracker.get_slot('service_company')
        return [SlotSet("service", slot_value_service_company)]

#fill company slot
class ActionSetSlotValueRequest(Action):
    def name(self) -> Text:
        return "action_fill_company_slot"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value_company=tracker.latest_message['text']
        return [SlotSet("company", slot_value_company)]

    
#read possible services from tilt hub and give options as buttons
class ActionGiveOptions(Action):
    def name(self) -> Text:
        return "action_give_options"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        buttons=[]
        message="Möglichkeiten sind: "
        channel = tracker.get_latest_input_channel() #get channel which is used
        if channel=="socketio":
            #buttons.append({"title": "Metadaten", "payload": '/datatypes{"datatype":"Metadaten"}'})
            buttons.append({"title": "Länder, in die meine Daten weitergegeben werden", "payload": '/datatypes{"datatype":"Länder"}'})
            buttons.append({"title": "Drittparteien an die meine Daten weitergegeben werden", "payload": '/datatypes{"datatype":"Drittparteien"}'})
            buttons.append({"title": "Anzahl der Drittparteien an die meine Daten weitergegeben werden", "payload": '/datatypes{"datatype":"Anzahl von Drittparteien"}'})
            buttons.append({"title": "Persönliche Daten, die gespeichert werden", "payload": '/datatypes{"datatype":"persönliche Daten"}'})
            buttons.append({"title": "Datenschutzbeauftragter", "payload": '/datatypes{"datatype":"Datenschutzbeauftragter"}'})
            buttons.append({"title": "Informationen zur Datenportabilität", "payload": '/datatypes{"datatype":"Datenportabilität"}'})
            buttons.append({"title": "Information zu meinen Rechten an den Daten", "payload": '/datatypes{"datatype":"Rechte"}'})
            buttons.append({"title": "Verantwortliche*r", "payload": '/datatypes{"datatype":"Verantwortliche*r"}'})
        else:
            message="Möglichkeiten sind: Länder, in die deine Daten weitergegeben werden, Drittparteien, an die deine Daten weitergegeben werden, die Anzahl dieser Drittparteien, persönliche Daten die gespeichert werden, Informationen zu deinen Rechten an den Daten, Informationen zu Datenportabilität, den Datenschutzbeauftragten oder den Verantwortlichen."
        dispatcher.utter_message(text=message, buttons=buttons)
        return []

#new action:
#read possible services from tilt hub and give options
class ActionReadServices(Action):
    def name(self) -> Text:
        return "action_read_services"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        channel = tracker.get_latest_input_channel() #get channel which is used
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta { name language} } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        if channel=="socketio":
        #buttons = []
            message="Mögliche Dienste sind: "
            for r in result_dict:
                if r["node"]["meta"]["language"]=="de":
                    name=r["node"]["meta"]["name"]
                    message = message + name + ", "
            
            message=message[:-2]
        else:
            message="Mögliche Dienste sind: "
            i=1
            for r in result_dict:
                if r["node"]["meta"]["language"]=="de":
                    name=r["node"]["meta"]["name"]
                    message = message + name +": "+ str(i)+ ", "
                    i = i+1
            
            message=message[:-2]
            message = message + "Nenne die Nummer des Dienstes, der dich interessiert."
        dispatcher.utter_message(text=message)
        return []
#update Slots for path change
class ActionSetSlotValueRequest(Action):
    def name(self) -> Text:
        return "action_change_to_request"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("requesting", "requesting"), SlotSet("privacy_policy", None)]


class ActionSetSlotValuePrivacy(Action):
    def name(self) -> Text:
        return "action_change_to_privacy"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("requesting", None), SlotSet("privacy_policy", "privacy")]
    
    
    
#Set Slots for change to privacy path
class ActionSetSlotThisServicePrivacy(Action):
    def name(self) -> Text:
        return "action_this_service"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot_value_requesting = tracker.get_slot('requesting')
        slot_value_privacy_policy = tracker.get_slot('privacy_policy')
        
        if slot_value_privacy_policy != None:
            return [SlotSet("policy", "Policy of this service")] 
        else:
            return [SlotSet("request", "Requesting at this service")] 

class ActionSetSlotAnotherServicePrivacy(Action):
    def name(self) -> Text:
        return "action_another_service"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        slot_value_requesting = tracker.get_slot('requesting')
        slot_value_privacy_policy = tracker.get_slot('privacy_policy')
        
        if slot_value_privacy_policy != None:
            return [SlotSet("policy", "Policy of another service")] 
        else:
            return [SlotSet("request", "Requesting at another service")]   
    
class ActionSetSlotNoServicePrivacy(Action):
    def name(self) -> Text:
        return "action_no_service"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value_requesting = tracker.get_slot('requesting')
        slot_value_privacy_policy = tracker.get_slot('privacy_policy')
        
        if slot_value_privacy_policy != None:
            return [SlotSet("policy", "No policy at all")] 
        else:
            return [SlotSet("request", "No requesting at all")]  

        
#give comparison info about personal data
class ActionGiveComparisonInfoSharingBetween(Action):
    def name(self) -> Text:
        return "action_give_comparison_info_sharing_between"
    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #get slot value
        service_list=tracker.get_slot("service")
        
        #check if service name is possible, else return
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta { name, language } } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        
        #loop through all given services and give info
        for service in service_list:
            contains = 0
            service_upper=service.title()
            number_dict = {"Eins": "1", "Zwei": "2", "Drei": "3", "Vier": "4", "Fünf": "5", "Sechs":"6", "Sieben": "7", "Acht": "8", "Neun": "9", "Zehn": "10", "Elf": "11", "Zwölf": "12", "Dreizehn": "13", "Vierzehn": "14", "Fünfzehn": "15", "Sechzehn": "16", "Siebzehn": "17", "Achtzehn": "18", "Neunzehn": "19", "Zwanzig": "20", "Einundzwanzig": "21", "Zweiundzwanzig": "22", "Dreiundzwanzig": "23", "Vierundzwanzig": "24", "Fünfundzwanzig": "25", "Sechsundzwanzig": "26", "Siebenundzwanzig": "27", "Achtundzwanzig": "28", "Neunundzwanzig": "29", "Dreißig": "30"}
            if service_upper in number_dict.keys():
                service = number_dict[service_upper]
            if service in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]:
                number = service
                i = 1
                for r in result_dict:
                    if r["node"]["meta"]["language"]=="de":
                        if str(i) == number:
                            meta_name=r["node"]["meta"]["name"]
                            service = meta_name
                            contains = 1
                    i = i+1
            else:
                service_upper=service.title()
                service_upper2=service.capitalize()
                #check if service name is possible, else return
                meta_name=service
                contains=0
                for r in result_dict:
                    if service in r["node"]["meta"]["name"] or service_upper in r["node"]["meta"]["name"] or service_upper2 in r["node"]["meta"]["name"]:
                        contains=1
                        meta_name = r["node"]["meta"]["name"]
            if contains==0:
                dispatcher.utter_message(text="Leider haben wir keinen Informationen über den Dienst {}.".format(service))
                continue    
            #get tilt of service
            address='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8080/tilt/tilt?filter={"meta.name" : "' + meta_name + '"}'
            
            # load password and username for database access
            f=open('./access_data.json')
            data=json.load(f)
            username=data["database"]["user"]
            pw=data["database"]["pw"]
            file= requests.get(address, auth=(str(username), str(pw)))
            file_read = json.loads(file.text[1:-1])
            instance = tilt.tilt_from_dict(file_read)
            
            #check if service transferres data to company
            part_yes="Der Dienst " + str(service) + " teilt deine Daten mit "
            yes_list=[]
            for element in list(instance.data_disclosed):
                for recipient in list(element.recipients):
                    if str(recipient.name).title() in service_list:
                        yes_list.append(str(recipient.name).title())
            if yes_list!=[]:
                string_service=part_yes+ ', '.join([str(elem) for elem in yes_list]) + "."
            else:
                string_service="Der Dienst " + str(service) + " teilt deine Daten mit keinem der anderen Dienste."
            dispatcher.utter_message(text=string_service)
        
                                             
        return[]
    
        
#give comparison info about country
class ActionGiveComparisonInfoCountry(Action):
    def name(self) -> Text:
        return "action_give_comparison_info_country"
    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #get slot values
        service_list=tracker.get_slot("service")
        country_de=tracker.get_slot("country")
        country=GoogleTranslator(source='de', target='en').translate(country_de) #get english name of country
        #check if service name is possible, else return
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta { name, language } } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        
        #loop through all given services and give info
        for service in service_list:
            contains = 0
            service_upper=service.title()
            number_dict = {"Eins": "1", "Zwei": "2", "Drei": "3", "Vier": "4", "Fünf": "5", "Sechs":"6", "Sieben": "7", "Acht": "8", "Neun": "9", "Zehn": "10", "Elf": "11", "Zwölf": "12", "Dreizehn": "13", "Vierzehn": "14", "Fünfzehn": "15", "Sechzehn": "16", "Siebzehn": "17", "Achtzehn": "18", "Neunzehn": "19", "Zwanzig": "20", "Einundzwanzig": "21", "Zweiundzwanzig": "22", "Dreiundzwanzig": "23", "Vierundzwanzig": "24", "Fünfundzwanzig": "25", "Sechsundzwanzig": "26", "Siebenundzwanzig": "27", "Achtundzwanzig": "28", "Neunundzwanzig": "29", "Dreißig": "30"}
            if service_upper in number_dict.keys():
                service = number_dict[service_upper]
            if service in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]:
                number = service
                i = 1
                for r in result_dict:
                    if r["node"]["meta"]["language"]=="de":
                        if str(i) == number:
                            meta_name=r["node"]["meta"]["name"]
                            service = meta_name
                            contains = 1
                    i = i+1
            else:
                service_upper=service.title()
                #check if service name is possible, else return
                for r in result_dict:
                    if service in r["node"]["meta"]["name"] or service_upper in r["node"]["meta"]["name"]:
                        contains=1
                        meta_name = r["node"]["meta"]["name"]

            if contains==0:
                dispatcher.utter_message(text="Leider haben wir keinen Informationen über den Dienst {}.".format(service))
                continue
                #if n_services ==1:
                #    return []
                #else: 
                #    service_list.remove(service)
                  
                
            #get tilt of service
            address='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8080/tilt/tilt?filter={"meta.name" : "' + meta_name + '"}'
            #load password and username for database access
            f=open('./access_data.json')
            data=json.load(f)
            username=data["database"]["user"]
            pw=data["database"]["pw"]
            #get file
            file= requests.get(address, auth=(username, pw))
            file_read = json.loads(file.text[1:-1])
            instance = tilt.tilt_from_dict(file_read)
            
            #check if service transferres data to country
            if not list(instance.third_country_transfers):
                dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an das Land {} weiter.".format(service, country_de))
            else:
                transfer=0
                for element in list(instance.third_country_transfers):
                    country_name=pytz.country_names[element.country]
                    if country_name==country:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten an das Land {} weiter.".format(service, country))
                        transfer=1
                if transfer==0:
                    dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an das Land {} weiter.".format(service, country_de))
                                             
        return[]        

    
#give comparison info about company
class ActionGiveComparisonInfoCompany(Action):
    def name(self) -> Text:
        return "action_give_comparison_info_company"
    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #get slot values
        service_list=tracker.get_slot("service")
        company=tracker.get_slot("company")
        company=str(company).title()
        
        #check if service name is possible, else return
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta { name, language } } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        
        #loop through all given services and give info
        for service in service_list:
            contains = 0
            service_upper=service.title()
            number_dict = {"Eins": "1", "Zwei": "2", "Drei": "3", "Vier": "4", "Fünf": "5", "Sechs":"6", "Sieben": "7", "Acht": "8", "Neun": "9", "Zehn": "10", "Elf": "11", "Zwölf": "12", "Dreizehn": "13", "Vierzehn": "14", "Fünfzehn": "15", "Sechzehn": "16", "Siebzehn": "17", "Achtzehn": "18", "Neunzehn": "19", "Zwanzig": "20", "Einundzwanzig": "21", "Zweiundzwanzig": "22", "Dreiundzwanzig": "23", "Vierundzwanzig": "24", "Fünfundzwanzig": "25", "Sechsundzwanzig": "26", "Siebenundzwanzig": "27", "Achtundzwanzig": "28", "Neunundzwanzig": "29", "Dreißig": "30"}
            if service_upper in number_dict.keys():
                service = number_dict[service_upper]
            if service in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]:
                number = service
                i = 1
                for r in result_dict:
                    if r["node"]["meta"]["language"]=="de":
                        if str(i) == number:
                            meta_name=r["node"]["meta"]["name"]
                            service = meta_name
                            contains = 1
                    i = i+1
            else:
                service_upper=service.title()
                #check if service name is possible, else return
                meta_name=service
                for r in result_dict:
                    if service in r["node"]["meta"]["name"] or service_upper in r["node"]["meta"]["name"]:
                        contains=1
                        meta_name = r["node"]["meta"]["name"]

            if contains==0:
                dispatcher.utter_message(text="Leider haben wir keinen Informationen über den Dienst {}.".format(service))
                continue
                
            #get tilt of service
            address='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8080/tilt/tilt?filter={"meta.name" : "' + meta_name + '"}'
            #load password and username for database access
            f=open('./access_data.json')
            data=json.load(f)
            username=data["database"]["user"]
            pw=data["database"]["pw"]
            #get file
            file= requests.get(address, auth=(username, pw))

            file_read = json.loads(file.text[1:-1])
            
            instance = tilt.tilt_from_dict(file_read)
            
            #check if service transferres data to company
            answer=0
            for element in list(instance.data_disclosed):
                transfer=0
                for recipient in list(element.recipients):
                    transfer=0
                    if (company in str(recipient.name).title() and answer==0) or (company in str(recipient.name) and answer==0):
                        transfer=1
                        answer=1
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten an das Unternehmen {} weiter.".format(service, company))
            if transfer==0 and answer==0:
                dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an das Unternehmen {} weiter.".format(service, company))
                                             
        return[]        
    
    
    
#give info about datatypes    
class ActionGiveServiceInfo(Action):
    def name(self) -> Text:
        return "action_give_privacy_info"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #get slot values
        service=tracker.get_slot("service")
        datatype=tracker.get_slot("datatype")
        datatype=datatype.capitalize()
        #take care of synonyms in case of text input
        for string in ["Meta Daten", "meta Daten", "meta daten", "Meta daten", "Metadaten"]:
            if datatype in string:
                datatype= "metadata"
                break
        for string in ["Datenschutzbeauftragte", "Datenschutzbeauftragter", "Datenschutz Beauftragter", "Datenschutz beauftragter", "Datenschutzbeauftragten"]:
            if datatype in string:
                datatype="data protection officer"
                break
        for string in ["Recht", "Rechte", "meine Rechte", "mein Recht", "Rechten"]:
            if datatype in string:
                datatype="right"
                break
        for string in ["Datenportabilität", "Daten Portabilität", "Daten-Portabilität", "Portabilität", "Daten portabilität", "Daten-portabilität"]:
            if datatype in string:
                datatype="access to data portability"
                break
        for string in ["Anzahl der Drittparteien", "Wieviele Drittparteien", "Anzahl", "Anzahl der drittparteien", "Anzahl der Dritt-Parteien", "Anzahl der dritt-parteien", "Anzahl der Dritt-parteien", "Anzahl von Dritt-Parteien", "Anzahl von drittparteien", "Anzahl von Drittparteien", "Anzahl von Dritt-parteien", "Anzahl der dritt partei", "Anzahl der Drittpartei", "Anzahl der drittpartei"]:
            if datatype in string:
                datatype="number of third parties"
                break
        for string in ["Drittparteien", "Dritt-Parteien", "Dritt Parteien", "dritt Parteien", "Dritt parteien", "Drittpartei"]:
            if datatype in string:
                datatype="third parties"
                break
        for string in ["Länder", "Länder, in die meine Daten weitergegeben werden", "Länder, an die meine Daten weitergegeben werden", "Land"]:
            if datatype in string:
                datatype="countries"
                break
        for string in ["Verantwortlicher", "Verantwortliche", "Verantwortliche*r", "Verantwortlichen"]:
            if datatype in string:
                datatype="controller"
                break
        for string in ["persönliche Daten", "Persönliche Daten", "Persönliche daten", "persönliche Daten, die über mich gespeichert werden", "persönliche Daten, die gespeichert werden"]:
            if datatype in string:
                datatype="personal data"
                break
        
        #map datatypes to datatypes as formulated as output
        datatypes_dict={
            "metadata": "Metadaten",
            "countries": "Länder, an die deine Daten weitergegeben werden",
            "third parties": "Drittparteien, an die deine Daten weitergegeben werden",
            "number of third parties": "Anzahl der Drittparteien, an die deine Daten weitergegeben werden",
            "personal data": "persönlichen Daten",
            "data protection officer": "Datenschutzbeauftragte*r",
            "access to data portability": "Datenportabilität und Datenzugriff",
            "right": "Rechte an den Daten",
            "controller": "Verantwortliche Person"
        }
        #if datatype not possible give info about that
        if datatype not in datatypes_dict.keys():
            dispatcher.utter_message(text="Leider haben wir keine Informationen zu '{}'.".format(datatype))
            return[]
        else: 
            datatype_out=datatypes_dict[datatype]
        
        
        channel = tracker.get_latest_input_channel() #get channel which is used
        
        
        #check if service name is possible, else return
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta {name, language} } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        service_list=service
        
        countries_dict={} #initalize dict for countries in case of more services
        
        #loop through all given services and give info
        for service in service_list:
            contains = 0
            service_upper=service.title()
            number_dict = {"Eins": "1", "Zwei": "2", "Drei": "3", "Vier": "4", "Fünf": "5", "Sechs":"6", "Sieben": "7", "Acht": "8", "Neun": "9", "Zehn": "10", "Elf": "11", "Zwölf": "12", "Dreizehn": "13", "Vierzehn": "14", "Fünfzehn": "15", "Sechzehn": "16", "Siebzehn": "17", "Achtzehn": "18", "Neunzehn": "19", "Zwanzig": "20", "Einundzwanzig": "21", "Zweiundzwanzig": "22", "Dreiundzwanzig": "23", "Vierundzwanzig": "24", "Fünfundzwanzig": "25", "Sechsundzwanzig": "26", "Siebenundzwanzig": "27", "Achtundzwanzig": "28", "Neunundzwanzig": "29", "Dreißig": "30"}
            if service_upper in number_dict.keys():
                service = number_dict[service_upper]
            if service in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]:
                number = service
                i = 1
                for r in result_dict:
                    if r["node"]["meta"]["language"]=="de":
                        if str(i) == number:
                            meta_name=r["node"]["meta"]["name"]
                            service_upper = meta_name
                            contains = 1
                    i = i+1
            else:
                service_upper=service.title()
                service_upper2=service.capitalize()
                #check if service name is possible, else return
                meta_name=service
                for r in result_dict:
                    if service in r["node"]["meta"]["name"] or service_upper in r["node"]["meta"]["name"] or service_upper2 in r["node"]["meta"]["name"]:
                        contains=1
                        meta_name = r["node"]["meta"]["name"]
                        #if service in r["node"]["meta"]["name"]:
                        #    meta_name=service
                        #elif service_upper in r["node"]["meta"]["name"]:
                        #    meta_name = service_upper
                        #else:
                        #    meta_name=service_upper2
            if contains==0:
                dispatcher.utter_message(text="Leider haben wir keine Informationen über den Dienst {}.".format(service))
                if service==service_list[-1]:
                    return []
                else: 
                    service_list.remove(service)
                
            #get tilt of service
            address='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8080/tilt/tilt?filter={"meta.name" : "' + meta_name + '"}'
            #load password and username for database access
            f=open('./access_data.json')
            data=json.load(f)
            username=data["database"]["user"]
            pw=data["database"]["pw"]
            #get file
            file= requests.get(address, auth=(username, pw))
            file_read = json.loads(file.text[1:-1])
            instance = tilt.tilt_from_dict(file_read)
            tilt_dict=instance.to_dict()   
#################################################################################################################################################            
            if channel =="telegram": #for telegram format differently
                dispatcher.utter_message(text="Das sind die Informationen über die {} des Dienstes {}.".format(datatype_out, service_upper))
                        
                if datatype=="countries" and len(service_list)==1: #if only one service given
                    if not list(instance.third_country_transfers):
                        dispatcher.utter_message(text="Deine Daten werden in kein Land weitergegeben.")
                    else:
                        countries=[]
                        EU=0
                        for element in list(instance.third_country_transfers):
                            country_name=pytz.country_names[element.country]
                            if country_name in EUROPEAN_UNION.names: #check if country is in EU
                                EU=EU+1
                            countries.append(country_name)
                        number_countries=len(countries)
                        countries_string = ', '.join([str(elem) for elem in countries])
                        if number_countries>1:
                            dispatcher.utter_message(text="Deine Daten werden in {} andere Länder weitergegeben. {} davon gehören zur Europäischen Unsion. **Die Länder sind:** {}".format(str(number_countries), str(EU), countries_string))
                        elif number_countries==1 and EU==1: 
                            dispatcher.utter_message(text="Deine Daten werden in ein anderes Land weitergegeben. Es ist Teil der Europäischen Union: {}".format(countries_string))
                        else:
                            dispatcher.utter_message(text="Deine Daten werden in ein anderes Land weitergegeben. Es ist kein Teil der Europäischen Union: {}".format(countries_string))
                        
                if datatype=="countries" and len(service_list)>1: #if more than one service given
                    countries=[]
                    for element in list(instance.third_country_transfers):
                        country_name=pytz.country_names[element.country]
                        countries.append(country_name)
                    countries_dict.update({service:countries})
                    
                elif datatype=="personal data":
                    categories=[]
                    for element in list(instance.data_disclosed):
                        categories.append(element.category)
                    if not categories:
                        dispatcher.utter_message(text="Der Dienst {} speichert keine persönlichen Daten von dir.".format(service_upper))
                    else:
                        categories_string = ', '.join([str(elem) for elem in categories])    
                        dispatcher.utter_message(text="Der Dienst {} speichert folgende Daten: {}.".format(service_upper, categories_string))
                    
                elif datatype=="third parties":
                    third_parties=[]
                    for element in list(instance.data_disclosed):
                        for recipient in list(element.recipients):
                            third_parties.append(recipient.name)
                    if None in third_parties:
                            third_parties.remove(None)
                    if not third_parties:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an Drittparteien weiter.".format(service_upper))
                    else:
                        third_parties_string = ', '.join([str(elem) for elem in third_parties])    
                        dispatcher.utter_message(text="Drittparteien: {}".format(third_parties_string))
                
                elif datatype=="number of third parties":
                    third_parties=[]
                    for element in list(instance.data_disclosed):
                        for recipient in list(element.recipients):
                            third_parties.append(recipient.name)
                    if None in third_parties:
                            third_parties.remove(None)
                    if not third_parties:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an Drittparteien weiter.".format(service_upper))
                    else:
                        number=len(third_parties)
                        if number==1:
                            dispatcher.utter_message(text="Deine Daten werden an eine Drittpartei weitergegeben.")
                        else: 
                            dispatcher.utter_message(text="Deine Daten werden an {} Drittparteien weitergegeben.".format(number))
                            
                elif datatype=="controller":
                    con_dict=tilt_dict["controller"]
                    if not bool(con_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen über {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        con=[]
                        rep=[]
                        if con_dict["name"]:
                            value=str(con_dict["name"])
                            con.append("Name: "+ str(value))
                        for element in con_dict.keys():
                            if con_dict[element]:
                                if element=="address":
                                    address=str(con_dict[element]).replace(" ", "%20")
                                    value_link= "https://maps.google.com/?q="+address
                                    name_link=dpo_dict[element]
                                    key_value_string="Adresse: " + "["+ name_link + "](" + value_link + ")"
                                    dispatcher.utter_message(json_message={'text': key_value_string, 'parse_mode': 'markdown'})
                                elif element=="country":
                                    country=str(dpo_dict[element])
                                    value=pytz.country_names[country]
                                    con.append("Land: " +value)
                                elif element=="representative":
                                    if con_dict[element]["name"]:
                                        value=con_dict[element]["name"]
                                        rep.append("Name: "+ str(value))
                                    for el in con_dict[element].keys():
                                        if el=="email":
                                            value=str(con_dict[element][el])
                                            key_value_string=str(el).capitalize()+ ": " +value
                                            rep.append(key_value_string)
                                        elif el =="phone":
                                            value=str(con_dict[element][el])
                                            key_value_string="Telefonnummer"+ ": " +value
                                            rep.append(key_value_string)
                                        elif el!="name":
                                            value=con_dict[element][el]
                                            key_value_string=str(el).capitalize()+ ": "+value
                                            rep.append(key_value_string)
                                    con.append("Repräsentant*in:  \n"+ ',  \n'.join([str(elem) for elem in rep]))
                                elif element!="name":
                                    value=str(con_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    con.append(key_value_string)
                        con_string = ',  \n'.join([str(elem) for elem in con])  
                        dispatcher.utter_message(text="{}".format(con_string))
                    
                elif datatype=="data protection officer":
                    dpo_dict=tilt_dict["dataProtectionOfficer"]
                    if not bool(dpo_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen zu {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        dpo=[]
                        if dpo_dict["name"]:
                            value=dpo_dict["name"]
                            dpo.append("Name: "+ str(value))
                        for element in dpo_dict.keys():
                            if dpo_dict[element]:
                                if element=="email":
                                    value=str(dpo_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    dpo.append(key_value_string)
                                elif element=="phone":
                                    value=dpo_dict[element]
                                    key_value_string="Telefonnummer: "+value
                                    dpo.append(key_value_string)
                                elif element=="address":
                                    address=str(dpo_dict[element]).replace(" ", "%20")
                                    value_link= "https://maps.google.com/?q="+address
                                    name_link=dpo_dict[element]
                                    key_value_string="Adresse: " + "["+ name_link + "](" + value_link + ")"
                                    dispatcher.utter_message(json_message={'text': key_value_string, 'parse_mode': 'markdown'})
                                elif element=="country":
                                    country=str(dpo_dict[element])
                                    value=pytz.country_names[country]
                                    dpo.append("Land: " +value)
                                elif element!="name":
                                    value=str(dpo_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    dpo.append(key_value_string)
                        dpo_string = ',  \n'.join([str(elem) for elem in dpo])  
                        dispatcher.utter_message(text="{}".format(dpo_string))
                    
                elif datatype=="access to data portability":
                    access_dict=tilt_dict["accessAndDataPortability"]
                    if not bool(access_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen zu {} von dem Dienst {}.".format(datatype, service_upper))
                    else:
                        info_access=[]
                        if access_dict["available"] and access_dict["description"]==False:
                            if access_dict["available"]=="true":
                                info_access.append("Datenportabilität ist möglich.")
                            else:
                                info_access.append("Datenportabilität ist nicht möglich.")
                        if access_dict["description"]:
                            info_access.append(str(file_read["accessAndDataPortability"]["description"]))
                        if access_dict["url"]:
                            info_access.append("URL: "+str(file_read["accessAndDataPortability"]["url"]))
                        if access_dict["email"]:
                            link_email= "mailto:"+ str(file_read["accessAndDataPortability"]["email"])
                            info_access.append("E-Mail: "+ link_email)
                        if access_dict["identificationEvidences"]:
                            identification=[]
                            info_access.append("Für eine Identifikation brauchst du: ")
                            for el in access_dict["identificationEvidences"]:
                                identification.append(el)
                            identification_string=', '.join([elem for elem in identification])  
                            info_access.append(identification_string)
                        if access_dict["administrativeFee"]:
                            fee=[]
                            info_access.append("Die Bearbeitungsgebühr beträgt: ")
                            for el in access_dict["administrativeFee"]:
                                fee.append(str(access_dict["administrativeFee"][el]))
                            fee=' '.join([elem for elem in fee])
                            info_access.append(fee)
                        info_access_string = '  \n'.join([str(elem) for elem in info_access])  
                        dispatcher.utter_message(text="{}".format(info_access_string))
                
                elif datatype=="right":
                    rights=["rightToInformation","rightToRectificationOrDeletion","rightToDataPortability","rightToWithdrawConsent", "rightToComplain"]
                    right_names=["Recht auf Information", "Recht auf Berichtigung und Löschung", "Recht auf Datenportabilität", "Widerrufsrecht", "Beschwerderecht"]
                    for dt in rights:
                        dt_dict=tilt_dict[dt]
                        info=[]
                        if not bool(dt_dict):
                            dispatcher.utter_message(text="Leider haben wir keine Informationen zu {} von dem Dienst {}.".format(datatype_out, service_upper))
                        elif dt=="rightToComplain":
                            info.append("Hier sind die Informationen zu deinem " + right_names[rights.index(dt)]+":")
                            if dt_dict["available"] and dt_dict["description"]==False:
                                if dt_dict["available"]=="true":
                                    info.append("Ein Datenzugriff ist möglich.")
                                else:
                                    info_access.append("Ein Datenzugriff ist nicht möglich.")
                            if dt_dict["description"]:
                                info.append(str(dt_dict["description"]))
                            if dt_dict["url"]:
                                info.append("URL: "+str(dt_dict["url"]))
                            if dt_dict["email"]:
                                info.append("E-Mail: "+str(dt_dict["email"]))
                            if dt_dict["identificationEvidences"]:
                                identification=[]
                                info.append("Für eine Identifikation brauchst du: ")
                                for el in dt_dict["identificationEvidences"]:
                                    identification.append(el)
                                identification_string=', '.join([elem for elem in identification])  
                                info.append(identification_string)
                            if dt_dict["supervisoryAuthority"]:
                                info_tmp="Aufsichtsbehörde:  \n"
                                for element in dt_dict["supervisoryAuthority"].keys():
                                    if dt_dict["supervisoryAuthority"][element]:
                                        if element=="email":
                                            value=str(dt_dict["supervisoryAuthority"][element])
                                            key_value_string=str(element).capitalize()+ ": " +value
                                            info_tmp= info_tmp +key_value_string + "  \n"
                                        elif element=="phone":
                                            value=dt_dict["supervisoryAuthority"][element]
                                            key_value_string="Telefonnummer: "+value
                                            info_tmp = info_tmp +key_value_string+ "  \n"
                                        elif element=="address":
                                            address=str(dt_dict["supervisoryAuthority"][element]).replace(" ", "%20")
                                            value_link= "https://maps.google.com/?q="+address
                                            name_link=dt_dict["supervisoryAuthority"][element]
                                            key_value_string="Adresse: " + "["+ name_link + "](" + value_link + ")"
                                            dispatcher.utter_message(json_message={'text': key_value_string, 'parse_mode': 'markdown'})
                                            #info_tmp.append(key_value_string)
                                        elif element=="country":
                                            country=str(dt_dict["supervisoryAuthority"][element])
                                            value=pytz.country_names[country]
                                            info_tmp  = info_tmp +(str(element).capitalize()+ ": " +value) + "  \n"
                                        else:
                                            value=str(dt_dict["supervisoryAuthority"][element])
                                            key_value_string=str(element).capitalize()+ ": " +value
                                            info_tmp  = info_tmp +key_value_string+ "  \n" 
                                info.append(info_tmp)
                        else:
                            info.append("Hier sind die Informationen zu deinem " + right_names[rights.index(dt)]+":")
                            if dt_dict["available"] and dt_dict["description"]==False:
                                if dt_dict["available"]=="true":
                                    info.append("Datenzugriff ist möglich.")
                                else:
                                    info_access.append("Datenzugriff ist nicht möglich.")
                            if dt_dict["description"]:
                                info.append(str(dt_dict["description"]))
                            if dt_dict["url"]:
                                info.append("URL: "+str(dt_dict["url"]))
                            if dt_dict["email"]:
                                info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                            if dt_dict["identificationEvidences"]:
                                identification=[]
                                info.append("Für eine Identifikation brachst du: ")
                                for el in dt_dict["identificationEvidences"]:
                                    identification.append(el)
                                identification_string=', '.join([elem for elem in identification])  
                                info.append(identification_string)
                        info_string = '  \n'.join([str(elem) for elem in info])  
                        dispatcher.utter_message(text="{}".format(info_string))
                        
############################################################################################################################################                              
            elif channel=="socketio": #if channel socketio keep formatting
                if not (datatype=="countries" and len(service_list)>1):
                    dispatcher.utter_message(text="Das sind die Informationen über **{}** des Dienstes {}.".format(datatype_out, service_upper))
                
                if datatype=="countries" and len(service_list)==1: #if only one service given
                    
                    if not list(instance.third_country_transfers):
                        dispatcher.utter_message(text="Deine Daten werden an keine anderen Länder weitergegeben.")
                    else:
                        countries=[]
                        EU=0
                        for element in list(instance.third_country_transfers):
                            country_name=pytz.country_names[element.country]
                            if country_name in EUROPEAN_UNION.names: #check if country is in EU
                                EU=EU+1
                            countries.append(country_name)
                        number_countries=len(countries)
                        countries_string = ', '.join([str(elem) for elem in countries])
                        if number_countries>1:
                            dispatcher.utter_message(text="Deine Daten werden an {} andere Länder weitergegeben. {} davon sind Teil der Europäischen Union. **Die Länder sind:** {}".format(str(number_countries), str(EU), countries_string))
                        elif number_countries==1 and EU==1: 
                            dispatcher.utter_message(text="Deine Daten werden an ein anderes Land weitergegeben: {}. Es ist Teil der Europäischen Union.".format(countries_string))
                        else:
                            dispatcher.utter_message(text="Deine Daten werden an ein anderes Land weitergegeben: {}. Es ist kein Teil der Europäischen Union.".format(countries_string))
                        
                if datatype=="countries" and len(service_list)>1: #if more than one service given
                    countries=[]
                    for element in list(instance.third_country_transfers):
                        country_name=pytz.country_names[element.country]
                        countries.append(country_name)
                    countries_dict.update({service:countries})
                    
                elif datatype=="personal data":
                    categories=[]
                    for element in list(instance.data_disclosed):
                        categories.append(element.category)
                    if not categories:
                        dispatcher.utter_message(text="Der Dienst {} speichert keine persönlichen Daten über dich.".format(service_upper))
                    else:
                        categories_string = ', '.join([str(elem) for elem in categories])    
                        dispatcher.utter_message(text="Der Dienst {} speichert folgende persönlichen Daten über dich: {}.".format(service_upper, categories_string))
                    
                elif datatype=="third parties":
                    third_parties=[]
                    for element in list(instance.data_disclosed):
                        for recipient in list(element.recipients):
                            third_parties.append(recipient.name)
                    if None in third_parties:
                            third_parties.remove(None)
                    if third_parties==[]:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten an keine Drittpartei weiter.".format(service_upper))
                    else:
                        third_parties_string = ', '.join([str(elem) for elem in third_parties])    
                        dispatcher.utter_message(text="Drittparteien sind: {}".format(third_parties_string))
                
                elif datatype=="number of third parties":
                    third_parties=[]
                    for element in list(instance.data_disclosed):
                        for recipient in list(element.recipients):
                            third_parties.append(recipient.name)
                    if None in third_parties:
                            third_parties.remove(None)
                    if not third_parties:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten an keine Drittparteien weiter.".format(service_upper))
                    else:
                        number=len(third_parties)
                        if number==1:
                            dispatcher.utter_message(text="Deine Daten werden an eine Drittpartei weitergegeben.")
                        else: 
                            dispatcher.utter_message(text="Deine Daten werden an {} Drittparteien weitergegeben.".format(number))
                    
                elif datatype=="controller":
                    con_dict=tilt_dict["controller"]
                    if not bool(con_dict):
                        dispatcher.utter_message(text="Unfortunately there is no information about the {} of {}.".format(datatype, service))
                    else:
                        con=[]
                        rep=[]
                        if con_dict["name"]:
                            value=str(con_dict["name"])
                            con.append("Name: "+ str(value))
                        for element in con_dict.keys():
                            if con_dict[element]:
                                if element=="address":
                                    address=str(con_dict[element]).replace(" ", "%20")
                                    value_link= "https://maps.google.com/?q="+address
                                    name_link=con_dict[element]
                                    key_value_string="Adresse: " + "["+ name_link + "](" + value_link + ")"
                                    con.append(key_value_string)
                                elif element=="country":
                                    country=str(con_dict[element])
                                    value=pytz.country_names[country]
                                    con.append("Land: " +value)
                                elif element=="representative":
                                    if con_dict[element]["name"]:
                                        value=con_dict[element]["name"]
                                        rep.append("Name: "+ str(value))
                                    for el in con_dict[element].keys():
                                        if el=="email":
                                            value=str(con_dict[element][el])
                                            key_value_string=str(el).capitalize()+ ": " +value
                                            rep.append(key_value_string)
                                        elif el =="phone":
                                            value=str(con_dict[element][el])
                                            key_value_string="Telefonnummer"+ ": " +value
                                            rep.append(key_value_string)
                                        elif el !="name":
                                            value=con_dict[element][el]
                                            key_value_string=str(el).capitalize()+ ": "+value
                                            rep.append(key_value_string)
                                    con.append("Repräsentant*in:  \n"+ ',  \n'.join([str(elem) for elem in rep]))
                                elif element!="name":
                                    value=str(con_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    con.append(key_value_string)
                        con_string = ',  \n'.join([str(elem) for elem in con])  
                        dispatcher.utter_message(text="{}".format(con_string))
                
                elif datatype=="supervisory authority":
                    sup_dict=tilt_dict["supervisoryAuthority"]
                    if not bool(sup_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen über {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        sup=[]
                        for element in sup_dict.keys():
                            if sup_dict[element]:
                                if element=="email":
                                    value=str(sup_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    sup.append(key_value_string)
                                elif element=="phone":
                                    value=sup_dict[element]
                                    key_value_string="Telefonnummer: "+value
                                    sup.append(key_value_string)
                                elif element=="address":
                                    address=str(sup_dict[element]).replace(" ", "%20")
                                    value_link= "https://maps.google.com/?q="+address
                                    name_link=sup_dict[element]
                                    key_value_string= "Adresse: " + "["+ name_link + "](" + value_link + ")"
                                    sup.append(key_value_string)
                                elif element=="country":
                                    country=str(sup_dict[element])
                                    value=pytz.country_names[country]
                                    sup.append("Land: " +value)
                                else:
                                    value=str(sup_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    dpo.append(key_value_string)
                        sup_string = ',  \n'.join([str(elem) for elem in dpo])  
                        dispatcher.utter_message(text="{}".format(sup_string))
                
                elif datatype=="data protection officer":
                    dpo_dict=tilt_dict["dataProtectionOfficer"]
                    if not bool(dpo_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen über {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        dpo=[]
                        if dpo_dict["name"]:
                            value=dpo_dict["name"]
                            dpo.append("Name: "+ value)
                        for element in dpo_dict.keys():
                            if dpo_dict[element]:
                                if element=="address":
                                    address=str(dpo_dict[element]).replace(" ", "%20")
                                    value_link= "https://maps.google.com/?q="+address
                                    name_link=dpo_dict[element]
                                    key_value_string="Adresse: " + "*["+ name_link + "](" + value_link + ")*"
                                    dpo.append(key_value_string)
                                elif element=="country":
                                    country=str(dpo_dict[element])
                                    value=pytz.country_names[country]
                                    key_value_string="Land: *" +value+"*"
                                    dpo.append(key_value_string)
                                elif element=="email":
                                    value="mailto:"+ "*"+str(dpo_dict[element])+"*"
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    dpo.append(key_value_string)
                                elif element=="phone":
                                    value=dpo_dict[element]
                                    key_value_string="Telefonnummer: "+value
                                    dpo.append(key_value_string)
                                elif element!="name":
                                    value="*"+str(dpo_dict[element])+"*"
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    dpo.append(key_value_string)    
                        dpo_string = ',  \n'.join([str(elem) for elem in dpo])  
                        dispatcher.utter_message(text="{}".format(dpo_string))
                    
                elif datatype=="access to data portability":
                    access_dict=tilt_dict["accessAndDataPortability"]
                    if not bool(access_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen über {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        info_access=[]
                        if access_dict["available"] and access_dict["description"]==False:
                            if access_dict["available"]=="true":
                                info_access.append("Datenportabilität ist möglich.")
                            else:
                                info_access.append("Datenportabilität ist nicht möglich.")
                        if access_dict["description"]:
                            info_access.append(str(file_read["accessAndDataPortability"]["description"]))
                        if access_dict["url"]:
                            info_access.append("URL: "+ "*"+str(file_read["accessAndDataPortability"]["url"])+"*")
                        if access_dict["email"]:
                            link_email= "mailto:"+ str(file_read["accessAndDataPortability"]["email"])
                            info_access.append("E-Mail: "+"*"+ link_email+"*")
                        if access_dict["identificationEvidences"]:
                            identification=[]
                            info_access.append("Für eine Identifikation benötigst du: ")
                            for el in access_dict["identificationEvidences"]:
                                identification.append("*"+el+"*")
                            identification_string=', '.join([elem for elem in identification])  
                            info_access.append(identification_string)
                        if access_dict["administrativeFee"]:
                            fee=[]
                            info_access.append("Die Bearbeitungsgebühr beträgt: ")
                            for el in access_dict["administrativeFee"]:
                                fee.append("*"+str(access_dict["administrativeFee"][el])+"*")
                            fee=' '.join([elem for elem in fee])
                            info_access.append(fee)
                        info_access_string = '  \n'.join([str(elem) for elem in info_access])  
                        dispatcher.utter_message(text="{}".format(info_access_string))
                        
                elif datatype=="right":
                    rights=["rightToInformation","rightToRectificationOrDeletion","rightToDataPortability","rightToWithdrawConsent", "rightToComplain"]
                    right_names=["Recht auf Information", "Recht auf Berichtigung und Löschung", "Recht auf Datenportabilität", "Widerrufsrecht", "Beschwerderecht"]
                    for dt in rights:
                        dt_dict=tilt_dict[dt]
                        info=[]
                        if not bool(dt_dict):
                            dispatcher.utter_message(text="Leider haben wir keine Informationen über {} für den Dienst {}.".format(datatype_out, service_upper))
                        elif dt=="rightToComplain":
                            info.append("Das sind die Informationen zu deinem " + right_names[rights.index(dt)]+":")
                            if dt_dict["available"] and dt_dict["description"]==False:
                                if dt_dict["available"]=="true":
                                    info.append("Datenzugriff ist möglich.")
                                else:
                                    info.append("Datenzugriff ist nicht möglich.")
                            if dt_dict["description"]:
                                info.append(str(dt_dict["description"]))
                            if dt_dict["url"]:
                                info.append("URL: "+str(dt_dict["url"]))
                            if dt_dict["email"]:
                                info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                            if dt_dict["identificationEvidences"]:
                                identification=[]
                                info.append("Für eine Identifikation benötigst du: ")
                                for el in dt_dict["identificationEvidences"]:
                                    identification.append(el)
                                identification_string=', '.join([elem for elem in identification])  
                                info.append(identification_string)
                            if dt_dict["supervisoryAuthority"]:
                                info_tmp="Aufsichtsbehörde:  \n"
                                for element in dt_dict["supervisoryAuthority"].keys():
                                    if dt_dict["supervisoryAuthority"][element]:
                                        if element=="email":
                                            value=str(dt_dict["supervisoryAuthority"][element])
                                            key_value_string=str(element).capitalize()+ ": mailto:" +value
                                            info_tmp= info_tmp +key_value_string + "  \n"
                                        elif element=="phone":
                                            value=dt_dict["supervisoryAuthority"][element]
                                            key_value_string="Telefonnummer: "+value
                                            info_tmp = info_tmp +key_value_string+ "  \n"
                                        elif element=="address":
                                            address=str(dt_dict["supervisoryAuthority"][element]).replace(" ", "%20")
                                            value_link= "https://maps.google.com/?q="+address
                                            name_link=dt_dict["supervisoryAuthority"][element]
                                            key_value_string="Adresse: " + "["+ name_link + "](" + value_link + ")"
                                            info_tmp = info_tmp +key_value_string+ "  \n"
                                        elif element=="country":
                                            country=str(dt_dict["supervisoryAuthority"][element])
                                            value=pytz.country_names[country]
                                            info_tmp  = info_tmp +"Land: " +value + "  \n"
                                        else:
                                            value=str(dt_dict["supervisoryAuthority"][element])
                                            key_value_string=str(element).capitalize()+ ": " +value
                                            info_tmp  = info_tmp +key_value_string+ "  \n"
                                info.append(info_tmp)
                        else:
                            info.append("Hier sind die Informationen zu deinem " + right_names[rights.index(dt)]+":")
                            if dt_dict["available"] and dt_dict["description"]==False:
                                if dt_dict["available"]=="true":
                                    info.append("Datenzugriff ist möglich.")
                                else:
                                    info_access.append("Datenzugriff ist nicht möglich.")
                            if dt_dict["description"]:
                                info.append(str(dt_dict["description"]))
                            if dt_dict["url"]:
                                info.append("URL: "+str(dt_dict["url"]))
                            if dt_dict["email"]:
                                info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                            if dt_dict["identificationEvidences"]:
                                identification=[]
                                info.append("Für eine Identifikation benötigst du: ")
                                for el in dt_dict["identificationEvidences"]:
                                    identification.append(el)
                                identification_string=', '.join([elem for elem in identification])  
                                info.append(identification_string)
                        info_string = '  \n'.join([str(elem) for elem in info])  
                        dispatcher.utter_message(text="{}".format(info_string))
####################################################################################################################################################         
            else: #format for alexa
                if datatype=="countries" and len(service_list)>1:
                    do_nothing=0
                else:
                    dispatcher.utter_message(text="Das sind die Informationen des Dienstes {} über die {}.".format(service_upper, datatype_out))
                        
                if datatype=="countries" and len(service_list)==1: #if only one service given
                    if not list(instance.third_country_transfers):
                        dispatcher.utter_message(text="Deine Daten werden an keine Drittpartei weitergegeben.")
                    else:
                        countries=[]
                        EU=0
                        for element in list(instance.third_country_transfers):
                            country_name=pytz.country_names[element.country]
                            country_name_german=GoogleTranslator(source='auto', target='de').translate(country_name)
                            if country_name in EUROPEAN_UNION.names: #check if country is in EU
                                EU=EU+1
                            countries.append(country_name_german)
                        number_countries=len(countries)
                        countries_string = ', '.join([str(elem) for elem in countries])
                        if number_countries>1:
                            dispatcher.utter_message(text="Deine Daten werden an {} andere Länder weitergegeben. {} davon gehören zur Europäischen Unsion. Die Länder sind:  {}".format(str(number_countries), str(EU), countries_string))
                        elif number_countries==1 and EU==1: 
                            dispatcher.utter_message(text="Deine Daten werden an ein anderes Land weitergegeben. Es ist Teil der Europäischen Union: {}.".format(countries_string))
                        else:
                            dispatcher.utter_message(text="Deine Daten werden an ein anderes Land weitergegeben. Es ist kein Teil der Europäischen Union: {}.".format(countries_string))
                        
                if datatype=="countries" and len(service_list)>1: #if more than one service given
                    countries=[]
                    for element in list(instance.third_country_transfers):
                        country_name=pytz.country_names[element.country]
                        countries.append(country_name)
                    countries_dict.update({service:countries})
                    
                elif datatype=="personal data":
                    categories=[]
                    for element in list(instance.data_disclosed):
                        categories.append(element.category)
                    if categories==[]:
                        dispatcher.utter_message(text="Der Dienst {} speichert keine persönlichen Daten von dir.".format(service_upper))
                    else:
                        categories_string = ', '.join([str(elem) for elem in categories]) 
                        
                        dispatcher.utter_message(text="Der Dienst {} speichert folgende Daten: {}.".format(service_upper, categories_string))
                    
                elif datatype=="third parties":
                    third_parties=[]
                    for element in list(instance.data_disclosed):
                        for recipient in list(element.recipients):
                            third_parties.append(recipient.name)
                    if None in third_parties:
                            third_parties.remove(None)
                    if not third_parties:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an Drittparteien weiter.".format(service_upper))
                    else:
                        third_parties_string = ', '.join([str(elem) for elem in third_parties])    
                        dispatcher.utter_message(text="Drittparteien: {}.".format(third_parties_string))
                
                elif datatype=="number of third parties":
                    third_parties=[]
                    for element in list(instance.data_disclosed):
                        for recipient in list(element.recipients):
                            third_parties.append(recipient.name)
                    if None in third_parties:
                            third_parties.remove(None)
                    if not third_parties:
                        dispatcher.utter_message(text="Der Dienst {} gibt deine Daten nicht an Drittparteien weiter.".format(service_upper))
                    else:
                        number=len(third_parties)
                        if number==1:
                            dispatcher.utter_message(text="Deine Daten werden an eine Drittpartei weitergegeben.")
                        else: 
                            dispatcher.utter_message(text="Deine Daten werden an {} Drittparteien weitergegeben.".format(number))
                            
                elif datatype=="controller":
                    con_dict=tilt_dict["controller"]
                    if not bool(con_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen über {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        con=[]
                        rep=[]
                        if con_dict["name"]:
                            value=con_dict["name"]
                            con.append("Name: "+ str(value))
                        for element in con_dict.keys():
                            if con_dict[element]:
                                if element=="address":
                                    value_link=con_dict[element]
                                    key_value_string="Adresse"+ ": " +  value_link + "."
                                    con.append(key_value_string)
                                    #unwichtig=0
                                elif element=="country":
                                    country=str(con_dict[element])
                                    value=pytz.country_names[country]
                                    con.append("Land"+ ": " +value)
                                elif element=="representative":
                                    if con_dict[element]["name"]:
                                        value=con_dict[element]["name"]
                                        rep.append("Name: "+ str(value))
                                    for el in con_dict[element].keys():
                                        if el=="email":
                                            value=str(con_dict[element][el])
                                            key_value_string=str(el).capitalize()+ ": " +value
                                            rep.append(key_value_string)
                                        elif el =="phone":
                                            value=str(con_dict[element][el])
                                            key_value_string="Telefonnummer"+ ": " +value
                                            rep.append(key_value_string)
                                        elif el != "name":
                                            value=con_dict[element][el]
                                            key_value_string=str(el).capitalize()+ ": "+value
                                            rep.append(key_value_string)
                                    con.append("Repräsentant*in:  \n"+ ',  \n'.join([str(elem) for elem in rep]))

                                elif element !="name":
                                    value=str(con_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    con.append(key_value_string)
                        con_string = ',  \n'.join([str(elem) for elem in con])  
                        dispatcher.utter_message(text="{}.".format(con_string))
                    
                elif datatype=="data protection officer":
                    dpo_dict=tilt_dict["dataProtectionOfficer"]
                    if not bool(dpo_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen zu {} für den Dienst {}.".format(datatype, service_upper))
                    else:
                        dpo=[]
                        if dpo_dict["name"]:
                            value=dpo_dict["name"]
                            dpo.append("Name: "+ str(value))
                        for element in dpo_dict.keys():
                            if dpo_dict[element]:
                                if element=="email":
                                    value=str(dpo_dict[element])
                                    key_value_string="E-Mail"+ ": " +value
                                    dpo.append(key_value_string)
                                elif element=="phone":
                                    value=dpo_dict[element]
                                    key_value_string="Telefonnummer"+ ": "+value
                                    dpo.append(key_value_string)
                                elif element=="address":
                                    value_link=dpo_dict[element]
                                    key_value_string= "Adresse: " +  str(value_link) + "."
                                    dpo.append(key_value_string)
                                elif element=="country":
                                    country=str(dpo_dict[element])
                                    value=pytz.country_names[country]
                                    dpo.append("Land"+ ": " +value)
                                elif element !="name":
                                    value=str(dpo_dict[element])
                                    key_value_string=str(element).capitalize()+ ": " +value
                                    dpo.append(key_value_string)
                        dpo_string = ',  \n'.join([str(elem) for elem in dpo])  
                        dispatcher.utter_message(text="{}.".format(dpo_string))
                    
                elif datatype=="access to data portability":
                    access_dict=tilt_dict["accessAndDataPortability"]
                    if not bool(access_dict):
                        dispatcher.utter_message(text="Leider haben wir keine Informationen zu {} von dem Dienst {}.".format(datatype, service_upper))
                    else:
                        info_access=[]
                        if access_dict["available"] and access_dict["description"]==False:
                            if access_dict["available"]=="true":
                                info_access.append("Datenportabilität ist möglich.")
                            else:
                                info_access.append("Datenportabilität ist nicht möglich.")
                        if access_dict["description"]:
                            info_access.append(str(file_read["accessAndDataPortability"]["description"]))
                        if access_dict["url"]:
                            info_access.append("URL: "+str(file_read["accessAndDataPortability"]["url"]))
                        if access_dict["email"]:
                            link_email= str(file_read["accessAndDataPortability"]["email"])
                            info_access.append("E-Mail: "+ link_email)
                        if access_dict["identificationEvidences"]:
                            identification=[]
                            for el in access_dict["identificationEvidences"]:
                                identification.append(el)
                            identification_string='Für eine Identifikation brauchst du: '+', '.join([elem for elem in identification])  
                            info_access.append(identification_string)
                        if access_dict["administrativeFee"]:
                            fee=[]
                            for el in access_dict["administrativeFee"]:
                                fee.append(str(access_dict["administrativeFee"][el]))
                            fee='Die Bearbeitungsgebühr beträgt: '+' '.join([elem for elem in fee])
                            info_access.append(fee)
                        info_access_string = ',  \n'.join([str(elem) for elem in info_access])  
                        dispatcher.utter_message(text="{}.".format(info_access_string))
                
                elif datatype=="right":
                    rights=["rightToInformation","rightToRectificationOrDeletion","rightToDataPortability","rightToWithdrawConsent", "rightToComplain"]
                    right_names=["Recht auf Information", "Recht auf Berichtigung und Löschung", "Recht auf Datenportabilität", "Widerrufsrecht", "Beschwerderecht"]
                    for dt in rights:
                        dt_dict=tilt_dict[dt]
                        info=[]
                        if not bool(dt_dict):
                            dispatcher.utter_message(text="Leider haben wir keine Informationen zu {} von dem Dienst {}.".format(datatype_out, service_upper))
                        elif dt=="rightToComplain":
                            info.append("Hier sind die Informationen zu deinem " + right_names[rights.index(dt)]+":")
                            if dt_dict["available"] and dt_dict["description"]==False:
                                if dt_dict["available"]=="true":
                                    info.append("Ein Datenzugriff ist möglich.")
                                else:
                                    info_access.append("Ein Datenzugriff ist nicht möglich.")
                            if dt_dict["supervisoryAuthority"]:
                                info_tmp="Aufsichtsbehörde:  \n"
                                for element in dt_dict["supervisoryAuthority"].keys():
                                    if dt_dict["supervisoryAuthority"][element]:
                                        if element=="email":
                                            value=str(dt_dict["supervisoryAuthority"][element])
                                            key_value_string="E-Mail" ": " +value
                                            info_tmp= info_tmp +key_value_string + ".  \n"
                                        elif element=="phone":
                                            value=dt_dict["supervisoryAuthority"][element]
                                            key_value_string="Telefonnummer"+ ": "+value
                                            info_tmp = info_tmp +key_value_string+ ".  \n"
                                        elif element=="address":
                                            unwichtig=0
                                        elif element=="country":
                                            country=str(dt_dict["supervisoryAuthority"][element])
                                            value=pytz.country_names[country]
                                            info_tmp  = info_tmp +("Land"+ ": " +value) + ".  \n"
                                        else:
                                            value=str(dt_dict["supervisoryAuthority"][element])
                                            key_value_string=str(element).capitalize()+ ": " +value
                                            info_tmp  = info_tmp +key_value_string+ ".  \n"
                                info.append(info_tmp)
                        else:
                            info.append("Hier sind die Informationen zu deinem " + right_names[rights.index(dt)]+":")
                            if dt_dict["available"] and dt_dict["description"]==False:
                                if dt_dict["available"]=="true":
                                    info.append("Datenzugriff ist möglich.")
                                else:
                                    info_access.append("Datenzugriff ist nicht möglich.")
                            if dt_dict["description"]:
                                info.append(str(dt_dict["description"]))
                        info_string = '  \n'.join([str(elem) for elem in info])  
                        dispatcher.utter_message(text="{}".format(info_string))
        
#################################################################################################################################################################        
        if datatype=="countries" and len(service_list)>1: #give info for all services at once
            countries_string="Das ist die Information der Dienste {} zu {} .  \n"
            services=' and '.join([str(elem) for elem in countries_dict.keys()])
            for key in countries_dict.keys():
                EU=0
                countries=', '.join([str(elem) for elem in countries_dict[key]]) 
                for el in countries_dict[key]: #check if country is in EU
                    if el in EUROPEAN_UNION.names:                        
                        EU=EU+1
                if len(countries_dict[key])>1:
                    countries_string=countries_string +"Der Dienst "+ key.capitalize() + " gibt deine Daten an " + str(len(countries_dict[key])) + " verschiedene Länder weiter. " + str(EU)+ " davon sind Teil der Europäischen Union. Die Länder sind " + countries + ".   \n"
                elif len(countries_dict[key])==1 and EU==1:
                    countries_string=countries_string +"Der Dienst "+ key.capitalize() + " gibt deine Daten an ein anderes Land weiter: " + countries +  ". Es ist Teil der Europäischen Union.  \n"
                else:
                    countries_string=countries_string +"Der Dienst "+ key.capitalize() + " gibt deine Daten an ein anderes Land weiter: "+ countries + ". Es ist nicht Teil der Europäischen Union.  \n"
            dispatcher.utter_message(text=countries_string.format(services, datatype_out))
            

            
        return []
