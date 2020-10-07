import requests
import xmltodict
import json


URL = "https://classic.wowhead.com/item=%d&xml"

#nothing too special here, just uses wowheads xml api to get tooltips. probably have to do one at a time sadly
def get_tooltip_from_item_id(item_id):
  reply = requests.get(URL % item_id)
  if reply.status_code != 200:
    print("Wowhead item query failed with error code: " + str(reply.status_code))
    print(requests.url)
    return False, False

  reply = xmltodict.parse(reply.text)
  name = reply["wowhead"]["item"]["name"]
  reply = reply["wowhead"]["item"]["jsonEquip"]
  reply = json.loads("{" + reply + "}") #doesnt have opening and closing braces for some reason idk
  return name, reply
