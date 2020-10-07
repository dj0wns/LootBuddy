import sqlite3
import os
import sys

class LootDB:
  def __init__(self, db_file):
    self.db_file = db_file
    self.init_db()
    self.command_queue = []
    
  def init_db(self):
    sql_commands = []
    sql_commands.append("PRAGMA foreign_keys = ON;")
    #raids table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS raids (
                              id integer NOT NULL PRIMARY KEY,
                              name text UNIQUE NOT NULL COLLATE NOCASE
                              );""")


    #bosses table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS bosses (
                              id integer NOT NULL PRIMARY KEY,
                              raid integer NOT NULL,
                              name text UNIQUE NOT NULL COLLATE NOCASE,
                              CONSTRAINT fk_raid FOREIGN KEY(raid) REFERENCES raids(id) ON DELETE CASCADE
                              );""")
    #items table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS items (
                              id integer NOT NULL PRIMARY KEY,
                              name text COLLATE NOCASE,
                              slot integer default -1,
                              armor integer default 0,
                              classes text default "" COLLATE NOCASE,
                              itemset integer default 0,
                              agility integer default 0,
                              intelligence integer default 0,
                              spirit integer default 0,
                              stamina integer default 0,
                              strength integer default 0,
                              melee_crit_percentage integer default 0,
                              melee_hit_percentage integer default 0,
                              ranged_crit_percentage integer default 0,
                              ranged_hit_percentage integer default 0,
                              attack_power integer default 0,
                              ranged_attack_power integer default 0,
                              spell_healing integer default 0,
                              spell_power integer default 0,
                              spell_crit_percentage integer default 0,
                              spell_hit_percentage integer default 0,
                              spell_penetration integer default 0,
                              mana_per_5 integer default 0,
                              speed integer default 0,
                              dps integer default 0
                              ) WITHOUT ROWID;""")
    
    #tokens table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS tokens (
                              id integer NOT NULL PRIMARY KEY,
                              token integer NOT NULL,
                              reward integer NOT NULL,
                              CONSTRAINT fk_token FOREIGN KEY(token) REFERENCES items(id) ON DELETE CASCADE,
                              CONSTRAINT fk_reward FOREIGN KEY(reward) REFERENCES items(id) ON DELETE CASCADE,
                              UNIQUE(token, reward)
                              );""")
    
    #drops table - links items to bosses
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS drops (
                              id integer NOT NULL PRIMARY KEY,
                              boss integer NOT NULL,
                              item integer NOT NULL,
                              CONSTRAINT fk_boss FOREIGN KEY(boss) REFERENCES bosses(id) ON DELETE CASCADE,
                              CONSTRAINT fk_item FOREIGN KEY(item) REFERENCES items(id) ON DELETE CASCADE,
                              UNIQUE(boss, item)
                              );""")
    #players table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS players (
                              id integer NOT NULL PRIMARY KEY,
                              name text UNIQUE NOT NULL COLLATE NOCASE,
                              last_updated datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
                              ) WITHOUT ROWID;""")
    #equipped item table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS playergear (
                              id integer NOT NULL PRIMARY KEY,
                              item integer NOT NULL,
                              player integer NOT NULL,
                              last_updated datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                              CONSTRAINT fk_item FOREIGN KEY(item) REFERENCES items(id) ON DELETE CASCADE,
                              CONSTRAINT fk_player FOREIGN KEY(player) REFERENCES player(id) ON DELETE CASCADE,
                              UNIQUE(item, player)
                              );""")

    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      for sql_command in sql_commands:
        c.execute(sql_command)
      conn.commit()
    except Exception as e:
      print(e)
    finally:
      conn.close()

  def get_raid_list(self):
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      c.execute("Select id, name from raids")
      return c.fetchall()
    except Exception as e:
      print(e)
    finally:
      conn.close()
  
  def get_boss_list(self, raid_index):
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      c.execute("SELECT id, name FROM bosses WHERE raid=?", (raid_index,))
      return c.fetchall()
    except Exception as e:
      print(e)
    finally:
      conn.close()
  
  def get_loot_list_for_boss(self, boss_index):
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      c.execute("""SELECT a.id, a.name 
                     FROM items a
                     JOIN drops b on b.item = a.id
                     WHERE b.boss=?
                     ORDER BY a.name""", (boss_index,))
      return c.fetchall()
    except Exception as e:
      print(e)
    finally:
      conn.close()
  
  def get_item_by_name(self, name):
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      c.execute("SELECT id FROM items WHERE name=?", (name, ))
      return c.fetchall()
    except Exception as e:
      print(e)
    finally:
      conn.close()
  
  def get_unresolved_item_ids(self):
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      c.execute("SELECT id FROM items WHERE slot=-1 and id IS NOT NULL")
      return c.fetchall()
    except Exception as e:
      print(e)
    finally:
      conn.close()

  def execute_queue(self):
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      for sql_command in self.command_queue:
        c.execute(sql_command[0], sql_command[1])
      conn.commit()
      self.command_queue = []
    except Exception as e:
      print(e)
    finally:
      conn.close()
  
  def queue_update_item(self, item_id, stats_dict):
    #Warning this command is susceptible to sql injection so don't get MITM'd by wowhead lmao
    command = """ UPDATE items
                    SET """
    args = ()
    for key, value in stats_dict.items():
      command = command + key + "=?, "
      args = args + (value,)
    command = command[:-2] #remove trailing comma and space
    command = command + " WHERE id=? "
    args = args + (item_id,)
    self.command_queue.append([command, args])

  def queue_add_player(self, id, name):
    self.command_queue.append([""" INSERT OR IGNORE INTO players(id, name)
                                 values(?, ?) """,
                               (id, name)])
  
  def queue_add_item_by_id(self, id):
    self.command_queue.append([""" INSERT OR IGNORE INTO items(id)
                                 values(?) """,
                               (id,)])

  def queue_add_item_player_link(self, item_id, player_id):
    self.command_queue.append([""" INSERT OR IGNORE INTO playergear(item, player)
                                 values(?, ?) """,
                               (item_id, player_id)])

  def queue_delete_player_gear(self, player_id):
    self.command_queue.append([""" DELETE FROM playergear
                                   WHERE player=?""",
                               (player_id,)])

  
  def populate_items_in_db(self, items_path, blizz_api):
    sql_commands = []
    tokens_to_add = [] #list of lists, first cell is token name, second is cell name
    items_path_len = len(os.path.normpath(items_path).split(os.path.sep))
    for root, dirpath, files in os.walk(items_path):
      tokenized_root = os.path.normpath(root).split(os.path.sep)
      if len(tokenized_root) <1:
        #Root dir boring
        continue
      if tokenized_root[-1] == "Special":
        #special file rules for token items
        for file in files:
          with open(os.path.join(root,file)) as item_file:
            items = [item.rstrip('\n') for item in item_file]
          for item in items:
            #first see if item exists already
            if not self.get_item_by_name(item):
              #if item does not exist get name from blizz api
              print(item)
              try:
                item_id = blizz_api.get_item_id_from_name(item)
              except OSError as err:
                print("OS error: {0}".format(err))  
                #skip item if something broke
                continue
              if item_id:
                sql_commands.append([""" INSERT OR IGNORE INTO items(id, name)
                                   values(?, ?) """,
                                   (item_id, item)])
            tokens_to_add.append([file, item])
        
      if "items.txt" in files:
        #lazy way of doing it, always insert if doesnt exist
        #insert raid
        sql_commands.append([""" INSERT OR IGNORE INTO raids(name)
                                 values(?) """,
                              (tokenized_root[-2],)])
        #insert boss
        sql_commands.append([""" INSERT OR IGNORE INTO bosses(raid, name)
                                 values((SELECT id FROM raids WHERE name=?), ?) """,
                              (tokenized_root[-2], tokenized_root[-1])])
        with open(os.path.join(root,"items.txt")) as item_file:
          items = [item.rstrip('\n') for item in item_file]
        for item in items:
          #first see if item exists already
          if not self.get_item_by_name(item):
            #if item does not exist get name from blizz api
            print(item)
            try:
              item_id = blizz_api.get_item_id_from_name(item)
            except OSError as err:
              print("OS error: {0}".format(err))  
              #skip item if something broke
              continue
            if item_id:
              sql_commands.append([""" INSERT OR IGNORE INTO items(id, name)
                                 values(?, ?) """,
                                 (item_id, item)])
            else:
              #error
              continue
            
          #then create in drops table
          sql_commands.append([""" INSERT OR IGNORE INTO drops(boss, item)
                                 values((SELECT id FROM bosses WHERE name=?), 
                                        (SELECT id FROM items WHERE name=?)) """,
                              (tokenized_root[-1], item)])
    #now bind tokens
    for token in tokens_to_add:
      sql_commands.append([""" INSERT OR IGNORE INTO tokens(token, reward) 
                                SELECT a.id, b.id FROM items
                                JOIN items a on a.name=?
                                JOIN items b on b.name=?
                          """,
                          (token[0], token[1])])
    try:
      conn = sqlite3.connect(self.db_file)
      c = conn.cursor()
      for sql_command in sql_commands:
        c.execute(sql_command[0], sql_command[1])
      conn.commit()
    except Exception as e:
      print(e)
    finally:
      conn.close()
      
    

