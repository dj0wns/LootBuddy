import tkinter


class OutputWidget:
  def __init__(self, root, gridx, gridy):
    self.frame = tkinter.Frame(root, bd=2, relief=tkinter.RAISED)
    self.frame.grid(column=gridx, row=gridy, sticky='nsew')
    #self.frame.grid_columnconfigure(0, weight=1)
    #self.frame.grid_rowconfigure(0, weight=1)
    
    self.text_box = tkinter.Text(self.frame, state="disabled", wrap="none")

    
    self.text_box.tag_config("positive", foreground="green")
    self.text_box.tag_config("negative", foreground="red")
    self.text_box.tag_config("bold", font=("Georgia", "10", "bold"))

    self.text_box.pack(expand=True, fill=tkinter.BOTH)

  def update_text_box(self, item_upgrade_list):
    item_upgrade_list = sorted(item_upgrade_list, key = lambda i: i["score_uplift"], reverse = True)
    self.text_box.configure(state="normal") #reenable box for editing
    #clear textbox
    self.text_box.delete("1.0", tkinter.END)
    for item_dict in item_upgrade_list:
      self.text_box.insert(tkinter.END, '(')
      self.text_box.insert(tkinter.END, "%.1f" % item_dict["score_uplift"], "positive" if item_dict["score_uplift"] > 0 else "negative")
      self.text_box.insert(tkinter.END, ') ')
      self.text_box.insert(tkinter.END, item_dict["name"], "bold")
      self.text_box.insert(tkinter.END, ' - ')
      self.text_box.insert(tkinter.END, item_dict["spec"])
      self.text_box.insert(tkinter.END, '[')
      self.text_box.insert(tkinter.END, item_dict["role"])
      self.text_box.insert(tkinter.END, '] ')
      self.text_box.insert(tkinter.END, 'Replaces: ')
      self.text_box.insert(tkinter.END, item_dict["old_item_name"])
      self.text_box.insert(tkinter.END, '\n\t')
      for key, value in item_dict["stat_change_dict"].items():
        #only print changes
        if value:
          self.text_box.insert(tkinter.END, key)
          self.text_box.insert(tkinter.END, ": ")
          self.text_box.insert(tkinter.END, "%d" % value,  "positive" if value > 0 else "negative")
          self.text_box.insert(tkinter.END, ", ")
      self.text_box.insert(tkinter.END, '\n')
    self.text_box.configure(state="disabled") #redisable when finished

