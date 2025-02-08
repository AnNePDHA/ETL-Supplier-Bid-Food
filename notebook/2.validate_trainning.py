import time
import pandas as pd
import numpy as np
import datetime
import os
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INPUT_URL = "Foodlink Raw Data File.xlsx"
TRAINING_URL = "all_data.xlsx"
similarity_threshold = 0.8

def convert_lower(text):
    return text.lower()

def strip_text(text):
   return text.strip()

def remove_stopwords(text):
  stop_words = set(stopwords.words('english'))
  words = word_tokenize(text)
  return [x for x in words if x not in stop_words]

def lemmatize_word(text):
  wordnet = WordNetLemmatizer()
  return " ".join([wordnet.lemmatize(word) for word in text])

def special_char(text):
  reviews = ''
  for x in text:
    if x.isalpha():
      reviews = reviews + x
    else:
      reviews = reviews + ' '
  return reviews

def replace_char(text):
  replace_lst = [' mx', ' cm', ' mm', ' s ', ' g', ' kg', ' gr', ' per', ' x ', ' lt']
  for replace_item in replace_lst:
    if replace_item in text:
      text = text. replace(replace_item, ' ')
  return " ".join(text.split())

def subgroup_appear_times(df_clean_data, product_code):
    subgroup = df_clean_data.loc[df_clean_data['Product Code'] == int(product_code)]['raw__subgroup'].item()
    mask = df_clean_data['raw__subgroup'] == subgroup
    return subgroup, (len(df_clean_data[mask]))

def find_match_lst(row, df1):
    max_score = -1
    res = []
    for index, row1 in df1.iterrows():
        
        score = fuzz.token_set_ratio(row["Text"], row1["Text"])
        # print(f'{row["Text"]} : {row_1["Text"]} : {score}')
        if (score > 90) and (row["raw__subgroup"] != row1["raw__subgroup"]):
            # print(f'{row["Product Code"]} : {row_1["Product Code"]}')
            res += [row1["Product Code"]]
    if res == []:
        res = None
    # print(res)
    return res

def find_best_match(row, df1):
    max_score = -1
    best_match = None

    for index, row1 in df1.iterrows():
        score = fuzz.token_set_ratio(row["Text"], row1["Text"])
        if score > max_score:
            max_score = score
            best_match = row1["validate_subgroup"]

    return best_match

master_data = pd.read_excel("Supplier_Info_Master.xlsx")
df = pd.read_excel(TRAINING_URL)
input_df = pd.read_excel(INPUT_URL)

for col in master_data.columns:
    master_data[col] = master_data[col].apply(convert_lower)
    master_data[col] = master_data[col].apply(strip_text)
    master_data[col] = master_data[col].str.replace("_x000D_\n","")

input_df = input_df[["x", "Item Description", "Item Type", "Brand"]]
input_df = input_df.replace("-", None)
input_df = input_df.fillna("")
input_df["Text"] = input_df["Item Description"] + ", " + input_df['Brand']
input_df.to_excel("clean_data_raw2.xlsx", index = False)

all_data = df[["Product Code", "Brand", "Type", "Description", "Product Line", "Category", "Supplier Description", "raw__category", "raw__main_group","raw__subgroup"]]
# all_data = df[["x", "Item Description", "Item Type", "Brand"]]
all_data.dropna(subset=["raw__subgroup"], inplace=True)
all_data = all_data.replace("-", None)
all_data = all_data.fillna("")
all_data["Text"] = all_data['Brand'] + ", " + all_data["Type"] + ", " + all_data["Description"] + ", " + all_data["Product Line"]  + "," + all_data["Category"] + "," + all_data["Supplier Description"] 
all_df1 = all_data.reset_index(drop = True)
all_df1["Text"] = all_df1["Text"].apply(convert_lower)
all_df1["Text"] = all_df1["Text"].apply(remove_stopwords)
all_df1["Text"] = all_df1["Text"].apply(lemmatize_word)
all_df1["Text"] = all_df1["Text"].apply(special_char)
all_df1["Text"] = all_df1["Text"].apply(replace_char)

tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(all_df1['Text'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

result_rows = []
for idx, row in all_df1.iterrows():
    subgroup = row['raw__subgroup']
    cleaned_text = row['Text']
    # Remove characters with numbers up to the nearest space
    # cleaned_text = re.sub(r'\S*\d+\S*', '', row['Text']).strip()
    
    # similar subgroups based on cosine similarity
    similar_indices = (cosine_sim[idx] > similarity_threshold).nonzero()[0]
    
    # Exclude duplicates from the 'similar subgroups'
    similar_indices = [i for i in similar_indices if all_df1.iloc[i]['raw__subgroup'] != subgroup]
    similar_pc = [all_df1.iloc[i]['Product Code'] for i in similar_indices if all_df1.iloc[i]['raw__subgroup'] != subgroup]
    
    # Store the similar subgroups and text
    similar_subgroups = ", ".join(set(all_df1.iloc[similar_indices]['raw__subgroup']) - {subgroup})
    
    if similar_subgroups and cleaned_text:  # Only add rows where "Similar Subgroups" is not blank and text is not empty
        # print(idx)

        # print(similar_indices)
        c_subgroup = len(all_df1[all_df1['raw__subgroup'] == subgroup])
        subgroup_new = subgroup 
        for i in similar_pc:
            temp_subgroup, c_temp_subgroup = subgroup_appear_times(all_df1, i)
            if c_temp_subgroup > c_subgroup:
                c_subgroup = c_temp_subgroup
                subgroup_new = temp_subgroup
                
        if subgroup_new == subgroup:
            subgroup_new = None        
        print(f'{row["Product Code"]}: Similar Product code: {similar_pc} - subgroup: {subgroup} - New subgroup: {subgroup_new}')
        result_rows.append({'Product Code' : row['Product Code'], 'Text': cleaned_text, 'validate_subgroup': subgroup, 'Similar Product Code' : similar_pc, 'New Subgroup': subgroup_new})
        
# Create df from the result rows
result_df = pd.DataFrame(result_rows, columns = ['Product Code', 'Text', 'validate_subgroup', 'Similar Product Code', 'New Subgroup'])
all_df2 = pd.merge(all_df1, result_df, on = ['Product Code', 'Text'], how = 'outer')
all_df2.loc[all_df2['New Subgroup'].isnull(), 'validate_subgroup'] = all_df2["raw__subgroup"]
all_df2.loc[all_df2['New Subgroup'].notnull(), 'validate_subgroup'] = all_df2["New Subgroup"]
all_df2 = all_df2.drop(['Similar Product Code', 'New Subgroup'], axis=1)
all_df2["subgroup_count"] = all_df2.groupby(["validate_subgroup"])["Product Code"].transform("count")
df1 = all_df2[all_df2['subgroup_count'] >= 6]
df2 = all_df2[all_df2['subgroup_count'] < 6]
df2["best_match"] = df2.apply(find_best_match, args=(df1,), axis=1)
all_df2 = pd.merge(all_df2, df2, on = ['Product Code', 'Brand', 'Type', 'Description', 'Product Line', 'Category', 'Supplier Description', 'Text', 'raw__category', 'raw__main_group', 'raw__subgroup', 'validate_subgroup', 'subgroup_count'], how = 'outer')
all_df2.loc[all_df2['best_match'].notnull(), 'validate_subgroup'] = all_df2["best_match"]
all_df2 = all_df2.drop(['subgroup_count', 'best_match'], axis = 1)
res_df = pd.merge(all_df2, master_data, how = 'left', left_on = 'validate_subgroup', right_on = 'Sub-group(English)').drop(['Sub-group(English)'], axis = 1)
res_df.rename(columns = {'Categories(English)' : 'validate_catagories', 'Main Group(English)' : 'validate_maingroup'}, inplace = True)
res_df = res_df[["Product Code", "Brand", "Type", "Description", "Product Line", "Category", "Supplier Description", "Text", "raw__category", "raw__main_group", "raw__subgroup", "validate_catagories", "validate_maingroup", 'validate_subgroup']]
res_df.to_excel("validate_data_test.xlsx", index=False)