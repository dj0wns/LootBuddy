import os
import tkinter
import tkinter.filedialog
import json
from lib import loot_db, loot_menu, db_widget, wcl_api, wowhead_api, blizz_api

fpath = os.path.realpath(__file__)
path = os.path.dirname(fpath)
lib_path = os.path.join(path,"lib")
DB_NAME = os.path.join(path,"loot.db")
BOSS_ITEMS = os.path.join(lib_path,"loot_names")

WCL_TOKEN_FILE = os.path.join(path,"wcl_client.txt") 
WCL_SECRET_FILE = os.path.join(path,"wcl_secret.txt")
BLIZZ_TOKEN_FILE = os.path.join(path,"blizz_client.txt") 
BLIZZ_SECRET_FILE = os.path.join(path,"blizz_secret.txt")

WINDOW_TITLE = "Loot Buddy!"

def parse_tooltip(tooltip):
  #returns a dict of all stats the item has
  stats = {}
  #intrinsic item values
  if "slotbak" in tooltip:
    stats["slot"] = tooltip["slotbak"]
  else :
    print("ITEM DOES NOT HAVE A SLOT SHOULD NEVER HAPPEN")
    

  if "armor" in tooltip:
    stats["armor"] = tooltip["armor"]
  if "classes" in tooltip:
    stats["classes"] = tooltip["classes"]
  if "itemset" in tooltip:
    stats["itemset"] = tooltip["itemset"]


  #Primary Stats
  if "agi" in tooltip:
    stats["agility"] = tooltip["agi"]
  if "int" in tooltip:
    stats["intelligence"] = tooltip["int"]
  if "spi" in tooltip:
    stats["spirit"] = tooltip["spi"]
  if "sta" in tooltip:
    stats["stamina"] = tooltip["sta"]
  if "str" in tooltip:
    stats["strength"] = tooltip["str"]

  #secondary Stats
  if "mlecritstrkpct" in tooltip:
    stats["melee_crit_percentage"] = tooltip["mlecritstrkpct"]
  if "mlehitpct" in tooltip:
    stats["melee_hit_percentage"] = tooltip["mlehitpct"]
  if "rgdcritstrkpct" in tooltip:
    stats["ranged_crit_percentage"] = tooltip["rgdcritstrkpct"]
  if "rgdhitpct" in tooltip:
    stats["ranged_hit_percentage"] = tooltip["rgdhitpct"]
  if "atkpwr" in tooltip:
    stats["attack_power"] = tooltip["atkpwr"]
  if "rgdatkpwr" in tooltip:
    stats["ranged_attack_power"] = tooltip["rgdatkpwr"]
  if "splheal" in tooltip:
    stats["spell_healing"] = tooltip["splheal"]
  if "splpwr" in tooltip:
    stats["spell_power"] = tooltip["splpwr"]
  if "splcritstrkpct" in tooltip:
    stats["spell_crit_percentage"] = tooltip["splcritstrkpct"]
  if "splhitpct" in tooltip:
    stats["spell_hit_percentage"] = tooltip["splhitpct"]
  if "splpen" in tooltip:
    stats["spell_penetration"] = tooltip["splpen"]
  if "manargn" in tooltip:
    stats["mana_per_5"] = tooltip["manargn"]

  #weapon stats
  if "speed" in tooltip:
    stats["speed"] = tooltip["speed"]
  if "dps" in tooltip:
    stats["dps"] = tooltip["dps"]

  return stats

if __name__ == '__main__':
  blizz_api_ = blizz_api.BlizzardApiHandle(BLIZZ_TOKEN_FILE, BLIZZ_SECRET_FILE)
  
  loot_db_ = loot_db.LootDB(DB_NAME)
  loot_db_.populate_items_in_db(BOSS_ITEMS, blizz_api_)
  
  wcl_api_ = wcl_api.WarcraftLogsApiHandle(WCL_TOKEN_FILE, WCL_SECRET_FILE)


  def loot_recommendation_callback():
    None

  def resolve_items():
    #Get and parse wowhead tooltips
    item_list = loot_db_.get_unresolved_item_ids()
    for item in item_list:
      if not item[0]:
        #empty slot, ignore
        continue
      name, tooltip_dict = wowhead_api.get_tooltip_from_item_id(item[0])
      if not tooltip_dict:
        #reached error, end update but make sure to update valid queries
        break;
      stats = parse_tooltip(tooltip_dict)
      stats["name"] = name #make sure to update name aswell
      loot_db_.queue_update_item(item[0], stats)
      print(stats) #kind of like a progress tracker i guess
      loot_db_.execute_queue()
  
  #build window root
  #left frame is item selector
  #right frame is best replacements + current item
  tk = tkinter.Tk()
  tk.geometry("720x480")
  tk.grid_columnconfigure(0, weight=1)
  tk.grid_columnconfigure(1, weight=1)
  tk.grid_rowconfigure(0, weight=10)
  tk.grid_rowconfigure(1, weight=2)
  tk.title(WINDOW_TITLE)
  left_frame = loot_menu.LootMenu(tk, 0, 0, loot_db_, loot_recommendation_callback)
  db_frame = db_widget.DBWidget(tk, 0, 1, loot_db_, wcl_api_, resolve_items)

  tk.mainloop()
  

