import tkinter

UNRESOLVED_ITEM_TEXT = "Unresolved Items: %d"

class DBWidget:
  def __init__(self, root, gridx, gridy, loot_db, wcl_api_handle, resolve_items):
    self.frame = tkinter.Frame(root, bd=2, relief=tkinter.RAISED)
    self.frame.grid(column=gridx, row=gridy, sticky='nsew')
    
    self.loot_db = loot_db #keep a reference
    self.wcl_api_handle = wcl_api_handle
    self.resolve_items_external = resolve_items

    self.report_id_label = tkinter.Label(self.frame, text="WCL Report ID:")
    self.report_id = tkinter.Entry(self.frame)

    self.download_button = tkinter.Button(self.frame, text="Download Report", command=self.download_report)
    
    self.resolve_items_stringvar = tkinter.StringVar()
    self.resolve_items_label = tkinter.Label(self.frame, textvariable=self.resolve_items_stringvar)
    self.resolve_items_stringvar.set(UNRESOLVED_ITEM_TEXT % len(self.loot_db.get_unresolved_item_ids()))
    self.resolve_items_button = tkinter.Button(self.frame, text="Resolve Items", command=self.resolve_items)

    self.report_id_label.grid(row=0, column=0)
    self.report_id.grid(row=1, column=0)
    self.download_button.grid(row=2, column=0)
    self.resolve_items_label.grid(row=3, column=0)
    self.resolve_items_button.grid(row=4, column=0)

  def download_report(self):
    if self.wcl_api_handle.download_report(self.report_id.get(), self.loot_db):
      print("Report Downloaded Successfully")
    self.resolve_items_stringvar.set(UNRESOLVED_ITEM_TEXT % len(self.loot_db.get_unresolved_item_ids()))
  
  def resolve_items(self):
    self.resolve_items_external()
    self.resolve_items_stringvar.set(UNRESOLVED_ITEM_TEXT % len(self.loot_db.get_unresolved_item_ids()))


