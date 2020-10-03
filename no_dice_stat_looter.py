import os
import tkinter
import tkinter.filedialog
from lib import loot_db, loot_menu

fpath = os.path.realpath(__file__)
path = os.path.dirname(fpath)
lib_path = os.path.join(path,"lib")
DB_NAME = os.path.join(path,"loot.db")
BOSS_ITEMS = os.path.join(lib_path,"loot_names")

WINDOW_TITLE = "No Dice Loot Extravaganza"

if __name__ == '__main__':
  loot_db_ = loot_db.LootDB(DB_NAME)
  loot_db_.populate_items_in_db(BOSS_ITEMS)
  def loot_recommendation_callback():
    None
  #build window root
  #left frame is item selector
  #right frame is best replacements + current item
  tk = tkinter.Tk()
  tk.geometry("720x480")
  tk.grid_columnconfigure(0, weight=1)
  tk.grid_columnconfigure(1, weight=1)
  tk.grid_rowconfigure(0, weight=1)
  tk.title(WINDOW_TITLE)
  left_frame = loot_menu.LootMenu(tk, 0, 0, loot_db_, loot_recommendation_callback)

  tk.mainloop()
  

