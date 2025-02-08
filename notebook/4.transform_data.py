import pandas as pd
import numpy as np
import re

def get_item_descript(item_descript, rules, measure):
    res_lst = []
    for rule in rules:
        temp = rule[0].replace(".", "[.]").replace("%", "\d+")
        temp = r"\b" + temp + r"\b"
        temp_measure = "(?:" + "|".join(measure) +")"
        # print(temp)
        res = re.findall(temp.replace("_", temp_measure) ,item_descript)
        # res = list(filter(None,lst))
        
        if res:
           
            for i in res:
                item_descript = item_descript.replace(i, "")

            res_lst += [(res, rule[1])]
    # print(item_descript)
    if res_lst:
        return pd.Series([res_lst, item_descript])
    return pd.Series([None, None])

def modify_item_description(item_descript, measure_units):
    rule = item_descript[1]
    item_descript = item_descript[0][0]
    # find numbers in the item description
    numbers = re.findall(r'\d+', item_descript)
    
    # replace each '%' in the rule with the found numbers
    modified_rule = rule.replace('%', '{}', len(numbers))
    
    # insert the found numbers into the rule
    modified_rule = modified_rule.format(*numbers)
    
    # replace '_' with measure units from item_descript
    measures = re.findall(f'({"|".join(measure_units)})', item_descript)
    
    for measure in measures:
        modified_rule = modified_rule.replace('_', measure, 1)

    return modified_rule

def apply_and_concat(df, field, func, column_names):
    return pd.concat((df, df[field].apply(lambda cell: pd.Series(func(cell), index=column_names))), axis=1)

def modify_item_description(item_descript, measure_units):
    rule = item_descript[1]
    item_descript = item_descript[0][0]
    # find numbers in the item description
    numbers = re.findall(r'\d+', item_descript)
    
    # replace each '%' in the rule with the found numbers
    modified_rule = rule.replace('%', '{}', len(numbers))
    
    # insert the found numbers into the rule
    modified_rule = modified_rule.format(*numbers)
    
    # replace '_' with measure units from item_descript
    measures = re.findall(f'({"|".join(measure_units)})', item_descript)
    
    for measure in measures:
        modified_rule = modified_rule.replace('_', measure, 1)

    return modified_rule

descript_rules = pd.read_excel("description_rules.xlsx")
all_df = pd.read_excel("all_data_ver.xlsx")
all_df = all_df[["Product Code", "Description"]]
weight = descript_rules["Weight"].dropna().tolist()
volume = descript_rules["Volume"].dropna().tolist()
length = descript_rules["Length"].dropna().tolist()
apply = descript_rules["Apply"].dropna().tolist()
transform = descript_rules["Transform"].dropna().tolist()
rules = list(zip(apply, transform))
measure = weight + volume + length

all_df[["Get Item", "New Description"]] = all_df["Description"].apply(get_item_descript, args=(rules, measure))