resto_druid = { "armor"                  : 0.0,
                "agility"                : 0.0,
                "intelligence"           : 1.0,
                "spirit"                 : 0.5,
                "stamina"                : 0.1,
                "strength"               : 0.0,
                "melee_crit_percentage"  : 0.0,
                "melee_hit_percentage"   : 0.0,
                "ranged_crit_percentage" : 0.0,
                "ranged_hit_percentage"  : 0.0,
                "attack_power"           : 0.0,
                "ranged_attack_power"    : 0.0,
                "spell_healing"          : 2.0,
                "spell_power"            : 0.0,
                "spell_crit_percentage"  : 1.0,
                "spell_hit_percentage"   : 0.0,
                "spell_penetration"      : 0.0,
                "mana_per_5"             : 1.0,
                "speed"                  : 0.0,
                "dps"                    : 0.0}




def calculate_recommendation_score(player, new_item, old_item):
  if player["class"] == 0:
    stat_weight = resto_druid 
  else:
    return False
  new_item_score = 0
  old_item_score = 0
  stat_change = {}
  for key, value in stat_weight.items():
    new_item_score = new_item_score + new_item[key] * value
    old_item_score = old_item_score + old_item[key] * value
    stat_change[key] = new_item[key] - old_item[key]
  print("%s - %s : score uplift of %f. (new(%s): %f, old(%s): %f)" 
          % (player["class"],
             player["name"], 
             new_item_score - old_item_score,
             new_item["name"],
             new_item_score,
             old_item["name"],
             old_item_score))
  stat_delta = "Stat Delta: "
  for key, value in stat_change.items():
    if stat_change[key]:
      stat_delta = stat_delta + " " + key + ": " + str(value)  
  print(stat_delta)
    


    


