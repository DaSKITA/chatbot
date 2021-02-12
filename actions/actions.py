# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
#
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk import Action, Tracker
#
from rasa_sdk.executor import CollectingDispatcher
#
import json
import requests
from tilt import tilt
import pytz


class ActionGiveServiceInfo(Action):

    def name(self) -> Text:
        return "action_give_privacy_info"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service=tracker.get_slot("service")
        datatype=tracker.get_slot("datatype_privacy")
        if service=="Green Company": 
            file = requests.get('https://raw.githubusercontent.com/Transparency-Information-Language/schema/master/tilt.json')
            file_read = json.loads(file.content)
            instance = tilt.tilt_from_dict(json.loads(file.content))
            dispatcher.utter_message(text="Here is the information about {} by the service {}.".format(datatype, service))
            if datatype=="countries":
                countries=[]
                # using tilt language (works)
                #for element in list(instance.data_disclosed):
                #    for recipient in element.recipients:
                #        countries.append(recipient.category)
                # not using tilt language (works)
                #for element in file_read["dataDisclosed"]:
                #    for recipient in element["recipients"]:
                #        countries.append(recipient["category"])
                # using tilt language (doesn't work)
                #for element in list(instance.thirdCountryTransfers): 
                #    countries.append(element.country)
                # not using tilt language (works)
                for element in file_read["thirdCountryTransfers"]:
                    country_name= pytz.country_names[element["country"]]
                    countries.append(country_name)
                countries_string = ', '.join([str(elem) for elem in countries])    
                dispatcher.utter_message(text="These are the countries: {}".format(countries_string))
                
            elif datatype=="personal data":
                categories=[]
                for element in list(instance.data_disclosed):
                    categories.append(element.category)
                categories_string = ', '.join([str(elem) for elem in categories])    
                dispatcher.utter_message(text="This is your personal data which is stored by {}: {}".format(service, categories_string))
                
            elif datatype=="data protection officer":
                dpo=[]
                for element in file_read["dataProtectionOfficer"]:
                    if file_read["dataProtectionOfficer"][element]:
                        value=str(file_read["dataProtectionOfficer"][element])
                        key_value_string=str(element).capitalize()+ ": " +value
                        dpo.append(key_value_string)    
                dpo_string = ',\n'.join([str(elem) for elem in dpo])  
                dispatcher.utter_message(text="{}".format(dpo_string))
                
            elif datatype=="access to data portability":
                info_access=[]
                if file_read["accessAndDataPortability"]["available"] and file_read["accessAndDataPortability"]["description"]==False:
                    if file_read["accessAndDataPortability"]["available"]=="true":
                        info_access.append("Data access is possible.")
                    else:
                        info_access.append("Data access is not possible.")
                if file_read["accessAndDataPortability"]["description"]:
                    info_access.append(str(file_read["accessAndDataPortability"]["description"]))
                if file_read["accessAndDataPortability"]["url"]:
                    info_access.append("URL: "+ str(file_read["accessAndDataPortability"]["url"]))
                if file_read["accessAndDataPortability"]["email"]:
                    info_access.append("E-Mail: "+ str(file_read["accessAndDataPortability"]["email"]))
                if file_read["accessAndDataPortability"]["identificationEvidences"]:
                    identification=[]
                    info_access.append("For your identification you would need: ")
                    for el in file_read["accessAndDataPortability"]["identificationEvidences"]:
                        identification.append(el)
                    identification_string=', '.join([elem for elem in identification])  
                    info_access.append(identification_string)
                if file_read["accessAndDataPortability"]["administrativeFee"]:
                    info_access.append("The administrative fee would be:")
                    for el in file_read["accessAndDataPortability"]["administrativeFee"]:
                        info_access.append(file_read["accessAndDataPortability"]["administrativeFee"][el])
                info_access_string = '\n'.join([str(elem) for elem in info_access])  
                dispatcher.utter_message(text="{}".format(info_access_string))
                
            elif datatype=="right to information" or datatype=="right to deletion" or datatype=="right to data portability" or datatype=="right to withdraw consent":
                if datatype=="right to information":
                    dt="rightToInformation"
                if datatype=="right to deletion":
                    dt="rightToRectificationOrDeletion"
                if datatype=="right to data portability":
                    dt="rightToDataPortability"
                if datatype=="right to withdraw consent":
                    dt= "rightToWithdrawConsent" 
                info=[]
                if file_read[dt]["available"] and file_read[dt]["description"]==False:
                    if file_read[dt]["available"]=="true":
                        info.append("Data access is possible.")
                    else:
                        info_access.append("Data access is not possible.")
                if file_read[dt]["description"]:
                    info.append(str(file_read[dt]["description"]))
                if file_read[dt]["url"]:
                    info.append("URL: "+ str(file_read[dt]["url"]))
                if file_read[dt]["email"]:
                    info.append("E-Mail: "+ str(file_read[dt]["email"]))
                if file_read[dt]["identificationEvidences"]:
                    identification=[]
                    info.append("For your identification you would need: ")
                    for el in file_read[dt]["identificationEvidences"]:
                        identification.append(el)
                    identification_string=', '.join([elem for elem in identification])  
                    info.append(identification_string)
                info_string = '\n'.join([str(elem) for elem in info])  
                dispatcher.utter_message(text="{}".format(info_string))
                
            else:
                dispatcher.utter_message(text="Here is the information about {} by the service {}.".format(datatype, service))
        elif service!="Green Company":
            dispatcher.utter_message(text="Here is the information about {} by the service {}.".format(datatype, service))

        return []


# This is a simple example for a custom action which utters "Hello World!"

#

#
#
#class ActionHelloWorld(Action):
#
#
#    def name(self) -> Text:
#        return "action_give_privacy_info"
#
#    def run(self, 
#            dispatcher: CollectingDispatcher,
#            tracker: Tracker,
#            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#        dispatcher.utter_message(text="Das kann ich leider noch nicht")
#
#        return []
