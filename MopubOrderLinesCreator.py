#!/usr/bin/env python

# Helper to generate new line orders for MoPub
# Author: Shuaib Jewon
# v0.1

import csv
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


class MopubOrderLinesCreator(object):
    def __init__(self, username, password, orderKey):
        self.browser = webdriver.Firefox()
        self.orderKey = orderKey
        self.login(username, password)

    def login(self, username, password):
        self.browser.get('https://app.mopub.com/account/login/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password').send_keys(password)
        self.browser.find_element_by_id('login-submit').click()
        self.waitForElement('revenue-tab', 'Error: Unsuccessful MoPub login')

    def createLineItem(self, customClassName, customData, customMethod, targetUnits, lineName, bid, keywords):
        print("Adding line order " + lineName)

        self.browser.get('https://app.mopub.com/advertise/orders/' + self.orderKey + '/new_line_item/')
        self.waitForElement('id_name')

        lineNameField = self.browser.find_element_by_id('id_name')
        adType = Select(self.browser.find_element_by_id('id_adgroup_type'))
        adPriority = Select(self.browser.find_element_by_id('id_priority'))
        networkType = Select(self.browser.find_element_by_id('id_network_type'))
        customClassNameField = self.browser.find_element_by_id('id_custom_native-custom_event_class_name')
        customDataField = self.browser.find_element_by_id('id_custom_native-custom_event_class_data')
        customMethodField = self.browser.find_element_by_id('id_custom_native-html_data')
        bidField = self.browser.find_element_by_id('id_bid')
        keywordsField = self.browser.find_element_by_id('id_keywords')
        submitButton = self.browser.find_element_by_id('submit')

        self.fillIn(lineNameField, lineName)
        adType.select_by_visible_text('Network')
        adPriority.select_by_visible_text('12')
        networkType.select_by_visible_text('Custom Native Network')
        self.fillIn(customClassNameField, customClassName)
        self.fillIn(customDataField, customData)
        self.fillIn(customMethodField, customMethod)
        self.fillIn(bidField, bid)
        self.fillIn(keywordsField, keywords)

        for targetUnit in targetUnits:
            unitCheckboxes = self.browser.find_elements_by_name('adunits')
            for unitCheckbox in unitCheckboxes:
                if unitCheckbox.get_attribute('value') == targetUnit:
                    unitCheckbox.click()

        submitButton.click()
        self.waitForElement('copy-line-item')

    def waitForElement(self, elementID, errorMessage='Error: Page load timeout'):
        try:
            element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, elementID)))
        except TimeoutException:
            print(errorMessage)
            self.quit()

    def fillIn(self, field, newValue):
        field.clear()
        field.send_keys(newValue)

    def quit(self):
        self.browser.quit()
        exit()


class RubiconCSVParser(object):

    def __init__(self, filename, linePrefix):
        self.filename = filename
        self.linePrefix = linePrefix
        self.lines = []
        self.parseCSV()

    # TODO: figure out how to handle last line
    def parseCSV(self):
        with open(self.filename) as f:
            lines = f.readlines()
            csvReader = csv.reader(lines[1:-1])  # skip the first and last line
            for row in csvReader:
                self.appendLine(row)

    def appendLine(self, row):
        lineName = self.generateLineName(self.linePrefix, float(row[2]), float(row[3]))
        lineBid = row[3]
        lineKeyword = row[0]
        line = (lineName, lineBid, lineKeyword)
        self.lines.append(line)

    def generateLineName(self, prefix, minBid, maxBid):
        return prefix + " $" + "{:0.2f}".format(minBid) + " - $" + "{:0.2f}".format(maxBid)

def run(mopubUsername, mopubPassword, mopubOrderKey, csvFilename, lineNamePrefix, targetUnits, customAdapterName, customData, customMethod = ''):
    helper = MopubOrderLinesCreator(mopubUsername, mopubPassword, mopubOrderKey)

    parser = RubiconCSVParser(csvFilename, lineNamePrefix)
    for line in parser.lines:
        helper.createLineItem(customAdapterName, customData, customMethod, targetUnits, line[0], line[1], line[2])

if __name__ == "__main__":
    start_time = time.time()
    run(
        'username',
        'password',
        'orderkey',
        'rubicon csv filename',
        'line name prefix',
        ['ad unit value'],
        'custom adapter name',
        'custom adapter data'
    )
    print("--- %s seconds ---" % (time.time() - start_time))
