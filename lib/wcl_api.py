import requests, json



URL = "https://classic.warcraftlogs.com/api/v2/client"
TOKEN_URL="https://www.warcraftlogs.com/oauth/token"


class WarcraftLogsApiHandle:
  def __init__(self, token_file, secret_file):
    with open (token_file, "r") as tokenfile:
      self.token = tokenfile.readline()
    with open (secret_file, "r") as secretfile:
      self.secret = secretfile.readline()
    self.oauth()

  def oauth(self):
    data = {'grant_type':'client_credentials'}
    reply = requests.post(TOKEN_URL, data = data, auth=(self.token.strip(), self.secret.strip()))
    print(reply.text)
    self.access_token = reply.json()['access_token']
  
  def download_report(self, reportId, db_handle):
    query = """
         { 
           reportData {
             report (code: "%s") {
               code
               masterData {
                 actors {
                   id
                   name
                   gameID
                 }
               }
               fights { #need to find a fight to scope events time
                 name 
                 startTime
                 endTime
               }
             }
           }
         }""" % reportId
    headers = {'Authorization' : 'Bearer ' + self.access_token}
    reply = requests.post(URL, params={'query': query}, headers=headers)
    reply = reply.json()
    #todo test reply
    report = reply["data"]["reportData"]["report"]
    fights = report["fights"]
    characters = report["masterData"]["actors"]

    #now query for the fight we want
    for fight in fights:
      if fight["name"] == "The Prophet Skeram":
        start_time = fight["startTime"]
        end_time = fight["endTime"]
        break
    print(start_time, end_time)
    
    #now query for the equipment data for that fight

    query = """
         { 
           reportData {
             report (code: "AhRtXNmMDfznxdFG") {
              code
              events (startTime: %d, endTime: %d) { #first event is the character gear data dump
                data
              }
             }
           }
         }""" % (start_time, end_time)
    headers = {'Authorization' : 'Bearer ' + self.access_token}
    reply = requests.post(URL, params={'query': query}, headers=headers)
    reply = reply.json()
    events = reply["data"]["reportData"]["report"]["events"]["data"]

    for event in events:
      if event["type"] == "combatantinfo":
        source_id = event["sourceID"]
        #first add characters to the db with ids
        db_handle.queue_add_player(characters[source_id]["gameID"],characters[source_id]["name"])
        #dump previous gear the player had
        db_handle.queue_delete_player_gear(characters[source_id]["gameID"])
        for item in event["gear"]:
          #next add item to make sure its in db - insert or ignore mode so no need to check if exists
          db_handle.queue_add_item_by_id(item["id"])
          #add association
          db_handle.queue_add_item_player_link(item["id"], characters[source_id]["gameID"])
        #equip data
        db_handle.execute_queue()
        print(source_id)
        print(characters[source_id]["name"])


    


