import tkinter

class LootMenu:
  def __init__(self, root, gridx, gridy, loot_db, loot_recommendation_callback):
    self.frame = tkinter.Frame(root, bd=0, relief=tkinter.SUNKEN)
    self.frame.grid(column=gridx, row=gridy, sticky='nsew')

    self.loot_db = loot_db #keep a reference
    self.raid_list = None
    self.boss_list = None
    self.item_list = None
    self.raid_names = None
    self.boss_names = None
    self.item_names = None

    self.selected_raid = tkinter.StringVar(self.frame)
    self.selected_boss = tkinter.StringVar(self.frame)
    self.selected_item = tkinter.StringVar(self.frame)
    
    self.update_options(1,1) #sqlite is 1 indexed for whatever reason

    self.selected_raid_menu = tkinter.OptionMenu(self.frame, self.selected_raid, *self.raid_names)
    self.selected_boss_menu = tkinter.OptionMenu(self.frame, self.selected_boss, *self.boss_names)
    self.selected_item_menu = tkinter.OptionMenu(self.frame, self.selected_item, *self.item_names)

    self.selected_raid.trace('w', self.selection_update)
    self.selected_boss.trace('w', self.selection_update)

    self.selected_raid_menu.grid(row=0, column=0)
    self.selected_boss_menu.grid(row=0, column=1)
    self.selected_item_menu.grid(row=1, column=0)

  def selection_update(self, var, idx, mode):
    raid = 0 #reset if invalid state
    boss = 0 #reset if invalid state
    if self.selected_raid.get() in self.raid_names:
      raid = self.raid_list[self.raid_names.index(self.selected_raid.get())][0] #get raid id from name list
    if self.selected_boss.get() in self.boss_names:
      boss = self.boss_list[self.boss_names.index(self.selected_boss.get())][0] #get raid id from name list
    self.update_options(raid, boss)
    #now update dropdowns
    self.selected_raid_menu['menu'].delete(0, 'end')
    self.selected_boss_menu['menu'].delete(0, 'end')
    self.selected_item_menu['menu'].delete(0, 'end')
    for name in self.raid_names:
      self.selected_raid_menu['menu'].add_command(label=name, command=tkinter._setit(self.selected_raid, name))
    for name in self.boss_names:
      self.selected_boss_menu['menu'].add_command(label=name, command=tkinter._setit(self.selected_boss, name))
    for name in self.item_names:
      self.selected_item_menu['menu'].add_command(label=name, command=tkinter._setit(self.selected_item, name))

  def update_options(self,raid,boss):
    self.raid_list = self.loot_db.get_raid_list()
    self.boss_list = self.loot_db.get_boss_list(raid)
    self.item_list = self.loot_db.get_item_list(boss)
    self.raid_names = [raid[1] for raid in self.raid_list]
    self.boss_names = [boss[1] for boss in self.boss_list]
    self.item_names = [item[1] for item in self.item_list]
    
    self.selected_raid.set(self.raid_names[raid-1]) #adjust for 1 indexed
    self.selected_boss.set(self.boss_names[boss-1]) #adjust for 1 indexed
    self.selected_item.set(self.item_names[0])


    
