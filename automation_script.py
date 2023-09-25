from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import selenium
import logging
import random
import time
import json
import csv
import os
import re
import pandas as pd

def launch_navigator(dict_credentials):
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option("useAutomationExtension", False)
    
    if dict_credentials['chrome_profile']['user_data_dir']!='':
        options.add_argument(r"user-data-dir={}".format(dict_credentials['chrome_profile']['user_data_dir']) )
    
    if dict_credentials['chrome_profile']['profile_directory'] != '':
        options.add_argument(r"profile-directory={}".format(dict_credentials['chrome_profile']['profile_directory']) )
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # driver_path = Service('/home/jorge/Work_may_2023/Mitsoku_project/Tool_TO_GET_PERSON_CONTACT/chrome_driver/chromedriver-linux64/chromedriver')
    driver = webdriver.Chrome(options=options)

def save_check_point(filename, dictionary):
    json_object = json.dumps(dictionary, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def load_check_point(filename):
    # Opening JSON file
    if os.path.isfile(filename):
        with open(filename, 'r') as openfile:        
            json_object = json.load(openfile)
    else:
        json_object = {}
    return json_object

def get_fields_dict(dict_credentials):
    csv_filepath = dict_credentials['csv_filepath']
    username = dict_credentials['username']
    password = dict_credentials['password']
    phone_column_name = dict_credentials['column_name']
    url = dict_credentials['current_url']
    template = dict_credentials['template']
    did =  dict_credentials['did']
    log = logging.basicConfig(level=logging.INFO)

    return csv_filepath, username, password, phone_column_name, url, template, did, log 

def start_new_chat():
    """Start new chat
    https://mjrealestate.3cx.us/webclient/#/chat/create"""
    menu = driver.find_element(By.ID, 'dropdown-alignment')
    drop_down_items = menu.find_elements(By.CLASS_NAME, 'dropdown-item')

    for dropdown in drop_down_items:
        if 'Start chat' in dropdown.text:
            send_sms_button = wait.until(EC.element_to_be_clickable(dropdown))            
            dropdown.click()

def get_contacts():
    list_chats = driver.find_elements(By.CLASS_NAME, 'grid-group-item.mhover.pointer.ng-star-inserted')
    return list_chats

def process_csv_to_webclient(dict_credentials, stop_event=None):
    
    # Initialize WebDriver
    launch_navigator(dict_credentials)

    # Open the dynamic URL
    # url = "https://1179.3cx.cloud/webclient/#/login?next=%2Foffice"
    if dict_credentials['current_url'] == 'https://mjrealestate.3cx.us/#/login':
        automatization_first_web_site(dict_credentials, stop_event)

    if dict_credentials['current_url'] == 'https://mjrealestate.3cx.us/webclient/#/people':
        automatization_second_web_site(dict_credentials, stop_event)

    # Close the driver:
    # driver.close()

def login_step(dict_credentials):
    wait = WebDriverWait(driver, 15)
    cond1 = dict_credentials['chrome_profile']['user_data_dir']== ''
    cond2 =  dict_credentials['chrome_profile']['profile_directory'] == ''
    if cond1 and cond2:
        
        extension_number_input = wait.until(EC.visibility_of_element_located((By.ID, "loginInput")))
        # extension_number_input = driver.find_element(By.ID, 'loginInput')
        extension_number_input.send_keys(dict_credentials['username'])

        password_input = driver.find_element(By.ID, 'passwordInput')
        password_input.send_keys(dict_credentials['password'])

        login_button = driver.find_element(By.ID, 'submitBtn')
        login_button.click()
        time.sleep(random.uniform(2,3.5))
    
    menuchat = wait.until(EC.visibility_of_element_located((By.ID, "menuChat")))
    time.sleep(random.uniform(1.2,1.5))

#####################################################################
#               MAIN FUNCTIONS                                      #
#####################################################################
def create_msg(row, template):

    first_name = row['Owner 1 First Name'].item()
    last_name = row['Owner 1 Last Name'].item()
    address = row['Address'].item()
    city = row['City'].item()
    state = row['State'].item()
    zip_code = row['Zip'].item()
    message = template.format(first_name=first_name,last_name=last_name,
        address=address,city=city,state=state,zip_code=zip_code)
    return message

def click_menu_contacts():
    # CLICK ON CONTACTS
    global wait
    contacts = wait.until(EC.element_to_be_clickable((By.ID, "menuContacts")))
    # contacts = driver.find_element(By.ID, 'menuContacts')
    contacts.click()
    
def click_new_contacts():
    # CLICK ON NEW CONTACT
    global wait
    new_contact = wait.until(EC.element_to_be_clickable((By.ID, "btnAdd")))
    # new_contact = driver.find_element(By.ID, 'btnAdd')
    new_contact.click()                
    time.sleep(random.uniform(0.5, 0.8))

def find_id(form_input):
    HTML = form_input.get_attribute('outerHTML')
    id_name = re.findall(r'id="(.+?)"', HTML)[0]
    return id_name

def fill_form_contact_info(row, phone_column_name):
    # FIND ALL THE ELEMENTS TO FILL TEXT
    global wait
    # form_inputs = wait.until(EC.visibility_of_element_located((By.ID, "form-input")))
    flag_wait = True
    while flag_wait:
        try:
            form_inputs = driver.find_elements(By.CLASS_NAME, 'form-input')    
            if len(form_inputs)!= 0:
                flag_wait = False    
        except:
            time.sleep(0.3)

    for form_input in form_inputs:        
        # SEARCH ELEMENT FIRST NAME
        if form_input.text== 'First Name':
            HTML = form_input.get_attribute('outerHTML')
            id_name = re.findall(r'id="(.+?)"', HTML)[0]        
            name_field = driver.find_element(By.ID, id_name)
            name_field.send_keys(row['Owner 1 First Name'].item())
        # SEARCH ELEMENT LAST NAME
        if form_input.text== 'Last Name':
            HTML = form_input.get_attribute('outerHTML')
            id_name = re.findall(r'id="(.+?)"', HTML)[0]        
            last_name_field = driver.find_element(By.ID, id_name)
            last_name_field.send_keys(row['Owner 1 Last Name'].item())
        
        # SEARCH ELEMENT MOBILE PHONE NUMBER
        if form_input.text== 'Mobile':
            id_phone = find_id(form_input)
            phone_number = driver.find_element(By.ID, id_phone)
            phone_number.send_keys('+1'+str(row[phone_column_name].item()))
            break     
    # CLICK ON BUTTON SAVE CONTACT
    button_save = driver.find_element(By.ID, 'btnSave')
    button_save.click()

def found_first_contact():
    
    flag_first_contact = True
    while flag_first_contact:
        try:
            first_contact = driver.find_element(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted').text
            
            if len(first_contact) != 0:
                flag_first_contact = False
                time.sleep(1.2)
        except:
            time.sleep(0.5)

    
    return first_contact

def click_on_msg_start():
    global wait
    contact_block = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "d-flex.mb-3.ng-star-inserted")))    
    # contact_block = driver.find_element(By.CLASS_NAME, 'd-flex.mb-3.ng-star-inserted')
    icon_send_msgs = contact_block.find_element(By.CLASS_NAME, 'sms-anchor.mhover.ng-star-inserted')
    icon_send_msgs.click()    

def wait_until_change(first_contact, phone):
    global wait
    # new_contact = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "grid-group-item.mhover.ng-star-inserted")))
    # new_contact = new_contact.text#driver.find_element(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted').text
    new_contact = '*-*'#driver.find_element(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted')
    while (first_contact == new_contact and phone not in first_contact) or new_contact =='':
        try:
            new_contact = driver.find_element(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted').text
        except:
            time.sleep(0.3)

def send_message(template_msg, send_message = False):
    global wait
    # send_button = wait.until(EC.visibility_of_element_located((By.ID, "sendMessageBtn")))
    message_input = driver.find_element(By.CLASS_NAME, 'message-input')
    message_input.clear()
    message_input.send_keys(template_msg)
    
    if send_message:
        send_button = driver.find_element(By.ID, 'sendMessageBtn')
        send_button.click()

def delete_chats():
    print("Deleting Chats: ")
    menuchats = driver.find_element(By.ID, 'menuChat')
    menuchats.click()
    flag_continue = True
    while flag_continue:
        try:
            contactoptions = driver.find_elements(By.CLASS_NAME, 'context-btn.btn.btn-plain-sm.ng-star-inserted')
            flag_continue = False
        except:
            time.sleep(0.05)
    
    count = 0
    while len(contactoptions)!=0:
        print("-", end= '')
        initial_len = len(contactoptions)        
        contactoptions[0].click()

        # Click on archive button
        dropdownoptions = driver.find_elements(By.CLASS_NAME, 'dropdown-item.ng-star-inserted')        
    #     [option.click() for option in dropdownoptions if 'Archive' in option.text or 'Delete' in option.text]    
        for option in dropdownoptions:
            if 'Delete' in option.text or 'Archive' in option.text:                
                option.click()
                time.sleep(0.2)                
                break

        new_len = initial_len
        while initial_len == new_len:
            try:
                contactoptions = driver.find_elements(By.CLASS_NAME, 'context-btn.btn.btn-plain-sm.ng-star-inserted')
                new_len = len(contactoptions)                
            except:
                time.sleep(0.05)
    print("No Chats")

def delete_contacts():
    print("Deleting Contacts: ")
    menucontacts = driver.find_element(By.ID, 'menuContacts')
    menucontacts.click()
    time.sleep(0.3)
    flag_continue = True
    while flag_continue:
        try:
            phone_contacts = driver.find_elements(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted')
            flag_continue = False
        except:
            time.sleep(0.05)

    # phone_contacts = driver.find_elements(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted')
    count = 0    
    # for phone_contact in phone_contacts:
    while len(phone_contacts)!=0:
        # time.sleep(0.5)
        print("-", end='')
        show_more = phone_contacts[0].find_element(By.ID, 'showMoreBtnTile')
        show_more.click()
        time.sleep(0.25)

        drop_down = driver.find_element(By.CLASS_NAME, 'dropdown-menu.ng-star-inserted')
        options = drop_down.find_elements(By.CLASS_NAME, 'ng-star-inserted')
        time.sleep(0.25)

        for option in options:
            if 'Delete' in option.text:
                option.click()
                time.sleep(0.25)
                flag_wait_confirmation = True
                while flag_wait_confirmation:
                    print("-", end=' ')
                    try:
                        button_ok = driver.find_element(By.CLASS_NAME, 'btn.btn-primary.ng-star-inserted')
                        if button_ok.text !='':                            
                            button_ok.click()                            
                            flag_wait_confirmation = False
                    except:
                        time.sleep(0.25)
                break
        wait_flag = True
        count = 0
        while wait_flag:
            try:
                errormsg = driver.find_element(By.CLASS_NAME, 'modal-body')
                if "Contact is not found" in errormsg.text:
                    button_ok = driver.find_element(By.CLASS_NAME, 'btn.btn-primary.ng-star-inserted')
                    button_ok.click()
                    wait_flag = False
            except:
                print('-*-',end='')
                time.sleep(0.35)
                count +=1
                if count == 3:
                    wait_flag = False
                
        wait_flag = True
        while wait_flag:
            print("-",end='')
            try:                 
                phone_contacts = driver.find_elements(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted')                
                wait_flag = False
            except:
                time.sleep(0.1)

def wait_for_next(start_time, time_wait = 12):
    execution_time = 0
    while execution_time < time_wait:
        end_time = time.time()
        execution_time = end_time - start_time    
        time.sleep(0.1)
    print("Time is up, pass to next message ",execution_time)

def automatization_second_web_site(dict_credentials, stop_event):
    global wait

    if not os.path.exists('check_points'):    
        os.mkdir('check_points')
    dict_issues = {}
    wait = WebDriverWait(driver, 15)
    
    csv_filepath, username, password, phone_column_name, url, template, did, log = get_fields_dict(dict_credentials)

    driver.get(url)
    time.sleep(5)
    # AUTENTICATION SECTION    
    login_step(dict_credentials)    

    # CLICK ON CHAT SECTION 
    menuchat = driver.find_element(By.ID, 'menuChat')
    menuchat.click()
    
    # flag_debug = False
    # count = 0
    file_name = csv_filepath.split('/')[-1]
    if not os.path.isfile('check_points/last_row.json'):
        last_row_dict = {}
        row_number = 0
        # save_check_point('check_points/last_row.json', last_row_dict)
    else:
        last_row_dict = load_check_point('check_points/last_row.json')
        try:
            last_row = last_row_dict[file_name]['last_row']
            row_number = last_row + 1
        except:
            # last_row = 0
            row_number = 0
    

    df = pd.read_csv(csv_filepath)
    count_delete = 0
    count_issue = 0
    print("stop_event ", stop_event)
    while row_number <= len(df): #and not stop_event:
        start_time = time.time() # take current time
        print("Start main loop ")
        row = df.iloc[[row_number]]

        if stop_event and stop_event.is_set():                
            break        
        agent_phone = row[phone_column_name].item()
        message = create_msg(row, template) # create a messge unin a row data.
        # IF agent_phone IS NOT EMPTY PROCEED WITH SEARCH CONTACT NUMBER
        try:
            print("agent_phone: ", agent_phone)            
            if agent_phone:
                agent_phone_with_prefix = '+1' + str(agent_phone)
                print("Current Phone: ", agent_phone_with_prefix, end='-')
                # CLICK ON MORE CONTACTS
                click_menu_contacts()
                steep = 'click_contact'
                click_new_contacts()
                steep = 'click new contact'
                fill_form_contact_info(row, phone_column_name)
                time.sleep(0.3)
                steep = 'click fill form'
                # debug("finish contact creation")

                # MAKE SEARCH OF CONTACT CREATED
                first_contact = found_first_contact() # load current first contact previusly to make search found the first contact
                steep = 'find first contact'

                search_box = wait.until(EC.visibility_of_element_located((By.ID, "inputSearch")))
                # search_box = driver.find_element(By.ID, 'inputSearch')
                search_box.clear()
                steep = 'clear search box'
                search_box.send_keys(agent_phone_with_prefix)
                wait_until_change(first_contact, phone = agent_phone_with_prefix) # wait until the first block of contact change
                steep = 'contact found'
                # debug("search contac finish ")
                time.sleep(2)

                # FIND BLOCK OF CONTACT
                phone_contacts = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "grid-group-item.mhover.ng-star-inserted")))
                # phone_contacts = driver.find_element(By.CLASS_NAME, 'grid-group-item.mhover.ng-star-inserted')
                phone_contacts.click()                
                steep = 'click on contact'
                # debug("search contac finish ")

                time.sleep(random.uniform(0.8,1.5))
                # CLICK ON START MESSAGE
                click_on_msg_start()
                steep = 'click on new message'
                time.sleep(1.2)
                # debug("finish click on start message")
                send_message(message, send_message = False)
                time.sleep(1.5)
                steep = 'msg sent'
                
                # SAVE CHECK POINT TAKING THE FILE NAME LIKE MAIN KEY
                last_row_dict[file_name] = {'last_row': row_number}
                save_check_point('check_points/last_row.json', last_row_dict)
                row_number +=1
                count_issue = 0
                count_delete +=1
                print('count_delete ', count_delete)
                if count_delete ==5:
                    # CLEAN MESSAGES AND DELETE CONTACTS.
                    print("Excution delete messages and contacts: ")
                    delete_chats()
                    delete_contacts()
                    count_delete = 0
                print("-", end='')
                wait_for_next(start_time, time_wait = 12)
        except:
            print("Count Issue: ", count_issue)
            if count_issue == 3:
                row_number += 1
            print("Issue steep: ", steep, 'from the row: ', row_number)
            
            dict_issues[row_number] = {'phone':agent_phone_with_prefix, 'steep':steep}
            save_check_point('check_points/issues_row.json', dict_issues)
            
            # user_input = input("Please type s to stop: ")
            # if user_input =='s':
            #     print(stop)
            try:
                ignoreanswer = driver.find_element(By.CLASS_NAME, 'btn.border-0.shadow-none.btn-transparent-dark.ng-tns-c290-4.ng-star-inserted')
                ignoreanswer.click()
                print("Issues caused by input message interfering")
            except:
                print("Other issue")
    if stop_event:
        print("Process stoped")
    # delete_chats()
    # delete_contacts()
    print("File Processed")


def debug(msg):
    user_input = input(msg + ' type s to stop')
    if user_input == 's':
        print(stop)

def automatization_first_web_site(dict_credentials, stop_event):    
    csv_filepath, username, password, phone_column_name, url, template, did, log = get_fields_dict(dict_credentials)
    # Initialize WebDriver    
    driver.get(url)

    # Wait for the username field to become visible
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.visibility_of_element_located((By.ID, "loginInput")))

    # Enter username
    # username_field.send_keys("13310")
    username_field.send_keys(username)

    # Wait for the password field to become visible
    password_field = wait.until(EC.visibility_of_element_located((By.ID, "passwordInput")))

    # Enter password
    # password_field.send_keys("75SVQO95zCfT7zp0")
    password_field.send_keys(password)

    # Locate the submit button by ID and click it
    submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submitBtn")))
    submit_button.click()

    # Wait for the chat icon to become visible and click it
    chat_link = wait.until(EC.element_to_be_clickable((By.ID, "menuChat")))
    chat_link.click()

    # Wait for the page to load    
    
    with open(csv_filepath, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            #print(row.keys())
            if stop_event and stop_event.is_set():
                break

            agent_phone = row[phone_column_name]
            if agent_phone:
                agent_phone_with_prefix = '+1' + agent_phone
                # this clicks on the plus sign to open the text options 
                new_chat_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-id='btnNewChat']")))
                
                new_chat_button.click()

                # this click on the SMS button to open the text field 
                send_sms_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-id='btnStartSmsChat']")))
                
                send_sms_button.click()
                
                #place number in text
                input_field = driver.find_element(By.ID, "inputChatCompose")
                
                input_field.send_keys(agent_phone_with_prefix)
                
                input_field.send_keys(Keys.RETURN)
                  # Wait before sending the message
                print(f"going to jump in xpath //app-provider-item")
            
           
                #provider_item = driver.find_element(By.XPATH, "//app-provider-item")
                provider_item = driver.find_element(By.XPATH, f"//small[contains(text(),'{did}')]")
                provider_item.click()
                
                print(f"right after the click")                

                # Click on the phone number element
                print(f"right before the CSS_SELECTOR showParticipants")
                phone_number_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#showParticipants")))
                print(f"right after the CSS_SELECTOR showParticipants")
                
                print(f"after 4 seconds  CSS_SELECTOR showParticipants")
                phone_number_element.click()
                print(f"click completed for CSS_SELECTOR showParticipants")
                           
                # # Wait for the "Add" button to become clickable
                print(f"jumping in chatInfoAddBtn")
                add_button = wait.until(EC.element_to_be_clickable((By.ID, "chatInfoAddBtn")))
                
                # Click on the "Add" button
                add_button.click()

                # Find the name and address from the CSV row
                first_name = row['Owner 1 First Name']
                last_name = row['Owner 1 Last Name']
                address = row.get('Address')
                city = row['City']
                state = row['State']
                zip_code = row['Zip']

                # Find the input group for First Name
                first_name_input_group = driver.find_element(By.CLASS_NAME, "input-group")

                # Find the input field for First Name within the input group
                first_name_input = first_name_input_group.find_element(By.CSS_SELECTOR, "input[data-qa='input']")

                # Fill in the input field with the first name
                first_name_input.send_keys(first_name)

                # Find the input field for Last Name
                last_name_input_group = driver.find_element(By.CLASS_NAME, "input-group")

                # Find the input field for Last Name within the input group
                last_name_input = last_name_input_group.find_element(By.CSS_SELECTOR, "input[data-qa='input']")

                last_name_input.send_keys(last_name)

                # Click on the "OK" button
                ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qa='modal-ok']")))
                ok_button.click()

                #Dynamic message 
                message = template.format(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code
                )

                # Find the message input field and fill in the message
                message_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "message-input")))
                message_input.send_keys(message)

                # Click on the send button
                send_button = driver.find_element(By.ID, "sendMessageBtn")
                send_button.click()

                # Wait for a moment before proceeding to the next row
                time.sleep(2)