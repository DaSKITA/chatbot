# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import json
import requests
from tilt import tilt
import pytz

#bold part:
#start_bold = "\033[1m"
#end_bold = "\033[0;0m"

#def phone_link(number):
#    return '<a href="tel:%s">%s</a>' % (number, number)

class ActionGiveServiceInfo(Action):

    def name(self) -> Text:
        return "action_give_privacy_info"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service=tracker.get_slot("service")
        datatype=tracker.get_slot("datatype_privacy")
        datatypes_dict={
            "metadata": "metadata",
            "countries": "countries to which your data is transferred",
            "third parties": "third parties to which your data is transferred",
            "number of third parties": "number of third parties to which your data is transferred",
            "personal data": "personal data, that is stored",
            "data protection officer": "data protection officer",
            "access to data portability": "access to data portability",
            "right": "rights to the data",
        }
        datatype_out=datatypes_dict[datatype]
        
        if service=="Green Company": 
            file = requests.get('https://raw.githubusercontent.com/Transparency-Information-Language/schema/master/tilt.json')
            file_read = json.loads(file.content)
            instance = tilt.tilt_from_dict(json.loads(file.content))
            dispatcher.utter_message(text="Here is the information about the **{}** specified by the service {} in their privacy policy.".format(datatype_out, service))
            tilt_dict=instance.to_dict() #nötig? wandle es ja nur wieder zurück um, waum geht list nicht?
            
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
                rights=["rightToInformation","rightToRectificationOrDeletion","rightToDataPortability","rightToWithdrawConsent"]
                right_names=["right to information", "right to rectificatiton or deletion", "right to data portability", "right to withdraw consent"]
                
                for dt in rights:
                    dt_dict=tilt_dict[dt]
                    if not bool(dt_dict):
                        dispatcher.utter_message(text="Unfortunately there is no information about {} of {}.".format(datatype_out, service))
                    else:
                        info=[]
                        info.append("**This is the information about your " + right_names[rights.index(dt)]+":**")
                        if dt_dict["available"] and dt_dict["description"]==False:
                            if dt_dict["available"]=="true":
                                info.append("Data access is possible.")
                            else:
                                info_access.append("Data access is not possible.")
                        if dt_dict["description"]:
                            info.append(str(dt_dict["description"]))
                        if dt_dict["url"]:
                            info.append("URL: "+ "*"+str(dt_dict["url"])+"*")
                        if dt_dict["email"]:
                            info.append("E-Mail: mailto:"+"*"+ str(dt_dict["email"])+"*")
                        if dt_dict["identificationEvidences"]:
                            identification=[]
                            info.append("For your identification you would need: ")
                            for el in dt_dict["identificationEvidences"]:
                                identification.append("*"+el+"*")
                            identification_string=', '.join([elem for elem in identification])  
                            info.append(identification_string)
                        info_string = '  \n'.join([str(elem) for elem in info])  
                        dispatcher.utter_message(text="{}".format(info_string))
                
        elif service!="Green Company":
            dispatcher.utter_message(text="Here is the information about {} by the service {}.".format(datatype_out, service))

        return []
