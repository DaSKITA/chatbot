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

class ActionGiveServiceInfo(Action):

    def name(self) -> Text:
        return "action_give_privacy_info"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service=tracker.get_slot("service")
        datatype=tracker.get_slot("datatype")
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
