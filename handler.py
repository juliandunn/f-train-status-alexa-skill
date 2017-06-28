"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

#import sys,os
#here = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(here, "./vendored"))

from __future__ import print_function
import os
from botocore.vendored import requests
from pprint import pformat
import json
import xml.etree.ElementTree as ET

API_URL = None
USER = None
HEADERS = None

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session, card_output=None):
    if card_output == None:
        card_output = output

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - \n" + card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the F Train status" \
                    "How may I assist you?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me how I can help with the train status." \
    "You can ask 'is the F train working'?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the train status skill. "\
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_train_status(intent, session):
    """ Do a GET to the MTA and find out the status of the BDFM trains
    """

    card_title = intent['name']
    card_output = None
    session_attributes = {}
    should_end_session = False

    req = requests.get("http://web.mta.info/status/serviceStatus.txt")
    root = ET.fromstring(req.content)
    bdfm_status = root.find(".//subway/line[name='BDFM']/status").text
    bdfm_status_text = "unknown"

    if bdfm_status == "GOOD SERVICE":
        bdfm_status_text = "fine"
    elif bdfm_status == "DELAYS":
        bdfm_status_text = "delayed"
    elif bdfm_status == "PLANNED WORK":
        bdfm_status_text = "probably fine but has planned work"

    speech_output = "The B D F and M trains are {}".format(bdfm_status_text)
    reprompt_text = "How else may I help you? Or you can tell me to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # For hackday, get server and credentials from the Lambda ENV.
    global API_URL
    global HEADERS
    global USER
    USER = os.environ.get("USER", None)
    API_URL = os.environ.get("API_URL", None)
    auth_token = os.environ.get("AUTH_TOKEN", None)

    HEADERS = {"Accept": "application/json",
               "Content-type": "application/json",
               "Authorization": "Bearer " + auth_token}

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetTrainStatus":
        return get_train_status(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """ Uncomment this if statement and populate with your skill's application
    ID to prevent someone else from configuring a skill that sends requests to
    this function.
    """
    if event['session']['application']['applicationId'] !=  "amzn1.ask.skill.31fde9ba-66d5-4635-9195-537e14564293":
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
