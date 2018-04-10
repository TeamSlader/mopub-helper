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
        print('Logging in MoPub (' + username + ":******)")

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

class MopubLineHelper(MopubHelper):
    def update_line_items(self, line_ids,target_units, deselect_units):
        count = 1
        for line_id in line_ids:
            print(str(count) + '. Updating line item with id ' + line_id)
            self.update_line_item(line_id, target_units, deselect_units)
            count = count + 1

    def update_line_item(self, line_id, target_units, deselect_units):
        url = 'https://app.mopub.com/advertise/line_items/' + line_id + '/edit/'
        
        self.browser.get(url)
        self.wait_for_element('submit', 'Error logging in')

        if deselect_units:
            self.deselect_target_units(target_units)
        else:
            self.select_target_units(target_units)

        self.browser.find_element_by_id('submit').click()
        self.wait_for_element('copy-line-item')

    def select_target_units(self, target_units):
        unit_checkboxes = self.browser.find_elements_by_name('adunits')

        for target_unit in target_units:
            unit_checkboxes = self.browser.find_elements_by_name('adunits')
            for unit_checkbox in unit_checkboxes:
                if unit_checkbox.get_attribute('value') == target_unit and not unit_checkbox.is_selected():
                    unit_checkbox.click()

    def deselect_target_units(self, target_units):
        unit_checkboxes = self.browser.find_elements_by_name('adunits')

        for target_unit in target_units:
            unit_checkboxes = self.browser.find_elements_by_name('adunits')
            for unit_checkbox in unit_checkboxes:
                if unit_checkbox.get_attribute('value') == target_unit and unit_checkbox.is_selected():
                    unit_checkbox.click()


