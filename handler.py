import json
import xml.etree.ElementTree as ET

import sys,os
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests

def fstatus(event, context):
  r = requests.get("http://web.mta.info/status/serviceStatus.txt")
  root = ET.fromstring(r.content)
  bdfm_status = root.find(".//subway/line[name='BDFM']/status").text
  bdfm_status_text = "unknown"

  if bdfm_status == "GOOD SERVICE":
    bdfm_status_text = "fine"
  elif bdfm_status == "DELAYS":
    bdfm_status_text = "delayed"
  elif bdfm_status == "PLANNED WORK":
    bdfm_status_text == "probably fine but has planned work"

  response = {}
  response['version'] = "1.0";
  response['response'] = {};
  response['response']['outputSpeech'] = {};
  response['response']['outputSpeech']['type'] = "PlainText";
  response['response']['outputSpeech']['text'] = "The B D F and M trains are %s." % bdfm_status_text
  response['response']['shouldEndSession'] = False;

  r = {
      "statusCode": 200,
      "body": json.dumps(response)
  }

  print(r)
