import random
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

_browser = None
_DEBUG = True

def train(loginCredentials, appName, trainingPhrases, closeBrowserWhenDone=True):
    random.seed()
    browser = webdriver.Chrome(os.path.join(os.path.dirname(os.path.abspath(__file__)),'chromedriver.exe'))
    if not closeBrowserWhenDone:
        _browser  = browser
    browser.implicitly_wait(10)
    browser.get('https://wit.ai/')
    loginButton = browser.find_element_by_xpath("//div[contains(@class, 'btn-login') and not(contains(@class, 'btn-facebook'))]/*")
    loginButton.click()
    parentWindow = browser.current_window_handle
    browser.switch_to.window(browser.window_handles[-1])
    usernameField = browser.find_element_by_id('login_field')
    passwordField = browser.find_element_by_id('password')
    usernameField.clear()
    passwordField.clear()
    usernameField.send_keys(loginCredentials['username'])
    passwordField.send_keys(loginCredentials['password'])
    usernameField.submit()
    browser.switch_to.window(parentWindow)
    koraProjectLink = browser.find_element_by_link_text(appName) #If it crashes here because it can't find the element by the link text, increase the browser's implicit wait time towards the top
    koraProjectLink.click()
    textBoxContainer = browser.find_element_by_css_selector('.sample-widget-tagged.tagger-tagged')

    def highlightSubPhrase(fullText, startIndexInclusive, endIndexExclusive):
        assert startIndexInclusive <= endIndexExclusive and \
               len(fullText) >= endIndexExclusive - startIndexInclusive and \
               len(fullText) >= endIndexExclusive and \
               startIndexInclusive > 0

        moveLeftToEnd = len(fullText) - endIndexExclusive
        highlightLength = endIndexExclusive - startIndexInclusive
        ActionChains(browser).move_to_element(textBoxContainer).click(textBoxContainer).send_keys(Keys.ARROW_LEFT * moveLeftToEnd).key_down(Keys.SHIFT).send_keys(Keys.ARROW_LEFT*highlightLength).key_up(Keys.SHIFT).perform()

    browser.implicitly_wait(2) #don't make this smaller or it starts screwing things up
    validateButton = browser.find_element_by_xpath("//button[@class='sample-widget-validate-btn']")
    for phrase in trainingPhrases:
        phraseText = phrase.text
        if _DEBUG:
            print(phraseText)
        ActionChains(browser).move_to_element(textBoxContainer).click(textBoxContainer).click(textBoxContainer).click(textBoxContainer).send_keys(Keys.BACK_SPACE + phraseText).perform()
        autoDetectedClose = browser.find_elements_by_css_selector('.diag-remove')
        for btn in autoDetectedClose:
            try:
                ActionChains(browser).move_to_element(btn).click(btn).perform()
            except StaleElementReferenceException:
                pass
        for instruction in phrase.instructions():
            if _DEBUG:
                print('\tInstruction: '+str(instruction))
            highlighted = False
            if 'startHighlight' in instruction and 'endHighlight' in instruction:
                ActionChains(browser).move_to_element(textBoxContainer).click(textBoxContainer)
                highlightSubPhrase(phraseText, instruction['startHighlight'], instruction['endHighlight'])
                highlighted = True
            entityField = browser.find_element_by_xpath("//input[contains(@class, 'wisp-input-quick-add')]")
            entityField.click() #need to get focus off of textBoxContainer and initiate dropdown menu
            entityInDropDown = None
            try:
                entityInDropDown = browser.find_element_by_xpath("//div[@class='story-dropdown']//*[text()='" + str(instruction['entity']) + "']")
            except NoSuchElementException:
                pass
            if entityInDropDown:
                entityInDropDown.click()
            else:   #creates new entity (also for existing wit builtin entity like wit/number which won't be found in the dropdown despite it being there)
                entityField.send_keys(instruction['entity'] + Keys.RETURN*2)
            if not highlighted:
                entityValueField = browser.find_element_by_xpath("//span[text()='Value']")
                ActionChains(browser).move_to_element(entityValueField).click().send_keys(instruction['value'] + Keys.RETURN).perform()

        validateButton.click()
