import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import tensorflow as tf
import tensorflow_hub as hub
from langchain.prompts import PromptTemplate
from langchain import LLMChain
from langchain.chat_models import AzureChatOpenAI

# Function to find similar records based on fuzzy matching
def find_similar_records(input_data, data_frame):
    results = []
    for index, row in data_frame.iterrows():
        brand_similarity = fuzz.ratio(input_data['Brand'], row['Brand'])
        # type_similarity = fuzz.ratio(input_data['Type'], row['Type'])
        description_similarity = fuzz.ratio(input_data['Description'], row['Description'])
        # product_line_similarity = fuzz.ratio(input_data['Product Line'], row['Product Line'])
        # category_similarity = fuzz.ratio(input_data['Category'], row['Category'])
        # text_similarity = fuzz.token_set_ratio(input_data['Text'], row['Text'])
        
        # Calculate the average similarity score
        # average_similarity = (brand_similarity + type_similarity + description_similarity +
        #                       product_line_similarity + category_similarity + text_similarity*3) / 8
        average_similarity = (brand_similarity + description_similarity ) / 2

        # Add the record and similarity score to the results list
        if average_similarity > 70:
            results.append((row, average_similarity))

    # Sort the results based on similarity score in descending order
    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results

def find_best_feature(input_data, input_value):
  variable_dict = {}
  for variable, value in zip(input_data, input_value):
      if variable in variable_dict:
          variable_dict[variable] += value
      else:
          variable_dict[variable] = value

  sorted_dict = {k: v for k, v in sorted(variable_dict.items(), key=lambda item: item[1], reverse=True)}

  return sorted_dict

def category_using_openAI(input_data):
  try:
    # Access the values of the desired columns
    brand = input_data['Brand']
    # _type = input_data['Type']
    description = input_data['Description']
    # category = input_data['Category']
    # Product_Line = input_data['Product Line']

    # query = f"Brand: {brand}, type: {_type}, Description: {description}, Product Line: {Product_Line}, Kind: {category}. Forget my previous question. Which item belongs to which category? (food, beverages or non-food)."
    query = f"Brand: {brand}, Description: {description}. Forget my previous question. Which item belongs to which category? (food, beverages or non-food)."
    # df.at[index, 'openai__category'] = 1
    # row['openai__category'] = classifier_category_chain(query)['text']
    return classifier_category_chain(query)['text']

  except:
    print("error in openAI")
    return "error"
  
def maingroup_using_openAI(input_data, input_category):
  try:
    # Access the values of the desired columns
    brand = input_data['Brand']
    # _type = input_data['Type']
    description = input_data['Description']
    # category = input_data['Category']
    # Product_Line = input_data['Product Line']

    if input_category == "food":
      # query = f"""Type: {_type}, Description: {description}, Product Line: {Product_Line}, Kind: {category}. Forget my previous question. Which item belongs to which category?
      query = f"""Brand: {brand}, Description: {description}. Forget my previous question. Which item belongs to which category?
(JUST ONE category in this list:
1. Arabic Sweet
2. bakery products
3. Bakery Products Fresh
4. confectionery
5. Cooked Food
6. dairy products
7. Dairy Products Fresh
8. Fish and Seafood Fresh
9. Fish and Seafood Frozen
10. Fruit Fresh
11. Fruits Frozen
12. ice cream
13. Juices Fresh
14. Meat Chilled
15. meat deep frozen
16. Mövenpick Fine Foods
17. potatoes
18. Poultry Fresh
19. Poultry Frozen
20. Processed Meat Cold Cuts
21. Sauces and Dressing
22. Vegetables fresh
23. Vegetables Frozen
24. dried products
25. Pasta Fresh and Frozen). """

      return classifier_food_chain(query)['text']

    elif input_category == "beverages":
      # query = f"""Type: {_type}, Description: {description}, Product Line: {Product_Line}, Kind: {category}. Forget my previous question. Which item belongs to which category?
      query = f"""Brand: {brand}, Description: {description} . Forget my previous question. Which item belongs to which category?
(JUST ONE category in this list:
1. alcoholic beverages
2. non-alcoholic beverages
3. hot drinks
4. fruit juices
"""
      return classifier_beverages_chain(query)['text']

    elif input_category == "non food":
      # query = f"""Brand: {brand}, type: {_type}, Description: {description}, Product Line: {Product_Line}. Forget my previous question. Which item belongs to which category?
      query = f"""Brand: {brand}, Description: {description}. Forget my previous question. Which item belongs to which category?
(MUST ONE category in this list:
1. consumables
2. cleaning products
3. uniforms
4. chinaware
5. office supplies
6. small kitchen items
7. stewarding
8. Illuminant
9. small pastry items
10. miscellaneous
11. collaterals
12. Electronic
13. Linen
14. housekeeping
15. Ironware
16. buffet item
17. children's concept
18. glassware
19. Spa and Wellness
20. tabletop
21. furniture
22. label
23. menus
24. packaging
25. cutlery
26. service material
27. technology
28. bar
29. consumables with logo
30. Drugs
31. Means of promotion and give aways
32. .packaging with logo
33. Retail
34. tool
"""
      return classifier_nonfood_chain(query)['text']
    return ' '
  except:
    print("error in openAI")
    return "error"

def subgroup_using_openAI(input_data, input_category, input_maingroup, df_subgroup):
  brand = input_data['Brand']
  # _type = input_data['Type']
  description = input_data['Description']
  # category = input_data['Category']
  # Product_Line = input_data['Product Line']

  filtered_df = df_subgroup[(df_subgroup['Categories(English)'] == input_category) & (df_subgroup['Main Group(English)'].str.lower() == input_maingroup)]
  subgroup_values = filtered_df['Sub-group(English)'].tolist()

  if subgroup_values == []:
    return " "
  elif len(subgroup_values) == 1:
    return subgroup_values[0]
  else:
    formatted_string = ""
    for index, item in enumerate(subgroup_values, start=1):
        formatted_string += f"{index}. {item}\n"

    classifier = """<|im_start|>system
You MUST forget all everything before processing this process
You answer the question "Which item belongs to which category?"
Given a sentence, assistant will determine if the sentence belongs in 1 of these categories, which are:
{formatted_string}

FOR EXAMPLE OF Output:
Output: "Dairy Products Fresh"
Output: "dried products"
Output: "Meat Chilled"
Output: "Vegetables fresh"
Output: "Vegetables Frozen"
Output: "meat deep frozen"
Output: "Sauces and Dressing"
Output: "Processed Meat"
Output: "Fish and Seafood Frozen"
Output: "Fish and Seafood Fresh"
Output: "Fruits Frozen"
Output: "Poultry Fresh"
Output: "Poultry Frozen"
Output: "potatoes"
Output: "Pasta Fresh and Frozen"
Output: "Mövenpick Fine Foods"
Output: "ice cream"
Output: "dairy products"
Output: "bakery products"
Output: "Juices Fresh"
Output: "Fruit Fresh"
Output: "confectionery"
Output: "Cooked Food"
Output: "Cold Cuts"
Output: "Arabic Sweet"

<|im_end|>

Input: {question}
<|im_start|>assistant
Output:"""

    query = f"""Brand: {brand}, Description: {description}. Forget my previous question. Which item belongs to which category?
({formatted_string})."""

    # print(query)
    classifier_chain = LLMChain(llm=llm3, prompt=PromptTemplate.from_template(classifier))

    return classifier_chain({'question': query, 'formatted_string': formatted_string})['text']

def full_classify(input_data, data_frame, df_master_data):
  # Find similar records
  similar_records = find_similar_records(input_data, data_frame)
  # print("Total matching feature:", len(similar_records))

  #defind variable
  record_list = []
  similarity_data_matching = []
  category_data_matching = []
  main_group_data_matching = []
  subgroup_data_matching = []

  # Print the top most similar records
  for record, similarity in similar_records:
      # print(f"Similarity: {similarity}")
      # print(type(record))
      # print("________________________________________________________________________________________")
      record_list.append(record.to_dict())
      similarity_data_matching.append(similarity)
      category_data_matching.append(record['raw__category'])
      main_group_data_matching.append(record['raw__main_group'])
      subgroup_data_matching.append(record['raw__subgroup'])

  # print("result of matching category:", find_best_feature(category_data_matching, similarity_data_matching))
  main_group_list = find_best_feature(main_group_data_matching, similarity_data_matching)
  # print("result of matching main group:", main_group_list)
  subgroup_list = find_best_feature(subgroup_data_matching, similarity_data_matching)
  # print("result of matching subgroup:", subgroup_list)
  # print("______________________________________________________________________________________")

  #-------------------------------------------------------------------------------------------------

  #category
  result_category = ' '
  if len(set(category_data_matching)) ==  0:
    #openAI
    if "error" in category_using_openAI(input_data).lower():
      result_category = ' '
    elif "non" in category_using_openAI(input_data).lower():
      result_category = "non food"
    elif "beverages" in category_using_openAI(input_data).lower():
      result_category = "beverages"
    else:
      result_category = "food"
  elif len(set(category_data_matching)):
    #data_matching
    result_category = next(iter(find_best_feature(category_data_matching, similarity_data_matching)))

  # print("result_category:", result_category)

  #-------------------------------------------------------------------------------------------------

  #main group
  result_maingroup = ' '
  maingroup_record_list = [d for d in record_list if d.get('raw__category') == result_category]
  available_maingroup_list = [d['raw__main_group'] for d in maingroup_record_list]
  unique_available_maingroup_list = list(set(available_maingroup_list))
  main_group_list = {key: main_group_list[key] for key in unique_available_maingroup_list if key in main_group_list}
  main_group_list = dict(sorted(main_group_list.items(), key=lambda x: x[1], reverse=True))

  if len(set(main_group_list)) ==  0:
    #openAI
    result_maingroup = maingroup_using_openAI(input_data, result_category).lower()
    list_maingroup = df_master_data["Main Group(English)"][df_master_data["Categories(English)"] == result_category].drop_duplicates().tolist()
    print("Maingroup by OpenAI:", result_maingroup)

    if "error" in result_maingroup:
      result_maingroup = 'error'
    elif result_maingroup not in list_maingroup:
      flag = False
      for main_item in list_maingroup:
        if main_item.lower() in result_maingroup:
          flag = True
          result_maingroup = main_item.lower()
          break
      if flag == False:
        result_maingroup = "other"

    # elif "belongs to the category" in result_maingroup:
    #   for m_item in list_maingroup:
    #     if m_item.lower() in result_maingroup:
    #       result_maingroup = m_item.lower()
    #       break
    # if result_maingroup not in list_maingroup:
    #   result_maingroup = "other"

  elif len(set(main_group_list)):
    #data_matching
    result_maingroup = next(iter(find_best_feature(main_group_list, similarity_data_matching)))

  # print("result_maingroup:", result_maingroup)


  #-------------------------------------------------------------------------------------------------

  #sub group
  result_subgroup = ' '
  if result_maingroup != "other":
    subgroup_record_list = [d for d in record_list if d.get('raw__main_group') == result_maingroup]
    available_subgroup_list = [d['raw__subgroup'] for d in subgroup_record_list]
    unique_available_subgroup_list = list(set(available_subgroup_list))
    subgroup_list = {key: subgroup_list[key] for key in unique_available_subgroup_list if key in subgroup_list}
    subgroup_list = dict(sorted(subgroup_list.items(), key=lambda x: x[1], reverse=True))

    if len(set(subgroup_list)) ==  0:
      #openAI
      result_subgroup = subgroup_using_openAI(input_data, result_category, result_maingroup, df_master_data).lower()
      list_subgroup = df_master_data["Sub-group(English)"][(df_master_data["Categories(English)"] == result_category) & (df_master_data["Main Group(English)"].str.lower() == result_maingroup)].drop_duplicates().tolist()
      print("Subgroup by OpenAI:", result_subgroup)
      if "error" in result_subgroup:
        result_subgroup = "error"
      elif result_subgroup not in list_subgroup:
        flag = False
        for sub_item in list_subgroup:
          if sub_item.lower() in result_subgroup:
            flag = True
            result_subgroup = sub_item
            break
        if flag == False:
          result_subgroup = "other"
      # elif "belongs to the category" in result_subgroup:
      #   for sub_item in list_subgroup:
      #     if sub_item.lower() in result_subgroup:
      #       result_subgroup = sub_item
      #       break
      # if result_subgroup not in list_subgroup:
      #   result_subgroup = "other"
    elif len(set(subgroup_list)):
      #data_matching
      result_subgroup = next(iter(find_best_feature(subgroup_list, similarity_data_matching)))
  else:
    result_subgroup = "other"

  # print("result_subgroup:", result_subgroup)
  return result_category, result_maingroup, result_subgroup

file_path = 'validate_data_test.xlsx'
all_df = pd.read_excel(file_path)
init_data_frame =  all_df[all_df['validate_catagories'].notnull()]
init_data_frame = init_data_frame[['Product Code', 'Brand', 'Type', 'Description', 'Product Line', 'Category', 'Text','validate_catagories', 'validate_maingroup', 'validate_subgroup']]
init_data_frame.rename(columns = {'validate_catagories' : 'raw__category', 'validate_maingroup' : 'raw__main_group', 'validate_subgroup' : 'raw__subgroup'}, inplace = True)
init_data_frame = init_data_frame.fillna("")
data_frame = init_data_frame

df_master_data = pd.read_excel('Supplier_Info_Master.xlsx')
df_master_data["Main Group(English)"] = df_master_data["Main Group(English)"].str.lower()
df_master_data["Sub-group(English)"] = df_master_data["Sub-group(English)"].str.lower()

test_dataset = pd.read_excel("clean_data_raw2.xlsx")
test_dataset = test_dataset.fillna("")

classifier_category = """<|im_start|>system
Given a sentence, assistant will determine if the sentence belongs in 1 of 3 categories, which are:
- food
- beverages
- non-food
You MUST just answer 1 word.
You MUST forget all everything before processing this process
You answer the question "Which item belongs to which category? (food, beverages or non-food)"
Spices, SNACKS (sugar, SALT, ...), DAIRY, VEGETABLES, FRUIT, PASTRY, PIZZAS, OILS & FATS, READY MEALS, READY SNACKS, SAUCE are considered food.
juice, beer, wine, water, SPIRITS ... are considered beverages.

<|im_end|>

Input: {question}
<|im_start|>assistant
Output:"""

classifier_food = """<|im_start|>system
You MUST forget all everything before processing this process
You answer the question "Which item belongs to which category?"
Given a sentence, assistant will determine if the sentence belongs in 1 of these categories, which are:
1. Arabic Sweet
2. bakery products
3. Bakery Products Fresh
4. confectionery
5. Cooked Food
6. dairy products
7. Dairy Products Fresh
8. Fish and Seafood Fresh
9. Fish and Seafood Frozen
10. Fruit Fresh
11. Fruits Frozen
12. ice cream
13. Juices Fresh
14. Meat Chilled
15. meat deep frozen
16. Mövenpick Fine Foods
17. potatoes
18. Poultry Fresh
19. Poultry Frozen
20. Processed Meat Cold Cuts
21. Sauces and Dressing
22. Vegetables fresh
23. Vegetables Frozen
24. dried products
25. Pasta Fresh and Frozen



FOR EXAMPLE OF Output:
Output: "Dairy Products Fresh"
Output: "dried products"
Output: "Meat Chilled"
Output: "Vegetables fresh"
Output: "Vegetables Frozen"
Output: "meat deep frozen"
Output: "Sauces and Dressing"
Output: "Processed Meat"
Output: "Fish and Seafood Frozen"
Output: "Fish and Seafood Fresh"
Output: "Fruits Frozen"
Output: "Poultry Fresh"
Output: "Poultry Frozen"
Output: "potatoes"
Output: "Pasta Fresh and Frozen"
Output: "Mövenpick Fine Foods"
Output: "ice cream"
Output: "dairy products"
Output: "bakery products"
Output: "Juices Fresh"
Output: "Fruit Fresh"
Output: "confectionery"
Output: "Cooked Food"
Output: "Cold Cuts"
Output: "Arabic Sweet"

<|im_end|>

Input: {question}
<|im_start|>assistant
Output:"""

classifier_beverages= """<|im_start|>system
You MUST follow these rule:
- You answer the question "Which item belongs to which category?"
- Kind of "tea", "coffee", "CHOCOLATE", "TEA", "COFFEE": are considered "hot drinks" category
- You MUST forget all everything before processing this process

Given a sentence, assistant will determine if the sentence belongs in 1 of these categories, which are:
1. alcoholic beverages
2. non-alcoholic beverages
3. hot drinks
4. fruit juices

FOR EXAMPLE OF Output:
Output: "alcoholic beverages"
Output: "non-alcoholic beverages"
Output: "hot drinks"
Output: "fruit juices"


<|im_end|>

Input: {question}
<|im_start|>assistant
Output:"""

classifier_non_food= """<|im_start|>system
You MUST forget all everything before processing this process
You answer the question "Which item belongs to which category?"
Given a sentence, assistant will determine if the sentence belongs in 1 of these categories, which are:
1. consumables
2. cleaning products
3. uniforms
4. chinaware
5. office supplies
6. small kitchen items
7. stewarding
8. Illuminant
9. small pastry items
10. miscellaneous
11. collaterals
12. Electronic
13. Linen
14. housekeeping
15. Ironware
16. buffet item
17. children's concept
18. glassware
19. Spa and Wellness
20. tabletop
21. furniture
22. label
23. menus
24. packaging
25. cutlery
26. service material
27. technology
28. bar
29. consumables with logo
30. Drugs
31. Means of promotion and give aways
32. .packaging with logo
33. Retail
34. tool

FOR EXAMPLE OF Output:
Output: "alcoholic beverages"
Output: "non-alcoholic beverages"
Output: "hot drinks"
Output: "fruit juices"


<|im_end|>

Input: {question}
<|im_start|>assistant
Output:"""

llm2 = AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_base='https://openai-nois-intern.openai.azure.com/',
            openai_api_version="2023-03-15-preview",
            deployment_name='gpt-35-turbo',
            openai_api_key='',
            temperature=0.5,
            max_tokens=1000
        )

llm3 = AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_base='https://openai-nois-intern.openai.azure.com/',
            openai_api_version="2023-03-15-preview",
            deployment_name='gpt-35-turbo-16k',
            openai_api_key='',
            temperature=0.4,
            max_tokens=1000
        )
classifier_category_chain = LLMChain(llm = llm2, prompt = PromptTemplate.from_template(classifier_category))
classifier_food_chain = LLMChain(llm = llm3, prompt = PromptTemplate.from_template(classifier_food))
classifier_beverages_chain = LLMChain(llm = llm3, prompt = PromptTemplate.from_template(classifier_beverages))
classifier_nonfood_chain = LLMChain(llm = llm3, prompt = PromptTemplate.from_template(classifier_non_food))

df_subgroup = df_master_data
result_dataset = test_dataset
result_dataset['data_matching_category'] = np.nan
result_dataset['data_matching_main_group'] = np.nan
result_dataset['data_matching_subgroup'] = np.nan
result_dataset

for index, row in result_dataset.iterrows():

  try:
    input_data = {
        'Brand': row['Brand'],
        'Description': row['Item Description'],
        'Text': row['Text']
    }

    classify_result = full_classify(input_data, data_frame, df_master_data)

    result_dataset.at[index, 'data_matching_category'] = classify_result[0]
    result_dataset.at[index, 'data_matching_main_group'] = classify_result[1]
    result_dataset.at[index, 'data_matching_subgroup'] = classify_result[2]

    print(f"{index}  {classify_result}")
    print("============================================")
  except:
    result_dataset.at[index, 'data_matching_category'] = ' '
    result_dataset.at[index, 'data_matching_main_group'] = ' '
    result_dataset.at[index, 'data_matching_subgroup'] = ' '
    print(f"{index}  {classify_result}")
    print("============================================")
    pass
  
result_dataset.to_excel('result_matching_raw.xlsx', index=False)