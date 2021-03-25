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

from graphqlclient import GraphQLClient
url='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8082/'

#read possible services from tilt hub and give options as buttons
class ActionReadServices(Action):
    def name(self) -> Text:
        return "action_read_services"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta { name } } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        buttons = []
        for r in result_dict:
            name=r["node"]["meta"]["name"]
            payload= "/services{\"service\":\"" + name + "\"}"
            buttons.append(
                {"title": "{}".format(name), "payload": payload})
        
        #message="Which service are you interested in?"
        dispatcher.utter_message(text= None, buttons=buttons)
        
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
        #take care of synonyms in case of text input
        if datatype in ["meta data"]:
            datatype= "metadata"
        elif datatype in ["dataprotectionofficer", "dataprotection officer"]:
            datatype="data protection officer"
        elif datatype in ["rights", "my rights", "my rights to the data", "my right to the data"]:
            datatype="right"
        elif datatype in ["access to dataportability"]:
            datatype="access to data portability"
        elif datatype in ["number of 3rd parties"]:
            datatype="number of third parties"
        elif datatype in ["3rd parties"]:
            datatype="third parties"
        
        #map datatypes to datatypes as formulated as output
        datatypes_dict={
            "metadata": "metadata",
            "countries": "countries to which your data is transferred",
            "third parties": "third parties to which your data is transferred",
            "number of third parties": "number of third parties to which your data is transferred",
            "personal data": "personal data, that is stored",
            "data protection officer": "data protection officer",
            "access to data portability": "access to data portability",
            "right": "rights to the data",
            "controller": "controller"
        }
        #if datatype not possible give info about that
        if datatype not in datatypes_dict.keys():
            dispatcher.utter_message(text="There is no information about the datatype '{}'.".format(datatype, service))
            return[]
        else: 
            datatype_out=datatypes_dict[datatype]
        
        channel = tracker.get_latest_input_channel() #get channel which is used
        
        #check if service name is possible, else return
        client = GraphQLClient(url)
        result = client.execute('''query { TiltNodes { edges { node { meta { name } } } } } ''')
        result_dict=ast.literal_eval(result)
        result_dict=result_dict["data"]["TiltNodes"]["edges"]
        contains=0
        for r in result_dict:
            if service == r["node"]["meta"]["name"]:
                contains=1
                meta_name=service
        if contains==0:
            dispatcher.utter_message(text="Unfortunately there is no information about {}".format(service))
            return []
        
        address='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8080/tilt/tilt?filter={"meta.name" : "' + meta_name + '"}'
        #file= requests.get('http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8080/tilt/tilt?filter={"meta.name" : "Blue"}', auth=('admin', 'secret'))
        file= requests.get(address, auth=('admin', 'secret'))
        file_read = json.loads(file.text[1:-1])
        
        #file = requests.get('https://raw.githubusercontent.com/Transparency-Information-Language/schema/master/tilt.json')
        #file_read = json.loads(file.content)
        instance = tilt.tilt_from_dict(file_read)
        tilt_dict=instance.to_dict()   
        
        if channel =="telegram": #for telegram format differently
            dispatcher.utter_message(text="Here is the information about the {} specified by the service {} in their privacy policy.".format(datatype_out, service))
            
            if datatype=="countries": 
                if not list(instance.third_country_transfers):
                    dispatcher.utter_message(text="Your data is not transferred to any other country.")
                else:
                    countries=[]
                    for element in list(instance.third_country_transfers):
                        country_name=pytz.country_names[element.country]
                        countries.append(country_name)
                    countries_string = ', '.join([str(elem) for elem in countries])    
                    dispatcher.utter_message(text="These are the countries: {}".format(countries_string))
                
            elif datatype=="personal data":
                categories=[]
                for element in list(instance.data_disclosed):
                    categories.append(element.category)
                if not categories:
                    dispatcher.utter_message(text="There is no personal data stored about you by {}.".format(service))
                else:
                    categories_string = ', '.join([str(elem) for elem in categories])    
                    dispatcher.utter_message(text="Your {}".format(categories_string))
                
            elif datatype=="third parties":
                third_parties=[]
                for element in list(instance.data_disclosed):
                    for recipient in list(element.recipients):
                        third_parties.append(recipient.name)
                if not third_parties:
                    dispatcher.utter_message(text="Your personal data is not transferred to third parties by {}.".format(service))
                else:
                    third_parties=third_parties[:-1]
                    third_parties_string = ', '.join([str(elem) for elem in third_parties])    
                    dispatcher.utter_message(text="Third parties: {}".format(third_parties_string))
            
            elif datatype=="number of third parties":
                third_parties=[]
                for element in list(instance.data_disclosed):
                    for recipient in list(element.recipients):
                        third_parties.append(recipient.name)
                if not third_parties:
                    dispatcher.utter_message(text="Your personal data is not transferred to third parties by {}.".format(service))
                else:
                    third_parties=third_parties[:-1]
                    number=len(third_parties)
                    if number==1:
                        dispatcher.utter_message(text="Your personal data is transferred to one third party.")
                    else: 
                        dispatcher.utter_message(text="Your personal data is transferred to {} third parties.".format(number))
                        
            elif datatype=="controller":
                con_dict=tilt_dict["controller"]
                if not bool(con_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} of {}.".format(datatype, service))
                else:
                    con=[]
                    for element in con_dict.keys():
                        if con_dict[element]:
                            if element=="address":
                                address=str(con_dict[element]).replace(" ", "%20")
                                value_link= "https://maps.google.com/?q="+address
                                name_link=dpo_dict[element]
                                key_value_string=str(element).capitalize()+ ": " + "["+ name_link + "](" + value_link + ")"
                                dispatcher.utter_message(json_message={'text': key_value_string, 'parse_mode': 'markdown'})
                            elif element=="country":
                                country=str(dpo_dict[element])
                                value=pytz.country_names[country]
                                con.append(str(element).capitalize()+ ": " +value)
                            elif element=="representative":
                                con.append("Representative:  \n")
                                for el in con_dict[element].keys():
                                    if el=="email":
                                        value=str(con_dict[element][el])
                                        key_value_string=str(el).capitalize()+ ": " +value
                                        con.append(key_value_string)
                                    else:
                                        value=con_dict[element][el]
                                        key_value_string=str(el).capitalize()+ ": "+value
                                        con.append(key_value_string)
                            else:
                                value=str(con_dict[element])
                                key_value_string=str(element).capitalize()+ ": " +value
                                con.append(key_value_string)
                    con_string = ',  \n'.join([str(elem) for elem in con])  
                    dispatcher.utter_message(text="{}".format(con_string))
                
            elif datatype=="data protection officer":
                dpo_dict=tilt_dict["dataProtectionOfficer"]
                if not bool(dpo_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} of {}.".format(datatype, service))
                else:
                    dpo=[]
                    for element in dpo_dict.keys():
                        if dpo_dict[element]:
                            if element=="email":
                                value=str(dpo_dict[element])
                                key_value_string=str(element).capitalize()+ ": " +value
                                dpo.append(key_value_string)
                            elif element=="phone":
                                value=dpo_dict[element]
                                key_value_string=str(element).capitalize()+ ": "+value
                                dpo.append(key_value_string)
                            elif element=="address":
                                address=str(dpo_dict[element]).replace(" ", "%20")
                                value_link= "https://maps.google.com/?q="+address
                                name_link=dpo_dict[element]
                                key_value_string=str(element).capitalize()+ ": " + "["+ name_link + "](" + value_link + ")"
                                dispatcher.utter_message(json_message={'text': key_value_string, 'parse_mode': 'markdown'})
                            elif element=="country":
                                country=str(dpo_dict[element])
                                value=pytz.country_names[country]
                                dpo.append(str(element).capitalize()+ ": " +value)
                            else:
                                value=str(dpo_dict[element])
                                key_value_string=str(element).capitalize()+ ": " +value
                                dpo.append(key_value_string)
                    dpo_string = ',  \n'.join([str(elem) for elem in dpo])  
                    dispatcher.utter_message(text="{}".format(dpo_string))
                
            elif datatype=="access to data portability":
                access_dict=tilt_dict["accessAndDataPortability"]
                if not bool(access_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} by {}.".format(datatype, service))
                else:
                    info_access=[]
                    if access_dict["available"] and access_dict["description"]==False:
                        if access_dict["available"]=="true":
                            info_access.append("Data access is possible.")
                        else:
                            info_access.append("Data access is not possible.")
                    if access_dict["description"]:
                        info_access.append(str(file_read["accessAndDataPortability"]["description"]))
                    if access_dict["url"]:
                        info_access.append("URL: "+str(file_read["accessAndDataPortability"]["url"]))
                    if access_dict["email"]:
                        link_email= "mailto:"+ str(file_read["accessAndDataPortability"]["email"])
                        info_access.append("E-Mail: "+ link_email)
                    if access_dict["identificationEvidences"]:
                        identification=[]
                        info_access.append("For your identification you would need: ")
                        for el in access_dict["identificationEvidences"]:
                            identification.append(el)
                        identification_string=', '.join([elem for elem in identification])  
                        info_access.append(identification_string)
                    if access_dict["administrativeFee"]:
                        fee=[]
                        info_access.append("The administrative fee would be: ")
                        for el in access_dict["administrativeFee"]:
                            fee.append(str(access_dict["administrativeFee"][el]))
                        fee=' '.join([elem for elem in fee])
                        info_access.append(fee)
                    info_access_string = '  \n'.join([str(elem) for elem in info_access])  
                    dispatcher.utter_message(text="{}".format(info_access_string))
            
            elif datatype=="right":
                rights=["rightToInformation","rightToRectificationOrDeletion","rightToDataPortability","rightToWithdrawConsent", "rightToComplain"]
                right_names=["right to information", "right to rectificatiton or deletion", "right to data portability", "right to withdraw consent", "right to complain"]
                for dt in rights:
                    dt_dict=tilt_dict[dt]
                    info=[]
                    if not bool(dt_dict):
                        dispatcher.utter_message(text="Unfortunately there is no information about {} of {}.".format(datatype_out, service))
                    elif dt=="rightToComplain":
                        info.append("This is the information about your " + right_names[rights.index(dt)]+":")
                        if dt_dict["available"] and dt_dict["description"]==False:
                            if dt_dict["available"]=="true":
                                info.append("Data access is possible.")
                            else:
                                info_access.append("Data access is not possible.")
                        if dt_dict["description"]:
                            info.append(str(dt_dict["description"]))
                        if dt_dict["url"]:
                            info.append("URL: "+str(dt_dict["url"]))
                        if dt_dict["email"]:
                            info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                        if dt_dict["identificationEvidences"]:
                            identification=[]
                            info.append("For your identification you would need: ")
                            for el in dt_dict["identificationEvidences"]:
                                identification.append(el)
                            identification_string=', '.join([elem for elem in identification])  
                            info.append(identification_string)
                        if dt_dict["supervisoryAuthority"]:
                            info_tmp="Supervisory Authority:  \n"
                            for element in dt_dict["supervisoryAuthority"].keys():
                                if dt_dict["supervisoryAuthority"][element]:
                                    if element=="email":
                                        value=str(dt_dict["supervisoryAuthority"][element])
                                        key_value_string=str(element).capitalize()+ ": " +value
                                        info_tmp= info_tmp +key_value_string + "  \n"
                                    elif element=="phone":
                                        value=dt_dict["supervisoryAuthority"][element]
                                        key_value_string=str(element).capitalize()+ ": "+value
                                        info_tmp = info_tmp +key_value_string+ "  \n"
                                    elif element=="address":
                                        address=str(dt_dict["supervisoryAuthority"][element]).replace(" ", "%20")
                                        value_link= "https://maps.google.com/?q="+address
                                        name_link=dt_dict["supervisoryAuthority"][element]
                                        key_value_string=str(element).capitalize()+ ": " + "["+ name_link + "](" + value_link + ")"
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
                                    #info_tmp_string = ',  \n'.join([str(elem) for elem in info_tmp])  
                            info.append(info_tmp)
                    else:
                        info.append("This is the information about your " + right_names[rights.index(dt)]+":")
                        if dt_dict["available"] and dt_dict["description"]==False:
                            if dt_dict["available"]=="true":
                                info.append("Data access is possible.")
                            else:
                                info_access.append("Data access is not possible.")
                        if dt_dict["description"]:
                            info.append(str(dt_dict["description"]))
                        if dt_dict["url"]:
                            info.append("URL: "+str(dt_dict["url"]))
                        if dt_dict["email"]:
                            info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                        if dt_dict["identificationEvidences"]:
                            identification=[]
                            info.append("For your identification you would need: ")
                            for el in dt_dict["identificationEvidences"]:
                                identification.append(el)
                            identification_string=', '.join([elem for elem in identification])  
                            info.append(identification_string)
                    info_string = '  \n'.join([str(elem) for elem in info])  
                    dispatcher.utter_message(text="{}".format(info_string))
                          
        else: #if channel is not telegram keep formating
            dispatcher.utter_message(text="Here is the information about the **{}** specified by the service {} in their privacy policy.".format(datatype_out, service))
            
            if datatype=="countries": 
                if not list(instance.third_country_transfers):
                    dispatcher.utter_message(text="Your data is not transferred to any other countries")
                else:
                    countries=[]
                    for element in list(instance.third_country_transfers):
                        country_name=pytz.country_names[element.country]
                        countries.append(country_name)
                    countries_string = ', '.join([str(elem) for elem in countries])    
                    dispatcher.utter_message(text="**These are the countries:** {}".format(countries_string))
                
            elif datatype=="personal data":
                categories=[]
                for element in list(instance.data_disclosed):
                    categories.append(element.category)
                if not categories:
                    dispatcher.utter_message(text="There is no personal data stored about you by {}.".format(service))
                else:
                    categories_string = ', '.join([str(elem) for elem in categories])    
                    dispatcher.utter_message(text="Your {}".format(categories_string))
                
            elif datatype=="third parties":
                third_parties=[]
                for element in list(instance.data_disclosed):
                    for recipient in list(element.recipients):
                        third_parties.append(recipient.name)
                if not third_parties:
                    dispatcher.utter_message(text="Your personal data is not transferred to third parties by {}.".format(service))
                else:
                    third_parties=third_parties[:-1]
                    third_parties_string = ', '.join([str(elem) for elem in third_parties])    
                    dispatcher.utter_message(text="Third parties: {}".format(third_parties_string))
            
            elif datatype=="number of third parties":
                third_parties=[]
                for element in list(instance.data_disclosed):
                    for recipient in list(element.recipients):
                        third_parties.append(recipient.name)
                if not third_parties:
                    dispatcher.utter_message(text="Your personal data is not transferred to third parties by {}.".format(service))
                else:
                    third_parties=third_parties[:-1]
                    number=len(third_parties)
                    if number==1:
                        dispatcher.utter_message(text="Your personal data is transferred to one third party.")
                    else: 
                        dispatcher.utter_message(text="Your personal data is transferred to {} third parties.".format(number))
                
            elif datatype=="controller":
                con_dict=tilt_dict["controller"]
                if not bool(con_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} of {}.".format(datatype, service))
                else:
                    con=[]
                    for element in con_dict.keys():
                        if con_dict[element]:
                            if element=="address":
                                address=str(con_dict[element]).replace(" ", "%20")
                                value_link= "https://maps.google.com/?q="+address
                                name_link=con_dict[element]
                                key_value_string=str(element).capitalize()+ ": " + "["+ name_link + "](" + value_link + ")"
                                con.append(key_value_string)
                            elif element=="country":
                                country=str(con_dict[element])
                                value=pytz.country_names[country]
                                con.append(str(element).capitalize()+ ": " +value)
                            elif element=="representative":
                                con_tmp="Representative:  \n"
                                for el in con_dict[element].keys():
                                    if el=="email":
                                        value=str(con_dict[element][el])
                                        key_value_string=str(el).capitalize()+ ": " +value
                                        con_tmp=con_tmp+key_value_string+ "  \n"
                                    else:
                                        value=con_dict[element][el]
                                        key_value_string=str(el).capitalize()+ ": "+value
                                        con_tmp=con_tmp+key_value_string+"  \n"
                                con.append(con_tmp)
                            else:
                                value=str(con_dict[element])
                                key_value_string=str(element).capitalize()+ ": " +value
                                con.append(key_value_string)
                    con_string = ',  \n'.join([str(elem) for elem in con])  
                    dispatcher.utter_message(text="{}".format(con_string))
            
            elif datatype=="supervisory authority":
                sup_dict=tilt_dict["supervisoryAuthority"]
                if not bool(sup_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} of {}.".format(datatype, service))
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
                                key_value_string=str(element).capitalize()+ ": "+value
                                sup.append(key_value_string)
                            elif element=="address":
                                address=str(sup_dict[element]).replace(" ", "%20")
                                value_link= "https://maps.google.com/?q="+address
                                name_link=sup_dict[element]
                                key_value_string=str(element).capitalize()+ ": " + "["+ name_link + "](" + value_link + ")"
                                sup.append(key_value_string)
                            elif element=="country":
                                country=str(sup_dict[element])
                                value=pytz.country_names[country]
                                sup.append(str(element).capitalize()+ ": " +value)
                            else:
                                value=str(sup_dict[element])
                                key_value_string=str(element).capitalize()+ ": " +value
                                dpo.append(key_value_string)
                    sup_string = ',  \n'.join([str(elem) for elem in dpo])  
                    dispatcher.utter_message(text="{}".format(sup_string))
            
            elif datatype=="data protection officer":
                dpo_dict=tilt_dict["dataProtectionOfficer"]
                if not bool(dpo_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} of {}.".format(datatype, service))
                else:
                    dpo=[]
                    for element in dpo_dict.keys():
                        if dpo_dict[element]:
                            if element=="address":
                                address=str(dpo_dict[element]).replace(" ", "%20")
                                value_link= "https://maps.google.com/?q="+address
                                name_link=dpo_dict[element]
                                key_value_string=str(element).capitalize()+ ": " + "*["+ name_link + "](" + value_link + ")*"
                                dpo.append(key_value_string)
                            elif element=="country":
                                country=str(dpo_dict[element])
                                value=pytz.country_names[country]
                                key_value_string=str(element).capitalize()+ ": *" +value+"*"
                                dpo.append(key_value_string)
                            elif element=="email":
                                value="mailto:"+ "*"+str(dpo_dict[element])+"*"
                                key_value_string=str(element).capitalize()+ ": " +value
                                dpo.append(key_value_string)
                            elif element=="phone":
                                value=dpo_dict[element]
                                key_value_string=str(element).capitalize()+ ": "+value
                                dpo.append(key_value_string)
                            else:
                                value="*"+str(dpo_dict[element])+"*"
                                key_value_string=str(element).capitalize()+ ": " +value
                                dpo.append(key_value_string)    
                    dpo_string = ',  \n'.join([str(elem) for elem in dpo])  
                    dispatcher.utter_message(text="{}".format(dpo_string))
                
            elif datatype=="access to data portability":
                access_dict=tilt_dict["accessAndDataPortability"]
                if not bool(access_dict):
                    dispatcher.utter_message(text="Unfortunately there is no information about the {} by {}.".format(datatype, service))
                else:
                    info_access=[]
                    if access_dict["available"] and access_dict["description"]==False:
                        if access_dict["available"]=="true":
                            info_access.append("Data access is possible.")
                        else:
                            info_access.append("Data access is not possible.")
                    if access_dict["description"]:
                        info_access.append(str(file_read["accessAndDataPortability"]["description"]))
                    if access_dict["url"]:
                        info_access.append("URL: "+ "*"+str(file_read["accessAndDataPortability"]["url"])+"*")
                    if access_dict["email"]:
                        link_email= "mailto:"+ str(file_read["accessAndDataPortability"]["email"])
                        info_access.append("E-Mail: "+"*"+ link_email+"*")
                    if access_dict["identificationEvidences"]:
                        identification=[]
                        info_access.append("For your identification you would need: ")
                        for el in access_dict["identificationEvidences"]:
                            identification.append("*"+el+"*")
                        identification_string=', '.join([elem for elem in identification])  
                        info_access.append(identification_string)
                    if access_dict["administrativeFee"]:
                        fee=[]
                        info_access.append("The administrative fee would be: ")
                        for el in access_dict["administrativeFee"]:
                            fee.append("*"+str(access_dict["administrativeFee"][el])+"*")
                        fee=' '.join([elem for elem in fee])
                        info_access.append(fee)
                    info_access_string = '  \n'.join([str(elem) for elem in info_access])  
                    dispatcher.utter_message(text="{}".format(info_access_string))
                    
            elif datatype=="right":
                rights=["rightToInformation","rightToRectificationOrDeletion","rightToDataPortability","rightToWithdrawConsent", "rightToComplain"]
                right_names=["right to information", "right to rectificatiton or deletion", "right to data portability", "right to withdraw consent", "right to complain"]
                for dt in rights:
                    dt_dict=tilt_dict[dt]
                    info=[]
                    if not bool(dt_dict):
                        dispatcher.utter_message(text="Unfortunately there is no information about {} of {}.".format(datatype_out, service))
                    elif dt=="rightToComplain":
                        info.append("This is the information about your " + right_names[rights.index(dt)]+":")
                        if dt_dict["available"] and dt_dict["description"]==False:
                            if dt_dict["available"]=="true":
                                info.append("Data access is possible.")
                            else:
                                info.append("Data access is not possible.")
                        if dt_dict["description"]:
                            info.append(str(dt_dict["description"]))
                        if dt_dict["url"]:
                            info.append("URL: "+str(dt_dict["url"]))
                        if dt_dict["email"]:
                            info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                        if dt_dict["identificationEvidences"]:
                            identification=[]
                            info.append("For your identification you would need: ")
                            for el in dt_dict["identificationEvidences"]:
                                identification.append(el)
                            identification_string=', '.join([elem for elem in identification])  
                            info.append(identification_string)
                        if dt_dict["supervisoryAuthority"]:
                            info_tmp="Supervisory Authority:  \n"
                            for element in dt_dict["supervisoryAuthority"].keys():
                                if dt_dict["supervisoryAuthority"][element]:
                                    if element=="email":
                                        value=str(dt_dict["supervisoryAuthority"][element])
                                        key_value_string=str(element).capitalize()+ ": mailto:" +value
                                        info_tmp= info_tmp +key_value_string + "  \n"
                                    elif element=="phone":
                                        value=dt_dict["supervisoryAuthority"][element]
                                        key_value_string=str(element).capitalize()+ ": "+value
                                        info_tmp = info_tmp +key_value_string+ "  \n"
                                    elif element=="address":
                                        address=str(dt_dict["supervisoryAuthority"][element]).replace(" ", "%20")
                                        value_link= "https://maps.google.com/?q="+address
                                        name_link=dt_dict["supervisoryAuthority"][element]
                                        key_value_string=str(element).capitalize()+ ": " + "["+ name_link + "](" + value_link + ")"
                                        info_tmp = info_tmp +key_value_string+ "  \n"
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
                        info.append("This is the information about your " + right_names[rights.index(dt)]+":")
                        if dt_dict["available"] and dt_dict["description"]==False:
                            if dt_dict["available"]=="true":
                                info.append("Data access is possible.")
                            else:
                                info_access.append("Data access is not possible.")
                        if dt_dict["description"]:
                            info.append(str(dt_dict["description"]))
                        if dt_dict["url"]:
                            info.append("URL: "+str(dt_dict["url"]))
                        if dt_dict["email"]:
                            info.append("E-Mail: mailto:"+str(dt_dict["email"]))
                        if dt_dict["identificationEvidences"]:
                            identification=[]
                            info.append("For your identification you would need: ")
                            for el in dt_dict["identificationEvidences"]:
                                identification.append(el)
                            identification_string=', '.join([elem for elem in identification])  
                            info.append(identification_string)
                    info_string = '  \n'.join([str(elem) for elem in info])  
                    dispatcher.utter_message(text="{}".format(info_string))
                
        #elif service!="Green Company":
        #    dispatcher.utter_message(text="Here is the information about {} by the service {}.".format(datatype_out, service))

        return []
