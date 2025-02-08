import pandas as pd
import xml.etree.ElementTree as ET

def has_number(string):
    return any(char.isnumeric() for char in string)

# Read the Excel file
df = pd.read_excel('result_matching_raw.xlsx')
df = df.astype(str)

# Create the root element
root = ET.Element('FUTURELOG')

# Create the HEAD element and its child
head = ET.SubElement(root, 'HEAD')
validity = ET.SubElement(head, 'VALIDITY')
validity.text = '25092023'

# Create the ARTICLES element
articles = ET.SubElement(root, 'ARTICLES')

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
# for index, row in df.head(100).iterrows(): 
    # Create the ARTICLE element
    article = ET.SubElement(articles, 'ARTICLE')

    # Create and populate the child elements of ARTICLE based on the column values
    name = ET.SubElement(article, 'NAME')
    longname = ET.SubElement(article, 'LONGNAME')
    orgname = ET.SubElement(article, 'ORGNAME')
    articledata = ET.SubElement(article, 'ARTICLEDATA')
    categories = ET.SubElement(article, 'CATEGORIES')
    maingroups = ET.SubElement(article, 'MAINGROUPS')
    groups = ET.SubElement(article, 'GROUPS')
    prices = ET.SubElement(article, 'PRICES')

    # Create and populate the child elements of NAME based on the column values
    de = ET.SubElement(name, 'DE')

    gb = ET.SubElement(name, 'GB')
    gb.text = row['Item Description']

    fr = ET.SubElement(name, 'FR')
    it = ET.SubElement(name, 'IT')
    nl = ET.SubElement(name, 'NL')
    tr = ET.SubElement(name, 'TR')
    vn = ET.SubElement(name, 'VN')
    th = ET.SubElement(name, 'TH')

    # Create and populate the child elements of LONGNAME based on the column values
    de_longname = ET.SubElement(longname, 'DE')
    gb_longname = ET.SubElement(longname, 'GB')
    gb_longname.text = row['Item Description']

    fr_longname = ET.SubElement(longname, 'FR')
    it_longname = ET.SubElement(longname, 'IT')
    nl_longname = ET.SubElement(longname, 'NL')
    tr_longname = ET.SubElement(longname, 'TR')
    vn_longname = ET.SubElement(longname, 'VN')
    th_longname = ET.SubElement(longname, 'TH')

    # Create and populate the child elements of ORGNAME based on the column values
    de_orgname = ET.SubElement(orgname, 'DE')

    gb_orgname = ET.SubElement(orgname, 'GB')
    gb_orgname.text = row['Item Description']

    fr_orgname = ET.SubElement(orgname, 'FR')
    it_orgname = ET.SubElement(orgname, 'IT')
    nl_orgname = ET.SubElement(orgname, 'NL')
    tr_orgname = ET.SubElement(orgname, 'TR')
    vn_orgname = ET.SubElement(orgname, 'VN')
    th_orgname = ET.SubElement(orgname, 'TH')

    # Create and populate the child elements of ARTICLEDATA based on the column values
    ugid = ET.SubElement(articledata, 'UGID')
    ugid.text = row['x']

    item_type = ET.SubElement(articledata, 'ITEM_TYPE')
    item_type.text = row['Item Type']

    brand = ET.SubElement(articledata, 'BRAND')
    brand.text = row['Brand']

    text_doc = ET.SubElement(articledata, 'TEXT')
    text_doc.text = row['Text']

    artno = ET.SubElement(articledata, 'ARTNO')
    ean = ET.SubElement(articledata, 'EAN')
    # ean.text = row['GTIN Bar Code']

    spec = ET.SubElement(articledata, 'SPEC')

    ingred = ET.SubElement(articledata, 'INGRED')
    # ingred.text = row['Ingredients']

    picurl = ET.SubElement(articledata, 'PICURL')
    # picurl.text = row['Img URL']
    # if type(row['Img URL']) is str:
    #     picurl.text = row['Img URL']
    # picurl.text = ' '

    custno = ET.SubElement(articledata, 'CUSTNO')
    manartno = ET.SubElement(articledata, 'MANARTNO')
    org = ET.SubElement(articledata, 'ORG')
    # org.text = row['Country of Origin']

    # Create and populate the child elements of CATEGORIES based on the column values
    category = ET.SubElement(categories, 'CATEGORY')

    # Create and populate the child elements of CATEGORY based on the column values
    cid = ET.SubElement(category, 'CID')
    name_category = ET.SubElement(category, 'NAME')
    de_category_name = ET.SubElement(name_category, 'DE')
    gb_category_name = ET.SubElement(name_category, 'GB')
    gb_category_name.text = row['data_matching_category']
    # print(type(row['raw__category']), row['raw__category'])

    # if type(row['raw__category']) is str:
    #     gb_category_name.text = row['raw__category']
    # gb_category_name.text = ' '

    fr_category_name = ET.SubElement(name_category, 'FR')
    it_category_name = ET.SubElement(name_category, 'IT')
    nl_category_name = ET.SubElement(name_category, 'NL')
    tr_category_name = ET.SubElement(name_category, 'TR')
    vn_category_name = ET.SubElement(name_category, 'VN')
    th_category_name = ET.SubElement(name_category, 'TH')

    # Create and populate the child elements of MAINGROUPS based on the column values
    maingroup = ET.SubElement(maingroups, 'MAINGROUP')

    # Create and populate the child elements of MAINGROUP based on the column values
    mgid_maingroup = ET.SubElement(maingroup, 'MGID')
    
    name_maingroup = ET.SubElement(maingroup, 'NAME')
    de_maingroup_name = ET.SubElement(name_maingroup, 'DE')
    gb_maingroup_name = ET.SubElement(name_maingroup, 'GB')
    gb_maingroup_name.text = row['data_matching_main_group']

    # if type(row['raw__main_group']) is str:
    #     gb_maingroup_name.text = row['raw__main_group']
    # gb_maingroup_name.text = ' '

    fr_maingroup_name = ET.SubElement(name_maingroup, 'FR')
    it_maingroup_name = ET.SubElement(name_maingroup, 'IT')
    nl_maingroup_name = ET.SubElement(name_maingroup, 'NL')
    tr_maingroup_name = ET.SubElement(name_maingroup, 'TR')
    vn_maingroup_name = ET.SubElement(name_maingroup, 'VN')
    th_maingroup_name = ET.SubElement(name_maingroup, 'TH')

    # Create and populate the child elements of MAINGROUPS based on the column values
    group = ET.SubElement(groups, 'GROUP')

    # Create and populate the child elements of MAINGROUP based on the column values
    ugid = ET.SubElement(group, 'UGID')
    name_group = ET.SubElement(group, 'NAME')
    de_group_name = ET.SubElement(name_group, 'DE')
    gb_group_name = ET.SubElement(name_group, 'GB')
    gb_group_name.text = row['data_matching_subgroup']

    # if type(row['raw__subgroup']) is str:
    #     gb_group_name.text = row['raw__subgroup']
    # gb_group_name.text = ' '

    fr_group_name = ET.SubElement(name_group, 'FR')
    it_group_name = ET.SubElement(name_group, 'IT')
    nl_group_name = ET.SubElement(name_group, 'NL')
    tr_group_name = ET.SubElement(name_group, 'TR')
    vn_group_name = ET.SubElement(name_group, 'VN')
    th_group_name = ET.SubElement(name_group, 'TH')

    # Create and populate the child elements of MAINGROUPS based on the column values
    price = ET.SubElement(prices, 'PRICE')

    # Create and populate the child elements of PRICE based on the column values
    custid = ET.SubElement(price, 'CUSTID')

    prcou = ET.SubElement(price, 'PRCOU')
    # prcou.text = row['Unit Price']

    prclev = ET.SubElement(price, 'PRCLEV')
    
    prcoff = ET.SubElement(price, 'PRCOFF')

    ou = ET.SubElement(price, 'OU')
    # ou.text = row['Uom']

    cu = ET.SubElement(price, 'CU')
    # nucuou = ET.SubElement(price, 'NUCUOU')

    # if has_number(row['Pack Size']):
    #     cu.text = row['Pack Size'][-2:]
    #     nucuou.text =  row['Pack Size'][:-2]
    # else:
    #     cu.text = row['Pack Size']
    #     nucuou.text = '1'

    vlz = ET.SubElement(price, 'VLZ')
    offstart = ET.SubElement(price, 'OFFSTART')
    offend = ET.SubElement(price, 'OFFEND')
    coreitem = ET.SubElement(price, 'COREITEM')

# Create the XML tree
tree = ET.ElementTree(root)

# Save the XML to a file
tree.write('result_matching_raw.xml', encoding='utf-8', xml_declaration=True)

