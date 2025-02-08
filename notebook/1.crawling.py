from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import datetime
import os
import requests

def login(driver):
    username_field = driver.find_element(By.ID, "UserName")
    password_field = driver.find_element(By.ID, "Password")
    login_button = driver.find_element(By.ID, "submitBtn")
    username_field.send_keys("")
    password_field.send_keys("")
    login_button.click()

def get_all_item_ID(driver):
    xpath='/html/body/div[2]/div[3]/header/div[4]/div/ul'
    tab = driver.find_element(By.XPATH, xpath)
    all_tab = tab.find_elements(By.TAG_NAME, "li")
    
    get_data_time = datetime.datetime.now()
    error_page = []
    element = [] 
    for index, li_element in enumerate(all_tab, start=1):
        li_xpath = xpath + f"/li[{index}]"
            #print(f"Li element {index} XPath:", li_xpath)
           
        if(index not in [1,2,3,4,5]):
            #click to tab
            wait = WebDriverWait(driver, 10)  # 10 seconds timeout
            page = wait.until(EC.visibility_of_element_located((By.XPATH, li_xpath)))
            page.click()
            
            time.sleep(5)
            #click to all product
            all_pro_xpath = '//*[@id="mega-menu-id"]/div/div[2]/div[1]/div[1]/span'
            wait = WebDriverWait(driver, 10)
            view_all_product = wait.until(EC.visibility_of_element_located((By.XPATH, all_pro_xpath)))
            view_all_product.click()


            #get the number of page
            if(index==10): 
                time.sleep(20)
            else: 
                time.sleep(10)
            wait = WebDriverWait(driver, 10)
            pageCount = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "page-count")))
            pageCount = int(pageCount.text.split(' ')[1])
            print("Total Pages:", pageCount)
            pageCount = pageCount + 1 
            try: 
                for i in range(1,pageCount):
                    #get all product displayed on screen
                    wait = WebDriverWait(driver, 20)
                    product_list = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "productList")))
                    time.sleep(5)
                    #get list of product code displayed in screen
                    pro = product_list.find_elements(By.CSS_SELECTOR, ".title-wrapper .productCode")
                    
                    print("Page",i ,"------",len(pro))
                    for x in pro:
                        print(x.text)
                        element = element + [x.text]
                        
                    if i == pageCount - 1: break
                   
                    target_ng_click = "nextPage()"
                    xpath_expression = f"//a[@ng-click='{target_ng_click}']"
                    wait = WebDriverWait(driver, 10)
                    nextPage = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_expression)))
                    nextPage.click()
                    time.sleep(3)
                    
            except StaleElementReferenceException:
                error_page = error_page + [(index,i)]
                print("Element became stale.")
            print("====================================")
    return element, get_data_time, error_page


def get_item_discription(driver, item_lst, item_url):
    df = []
    error_ID = []
    for item in item_lst:
        print(item)
        get_data_time = datetime.datetime.now()
        url = item_url + item
        driver.get(url)
        time.sleep(5)
        
        try:
            #get the item's description
            wait = WebDriverWait(driver, 10)
            title = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".productDetail h1")))
            title = title.text.split(' - ')
            #get type
            product_type = title[1]
            #get description
            description = title[0]
            wait = WebDriverWait(driver, 10)
            product_info = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "product-info"))).text
            #['Brand:', 'BRYOPIN MEATS', 'Product Line:', 'PORK', 'Category:', 'PORK PORTIONED', 'Tax Rate:', '0%', 'Past Qty:', '-', 'Warehouse:', 'E360DEMO - BIDFOOD BOTANY']
            product_info = product_info.split('\n') 

            #get the brand
            brand = product_info[1]
            #get product line
            product_line = product_info[3]
            #get category
            category = product_info[5]
            # Get tax
            tax = product_info[7]
            
            # Get warehouse
            warehouse = product_info[-1]
            
            # Get the pack_size
            wait = WebDriverWait(driver, 10)
            pack_size_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".packSize .value")))
            
            pack_size = pack_size_list[0].text
            Ctn_qty = '1'
            if len(pack_size_list) > 1: Ctn_qty = pack_size_list[1].text
            
            #get the UOM
            wait = WebDriverWait(driver, 10)
            UOM_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".UOM .type")))
            
            UOM = UOM_list[0].text
            container_UOM = UOM_list[0].text
            if len(UOM_list) > 1:
                container_UOM = UOM_list[1].text
            
            #get stock
            wait = WebDriverWait(driver, 10)
            stock_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".stock .stock-status")))
            
            stock = stock_list[0].text
            container_quanity = stock_list[0].text
            if len(stock_list) > 1:
                container_quanity = stock_list[1].text
                
            #get price
            wait = WebDriverWait(driver, 10)
            price_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".itemPrice .price")))
            
            unit_price = price_list[0].text
            container_price = price_list[0].text
            if len(price_list) > 1:
                container_price = price_list[1].text
            
            
            wait = WebDriverWait(driver, 10)
            image = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".detailImage")))
            
            img_url = image.get_attribute("src")
            img_name = "BidFood-" + item + '.jpg'
            img_path = os.path.join("images", img_name)
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open(img_path, "wb") as img_file:
                    img_file.write(img_response.content)
                print(f"Image {img_name} saved.")
            else:
                print(f"Failed to download image {img_name}. Status code: {img_response.status_code}")
            item_info = [item, brand, product_type, description, product_line, category, warehouse,pack_size, UOM, Ctn_qty, container_UOM, stock, container_quanity, unit_price, container_price, tax, img_name, get_data_time]
            #print(title)
            df = df + [item_info]
            print(item_info)
            #print(pack_size,UOM,stock,price)
            print("=========")
        except Exception as e:
            error_ID = error_ID + [item]
            print("An error occurred:", e)
    return df, error_ID

def check_exists_by_css_celector(driver, css_selector):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    return True

def get_additional_information(driver):
    additional_info = {}
    table_info = []
    lst_additional_info = driver.find_element(By.CSS_SELECTOR, ".additional-info ul").text.split('\n')

    for item in lst_additional_info:
        view_additional_info = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, item)))
        view_additional_info.click()
        try:
            temp_info = {}
            no_table_information = driver.find_element(By.CSS_SELECTOR, ".additional-info .tab-content").text
            list_cols = driver.find_elements(By.CSS_SELECTOR, ".additional-info .tab-content .col-xs-4")
            cols_text = [item.text for item in list_cols]
            list_info = driver.find_elements(By.CSS_SELECTOR, ".additional-info .tab-content .col-xs-8")
            info_text = [item.text for item in list_info]
            #if(item in ["Packaging"]): print(test)
            table_information = driver.find_elements(By.CSS_SELECTOR, ".additional-info .table")
            # redunt_lst = driver.find_elements(By.CSS_SELECTOR, ".additional-info .tab-content .panel-title")
            # redunt_text = [item.text for item in redunt_lst if item.text != '']
            # print(redunt_text)
            table_list = []
            for table in table_information:
                if table.text =='': continue
                index = no_table_information.find(table.text)
                no_table_information = no_table_information[0:index] + no_table_information[index+len(table.text):]

                row = table.find_elements(By.CSS_SELECTOR, "tr")
                column_name = row[0].find_elements(By.CSS_SELECTOR, "th")
                list_column = []

                temp_table = {}
                for i in column_name:
                    temp_table[i.text] =[]
                    list_column.append(i.text)
                for value in row[1:]:
                    x = value.find_elements(By.CSS_SELECTOR, "td")
                    for i in range(len(x)):
                        if x[i].text == '': temp_table[list_column[i]].append(None)
                        else:
                            temp_table[list_column[i]].append(x[i].text)
                if '' in temp_table.keys():
                    del temp_table['']
                table_list.append(temp_table)
            print(table_list) 
            no_table_information =  [item for item in no_table_information.split('\n') if item != '']
        
            print(no_table_information)
            for i in range(0, len(cols_text)):
                if cols_text[i] != '':
                # print(f'{cols_text[i]} : {info_text[i]}')
                    if info_text[i] != '':
                        # print(f'{cols_text[i]} : {info_text[i]}')
                        temp_info[cols_text[i]] = info_text[i]
                    else:
                        temp_info[cols_text[i]] = None
                
            additional_info.update(temp_info)
            table_info += table_list
            
        except NoSuchElementException:
            print("No table")

        print("********************************")     
    return additional_info, table_info

driver = webdriver.Chrome()
login_url = 'https://au-shopv5.uat.bdirectcloud.net'
driver.get(login_url)
os.makedirs("images", exist_ok = True)
login(driver)

xpath='/html/body/div[2]/div[3]/header/div[4]/div/ul'
tab = driver.find_element(By.XPATH, xpath)
all_tab = tab.find_elements(By.TAG_NAME, "li")
# print(all_tab)
get_data_time = datetime.datetime.now()
error_page = []
element = {}
for index, li_element in enumerate(all_tab, start=1):
    li_xpath = xpath + f"/li[{index}]"
    # print(f"Li element {index} XPath:", li_xpath)
    if index not in [1, 2, 3, 4, 5]:
        element[index] = []
        wait = WebDriverWait(driver, 10)  # 10 seconds timeout
        page = wait.until(EC.visibility_of_element_located((By.XPATH, li_xpath)))
        page.click()
        
        time.sleep(7)
        #click to all product
        all_pro_xpath = '//*[@id="mega-menu-id"]/div/div[2]/div[1]/div[1]/span'
        wait = WebDriverWait(driver, 10)
        view_all_product = wait.until(EC.visibility_of_element_located((By.XPATH, all_pro_xpath)))
        view_all_product.click()


        #get the number of page
        if(index==10): 
            time.sleep(20)
        else: 
            time.sleep(10)
        wait = WebDriverWait(driver, 10)
        pageCount = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "page-count")))
        pageCount = int(pageCount.text.split(' ')[1])
        print("Total Pages:", pageCount)
        pageCount = pageCount + 1
        try: 
            for i in range(1,pageCount):
                #get all product displayed on screen
                wait = WebDriverWait(driver, 20)
                product_list = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "productList")))
                time.sleep(5)
                #get list of product code displayed in screen
                pro = product_list.find_elements(By.CSS_SELECTOR, ".title-wrapper .productCode")
                print("Page",i ,"------",len(pro))
                for x in pro:
                    print(x.text)
                    element[index] = element[index] + [x.text]
                    
                if i == pageCount - 1: break
                
                target_ng_click = "nextPage()"
                xpath_expression = f"//a[@ng-click='{target_ng_click}']"
                wait = WebDriverWait(driver, 10)
                nextPage = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_expression)))
                nextPage.click()
                time.sleep(3)
                
        except StaleElementReferenceException:
            error_page = error_page + [(index,i)]
            print("Element became stale.")

all_df = pd.DataFrame({"Product Code": []})
error_ID = []
item_url = "https://au-shopv5.uat.bdirectcloud.net/#/products/detail/"
item_lst = []
for item in element:
    item_lst += item
for item in item_lst:
    print(item)
    item_info = {
        'Product Code' : [],
        'Brand' : [],
        "Type" : [],
        "Description" : [],
        "Product Line" : [],
        "Category" : [],
        "Small Unit Warehouse" : [],
        "Container Warehouse" : [],
        "Pack Size" : [],
        "Uom" : [],
        "Ctn Qty" : [],
        "Ctn Uom" : [],
        "Unit Stock" : [],
        "Ctn Stock" : [],
        "Unit Price" : [],
        "Ctn Price" : [],
        "Tax%" : [],
        "Img Name" : [],
        "Img URL" : [],
        "Get data time" : []
    }
    get_data_time = datetime.datetime.now()
    url = item_url + item
    driver.get(url)
    time.sleep(4)
    
    # try:
        #get the item's description
    wait = WebDriverWait(driver, 10)
    title = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".productDetail h1")))
    title = title.text.split(' - ')

    #get type
    product_type = title[1]
    
    #get description
    description = title[0]
    
    wait = WebDriverWait(driver, 10)
    product_info = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "product-info"))).text
    #['Brand:', 'BRYOPIN MEATS', 'Product Line:', 'PORK', 'Category:', 'PORK PORTIONED', 'Tax Rate:', '0%', 'Past Qty:', '-', 'Warehouse:', 'E360DEMO - BIDFOOD BOTANY']
    product_info = product_info.split('\n') 

    #get the brand
    brand = product_info[1]
    #get product line
    product_line = product_info[3]
    #get category
    category = product_info[5]
    #get tax
    tax = product_info[7]
    
    #get warehouse
    warehouse = product_info[-1]
    
    #get the pack_size
    wait = WebDriverWait(driver, 10)
    pack_size_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".packSize .value")))
    
    pack_size = pack_size_list[0].text
    Ctn_qty = '1'
    if len(pack_size_list) > 1: Ctn_qty = pack_size_list[1].text
    
    #get the UOM
    wait = WebDriverWait(driver, 10)
    UOM_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".UOM .type")))
    
    UOM = UOM_list[0].text
    container_UOM = UOM_list[0].text
    if len(UOM_list) > 1:
        container_UOM = UOM_list[1].text
        
    #get the UOM
    wait = WebDriverWait(driver, 10)
    warehouse_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".warehouse .type")))
    
    small_unit_warehouse = warehouse_list[0].text
    container_warehouse = warehouse_list[0].text
    if len(UOM_list) > 1:
        container_warehouse = warehouse_list[1].text
    
    #get stock
    wait = WebDriverWait(driver, 10)
    stock_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".stock .stock-status")))
    
    stock = stock_list[0].text
    container_quanity = stock_list[0].text
    if len(stock_list) > 1:
        container_quanity = stock_list[1].text
        
    #get price
    wait = WebDriverWait(driver, 10)
    price_list = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".itemPrice .price")))
    
    unit_price = price_list[0].text
    container_price = price_list[0].text
    if len(price_list) > 1:
        container_price = price_list[1].text
    
    
    wait = WebDriverWait(driver, 10)
    try:
        image = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".detailImage")))
        img_url = image.get_attribute("src")
        img_name = item + '.jpg'
        img_path = os.path.join("images", img_name)
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            with open(img_path, "wb") as img_file:
                img_file.write(img_response.content)
            print(f"Image {img_name} saved.")
        else:
            print(f"Failed to download image {img_name}. Status code: {img_response.status_code}")
    except:
        img_name = "No image in this product"
        img_url = None

    bar_code = None
    product_web = None
    country_origin = None
    country_origin_statement = None
    net_content = None
    supplier_description = None

    item_info['Product Code'] = [item]
    item_info['Brand'] = [brand]
    item_info['Type'] = [product_type]
    item_info['Description'] = [description]
    item_info['Product Line'] = [product_line]
    item_info['Category'] = [category]
    item_info['Small Unit Warehouse'] = [small_unit_warehouse]
    item_info['Container Warehouse'] = [container_warehouse]
    item_info['Pack Size'] = [pack_size]
    item_info['Uom'] = [UOM]
    item_info['Ctn Qty'] = [Ctn_qty]
    item_info['Ctn Uom'] = [container_UOM]
    item_info['Unit Stock'] = [stock]
    item_info['Ctn Stock'] = [container_quanity]
    item_info['Unit Price'] = [unit_price]
    item_info['Ctn Price'] = [container_price]
    item_info['Tax%'] = [tax]
    item_info['Img Name'] = [img_name]
    item_info['Img URL'] = [img_url]
    item_info['Get data time'] = [get_data_time]

    if check_exists_by_css_celector(driver, ".additional-info"):
        additional_info, table_info = get_additional_information(driver)
        item_info.update(additional_info)

    # except Exception as e:
    #     error_ID = error_ID + [item]
    #     print("An error occurred:", e)

    
    for k, v in item_info.items():
        print(f'{k} : {v}')
    df = pd.DataFrame(data = item_info)
    # display(df)
    print("=========")
    all_df = pd.merge(all_df, df, how = "outer")

all_df.to_excel("all_data.xlsx", index = False)