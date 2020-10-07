import sqlite3
import os

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
                              name text UNIQUE NOT NULL
                              );""")


    #bosses table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS bosses (
                              id integer NOT NULL PRIMARY KEY,
                              raid integer NOT NULL,
                              name text UNIQUE NOT NULL,
                              CONSTRAINT fk_raid FOREIGN KEY(raid) REFERENCES raids(id) ON DELETE CASCADE
                              );""")
    #items table
    sql_commands.append(""" CREATE TABLE IF NOT EXISTS items (
                              id integer NOT NULL PRIMARY KEY,
                              name text UNIQUE,
                              item_id integer UNIQUE
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
                              name text UNIQUE NOT NULL,
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
  
  def get_item_list(self, boss_index):
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

  def queue_add_player(self, id, name):
    self.command_queue.append([""" INSERT OR IGNORE INTO players(id, name)
                                 values(?, ?) """,
                               (id, name)])
  
  def queue_add_item_by_id(self, id):
    self.command_queue.append([""" INSERT OR IGNORE INTO items(item_id)
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

  
  def populate_items_in_db(self, items_path):
    sql_commands = []
    items_path_len = len(os.path.normpath(items_path).split(os.path.sep))
    for root, dirpath, files in os.walk(items_path):
      tokenized_root = os.path.normpath(root).split(os.path.sep)
      if len(tokenized_root) <1:
        #Root dir boring
        continue
      if tokenized_root[-1] == "Special":
        #special file rules for token items
        None
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
          #first add item to item list
          sql_commands.append([""" INSERT OR IGNORE INTO items(name)
                                 values(?) """,
                              (item,)])
          #then create in drops table
          sql_commands.append([""" INSERT OR IGNORE INTO drops(boss, item)
                                 values((SELECT id FROM bosses WHERE name=?), 
                                        (SELECT id FROM items WHERE name=?)) """,
                              (tokenized_root[-1], item)])
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
      
    

