import requests
import json
import urllib.parse


#dirty to return 1000 data points but there is no documentation of an exact match so... gl
URL = "https://us.api.blizzard.com/data/wow/search/item?_page=%d&_pageSize=100&namespace=static-us&locale=en_US&name.en_US=%s&orderby=id&_page=1&access_token=%s"
AUTH_URI = "https://us.battle.net/oauth/authorize"
TOKEN_URI = "https://us.battle.net/oauth/token"


class BlizzardApiHandle:
  def __init__(self, token_file, secret_file):
    with open (token_file, "r") as tokenfile:
      self.token = tokenfile.readline()
    with open (secret_file, "r") as secretfile:
      self.secret = secretfile.readline()
    self.oauth()

  def oauth(self):
    data = {'grant_type':'client_credentials'}
    reply = requests.post(TOKEN_URI, data = data, auth=(self.token.strip(), self.secret.strip()))
    if reply.status_code != 200:
      print ("Blizzard oauth failed with error: " + str(reply.status_code))
      print(reply.url)
      return False
    print(reply.text)
    self.access_token = reply.json()['access_token']

  def request_page(self, page_num, name):
    url_name = urllib.parse.quote(name, safe='')
    reply = requests.get(URL % (page_num, url_name, self.access_token))
    if reply.status_code != 200:
      print ("Blizzard item id lookup failed with error: " + str(reply.status_code) + " on an item named: " + name)
      print(reply.url)
      return False
    #now sift through results to find the correct item id
    reply = reply.json()
    return reply

  def get_item_id_from_name(self, name):
    for i in range(200): #20000 items should be sufficient hopefully
      reply = self.request_page(i+1, name)
      if not reply:
        return False
      for item in reply["results"]:
        if item["data"]["name"]["en_US"].lower() == name.lower():
          #found the item!!!!
          return item["data"]["id"]

  
