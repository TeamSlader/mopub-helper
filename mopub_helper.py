#!/usr/bin/env python

# Mopub Helper
# Author: Shuaib Jewon
# v0.2

import csv
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

class MopubHelper(object):
    def __init__(self, username, password):
        self.browser = webdriver.Firefox()
        self.login(username, password)

    def login(self, username, password):
        self.browser.get('https://app.mopub.com/account/login/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password').send_keys(password)
        self.browser.find_element_by_id('login-submit').click()
        self.wait_for_element('revenue-tab', 'Error: Unsuccessful MoPub login')

    def wait_for_element(self, element_id, error_message='Error: Page load timeout'):
        try:
            element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, element_id)))
        except TimeoutException:
            print(error_message)
            self.quit()

    def get_line_items_for_order(self, order_key):
        print('Grabbing line items from order key ' + order_key)

        self.browser.get('https://app.mopub.com/advertise/orders/' + order_key)
        time.sleep(5)

        line_ids = []
        elems = self.browser.find_elements_by_xpath('//a[@href]')
        for elem in elems:
            url = elem.get_attribute('href')
            if url.startswith('https://app.mopub.com/advertise/line_items/'):
                line_ids.append(url[43:-1])
        return line_ids

    def quit(self):
        self.browser.quit()
        exit()



