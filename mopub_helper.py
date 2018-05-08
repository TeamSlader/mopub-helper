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

    def get_line_items_for_unit(self, unit_key):
        print('Grabbing line items from unit key ' + unit_key)

        self.browser.get('https://app.mopub.com/ad-unit?key=' + unit_key)
        time.sleep(5)

        line_ids = []
        elems = self.browser.find_elements_by_xpath('//a[@href]')
        for elem in elems:
            url = elem.get_attribute('href')
            if url.startswith('https://app.mopub.com/advertise/line_items/'):
                line_ids.append(url[43:])
        return line_ids

    def quit(self):
        self.browser.quit()
        exit()

class MopubLineHelper(MopubHelper):
    def create_line_item(self, order_key, custom_class_name, custom_data, custom_method, target_units, line_name, bid, keywords):
        print("Adding line order " + line_name)

        self.browser.get('https://app.mopub.com/advertise/orders/' + order_key + '/new_line_item/')
        self.wait_for_element('id_name')

        self.fill_line_item_custom_class(custom_class_name, custom_data, custom_method, target_units, line_name, bid, keywords)

        submit_button.click()
        self.wait_for_element('copy-line-item')

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

    def fill_line_item_custom_class(self, custom_class_name, custom_data, custom_method, target_units, line_name, bid, keywords):
        line_name_field = self.browser.find_element_by_id('id_name')
        ad_type = Select(self.browser.find_element_by_id('id_adgroup_type'))
        ad_priority = Select(self.browser.find_element_by_id('id_priority'))
        network_type = Select(self.browser.find_element_by_id('id_network_type'))
        custom_class_name_field = self.browser.find_element_by_id('id_custom_native-custom_event_class_name')
        custom_data_field = self.browser.find_element_by_id('id_custom_native-custom_event_class_data')
        custom_method_field = self.browser.find_element_by_id('id_custom_native-html_data')
        bid_field = self.browser.find_element_by_id('id_bid')
        keywords_field = self.browser.find_element_by_id('id_keywords')
        submit_button = self.browser.find_element_by_id('submit')

        self.fill_in(line_name_field, line_name)
        ad_type.select_by_visible_text('Network')
        ad_priority.select_by_visible_text('12')
        network_type.select_by_visible_text('Custom Native Network')
        self.fill_in(custom_class_name_field, custom_class_name)
        self.fill_in(custom_data_field, custom_data)
        self.fill_in(custom_method_field, custom_method)
        self.fill_in(bid_field, bid)
        self.fill_in(keywords_field, keywords)

        self.select_target_units(target_units)

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

    def fill_in(self, field, newValue):
        field.clear()
        field.send_keys(newValue)

class RubiconCSVParser(object):
    def __init__(self, filename, line_prefix):
        self.filename = filename
        self.line_prefix = line_prefix
        self.lines = []
        self.parse_csv()

    # TODO: figure out how to handle last line
    def parse_csv(self):
        with open(self.filename) as f:
            lines = f.readlines()
            csv_reader = csv.reader(lines[1:-1])  # skip the first and last line
            for row in csv_reader:
                self.append_line(row)

    def append_line(self, row):
        line_name = self.generate_line_name(self.line_prefix, float(row[2]), float(row[3]))
        line_bid = row[3]
        line_keyword = row[0]
        line = (line_name, line_bid, line_keyword)
        self.lines.append(line)

    def generate_line_name(self, prefix, min_bid, max_bid):
        return prefix + " $" + "{:0.2f}".format(min_bid) + " - $" + "{:0.2f}".format(max_bid)
