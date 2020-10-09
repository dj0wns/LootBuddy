import requests
import json
import os
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import flask #have to manage a baby webserver to receive the token

URL = "https://classic.warcraftlogs.com/api/v2/user"
TOKEN_URL="https://www.warcraftlogs.com/oauth/token"
AUTH_URL="https://classic.warcraftlogs.com/oauth/authorize"


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
    if reply.status_code != 200:
      print("WCL oauth failed with error: " + str(reply.status_code))
      return False
    print(reply.text)
    self.access_token = reply.json()['access_token']

  def oauth2(self):
    app = flask.Flask(__name__)

    @app.route("/")
    def demo():
      wcl = OAuth2Session(self.token.strip())
      authorization_url, state = wcl.authorization_url(AUTH_URL)
      flask.session['oauth_state'] = state
      return flask.redirect(authorization_url)
    @app.route("/callback")
    def callback():
      wcl = OAuth2Session(self.token.strip(), state=flask.session['oauth_state'])
      token = wcl.fetch_token(TOKEN_URL, client_secret=self.secret.strip(),
                              authorization_response=flask.request.url)
      self.auth_token = token["access_token"]
      print(token)
      func = flask.request.environ.get('werkzeug.server.shutdown')
      if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
      func()
      return 'You may now close this window!'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.secret_key = os.urandom(24)
    app.run(debug=False)

  
  def download_report(self, reportId, db_handle):
    self.oauth2()
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
                   subType
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
    headers = {'Authorization' : 'Bearer ' + self.auth_token}
    reply = requests.post(URL, params={'query': query}, headers=headers)
    if reply.status_code != 200:
      print("WCL first report query failed with error: " + str(reply.status_code))
      return False
    reply = reply.json()
    report = reply["data"]["reportData"]["report"]
    if not report:
      print("Invalid report ID: " + str(reportId))
      return False
      
    fights = report["fights"]
    characters = report["masterData"]["actors"]

    #now query for the fight we want
    for fight in fights:
      print(fight['name'])
      if fight["name"] == "Fankriss the Unyielding":
        start_time = fight["startTime"]
        end_time = fight["endTime"]
        break
    print(start_time, end_time)
    
    #now query for the equipment data for that fight

    query = """
         { 
           reportData {
             report (code: "%s") {
              code
              events (startTime: %d, endTime: %d) { #first event is the character gear data dump
                data
              }
             }
           }
         }""" % (reportId, start_time, end_time)
    headers = {'Authorization' : 'Bearer ' + self.auth_token}
    reply = requests.post(URL, params={'query': query}, headers=headers)
    if reply.status_code != 200:
      print("WCL event query failed with error: " + str(reply.status_code))
      return False
    reply = reply.json()
    events = reply["data"]["reportData"]["report"]["events"]["data"]

    for event in events:
      if event["type"] == "combatantinfo":
        source_id = event["sourceID"]
        #first add characters to the db with ids
        db_handle.queue_add_player(characters[source_id]["gameID"],characters[source_id]["name"],characters[source_id]["subType"])
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
    return True
