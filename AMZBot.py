#!/usr/bin/env python3
"""
    *******************************************************************************************
    AMZBot: Amazon Product Ranking Bot
    Author: Ali Toori, Python Developer [Bot Builder]
    Founder: https://boteaz.com
    *******************************************************************************************
"""
import time
import os
import json
import ntplib
import random
import pyfiglet
import requests
import pandas as pd
from random import randint
import logging.config
from pathlib import Path
from time import sleep
import webbrowser
import pyautogui
import pyperclip
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from multiprocessing import freeze_support
pyautogui.FAILSAFE = False


class AMZBot:
    def __init__(self):
        self.comments_today = 0
        self.PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
        self.file_settings = str(self.PROJECT_ROOT / 'BotRes/Settings.json')
        self.file_products = str(self.PROJECT_ROOT / 'BotRes/Products.csv')
        self.file_proxies = str(self.PROJECT_ROOT / 'BotRes/proxies.txt')
        self.settings = self.get_settings()
        self.LOGGER = self.get_logger()
        self.amz_hone_url = "https://www.amazon.com/"
        self.proxies = self.get_proxies()
        self.user_agents = self.get_user_agents()

    # Loads LOGGER
    @staticmethod
    def get_logger():
        """
        Get logger file handler
        :return: LOGGER
        """
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',  # colored output
                    # --> %(log_color)s is very important, that's what colors the line
                    'format': '[%(asctime)s,%(lineno)s] %(log_color)s[%(message)s]',
                    'log_colors': {
                        'DEBUG': 'green',
                        'INFO': 'cyan',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red',
                    },
                },
                'simple': {
                    'format': '[%(asctime)s,%(lineno)s] [%(message)s]',
                },
            },
            "handlers": {
                "console": {
                    "class": "colorlog.StreamHandler",
                    "level": "INFO",
                    "formatter": "colored",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "filename": "AMZBot.log",
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 1
                },
            },
            "root": {"level": "INFO",
                     "handlers": ["console", "file"]
                     }
        })
        return logging.getLogger()

    # Enables CMD color
    @staticmethod
    def enable_cmd_colors():
        # Enables Windows New ANSI Support for Colored Printing on CMD
        from sys import platform
        if platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Prints ASCII Art Banner
    @staticmethod
    def banner():
        print('************************************************************************\n')
        pyfiglet.print_figlet('____________                   AMZBot ____________\n', colors='RED')
        print('Amazon Product Ranking Bot\n'
              'Author: Ali Toori, Bot Developer\n'
              'Founder: https://boteaz.com/\n'
              '************************************************************************')

    def get_settings(self):
        """
        Creates default or loads existing settings file.
        :return: settings
        """
        if os.path.isfile(self.file_settings):
            with open(self.file_settings, 'r') as f:
                settings = json.load(f)
            return settings
        settings = {"Settings": {
            "Email": "Enter Your Email ID"
        }}
        with open(self.file_settings, 'w') as f:
            json.dump(settings, f, indent=4)
        with open(self.file_settings, 'r') as f:
            settings = json.load(f)
        return settings

    # Loads proxies
    def get_proxies(self):
        file_proxies = str(self.PROJECT_ROOT / 'BotRes/proxies.txt')
        with open(file_proxies) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Loads user agents
    def get_user_agents(self):
        file_uagents = str(self.PROJECT_ROOT / 'BotRes/user_agents.txt')
        with open(file_uagents) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Loads product names
    def get_products(self):
        file_proxies = str(self.PROJECT_ROOT / 'BotRes/products.txt')
        with open(file_proxies) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Returns center of the screen
    @staticmethod
    def get_screen_center():
        height = pyautogui.size().width
        width = pyautogui.size().height
        center_x, center_y = int(height/2), int(width/2)
        return center_x, center_y

    # Gets element's X,Y coordinates on screen by image
    def get_element_by_image(self, element_name):
        self.LOGGER.info(f'Getting element: {element_name}')
        # Get element's image path
        image_path = str(self.PROJECT_ROOT / f'BotRes/images/{element_name}.png')

        # Return element's center coordinates on screen
        return pyautogui.locateCenterOnScreen(image_path)

    # Clicks an element by X,Y coordinates on screen
    def click_element(self, element_name):
        # Click element by coordinates
        try:
            coordinates = self.get_element_by_image(element_name=element_name)
            x, y = coordinates
            self.LOGGER.info(f'Clicking element: {element_name}, Coordinates: {coordinates}')
            # Move to the element by coordinates, wait for 0.5secs and then click on the element's center
            pyautogui.moveTo(x, y)
            sleep(0.5)
            pyautogui.click()
            self.LOGGER.info(f'Clicked element: {element_name}, Coordinates: {coordinates}')
            # Return True if element found
            return True
        except:
            # Return False if not found
            return False

    # Clear browser cache
    def block_cookies(self):
        self.LOGGER.info(f"Blocking third-party cookies")
        # Go to block cookies switch
        pyautogui.press(['tab', 'tab'])
        sleep(1)
        pyautogui.press('enter')
        sleep(1)
        self.LOGGER.info(f"Third-party cookies have been blocked")

    def clear_cache(self):
        self.LOGGER.info(f"Clearing cache")
        # Go to clear cache tab in chrome
        google_base_url = 'https://www.google.com'
        amz_base_url = 'www.amazon.com'
        webbrowser.open_new(google_base_url)
        sleep(1)
        pyautogui.hotkey('ctrl', 'l')
        pyautogui.write(f'chrome://settings/content/siteDetails?site=https%3A%2F%2F{amz_base_url}')
        # pyautogui.hotkey('ctrl', 'shift', 'delete')
        # pyautogui.hotkey('ctrl', 'n')
        pyautogui.press('enter')
        sleep(3)
        # # Press tab to focus on ClearData button
        # pyautogui.press('tab')
        # pyautogui.press('enter')
        # Click Clear Data button if found, otherwise the cache has already been cleared
        clear_button_clicked = self.click_element(element_name="ClearDataButton")
        # If ClearButton was found, proceed, otherwise skip
        if clear_button_clicked:
            sleep(0.5)
            # Switch to Clear button
            pyautogui.press(['tab', 'tab'])
            # Press enter to trigger the "Skip" button
            pyautogui.press('enter')
            sleep(3)
            # Close the current tab in chrome
            pyautogui.hotkey('ctrl', 'w')
            self.LOGGER.info(f"Cache has been cleared")
        else:
            # Close the current tab in chrome
            pyautogui.hotkey('ctrl', 'w')
            self.LOGGER.info(f"Cache not found !")

    def change_proxy(self):
        self.LOGGER.info(f"Changing proxy")
        element_name = "connect_icon"
        # Get a random number between range of proxies
        proxy_numbers = [i + 1 for i in range(len(self.proxies))]
        proxy_number = random.choice(proxy_numbers)
        # proxy_number = 1

        # Click Oxylabs extension icon
        sleep(3)
        try:
            # Try clicking icon when not connected
            self.click_element(element_name="oxylabs_icon")
        except:
            # Try clicking icon when connected
            self.click_element(element_name="oxylabs_icon_connected")
        sleep(3)

        # Click Connect button by Y coordinate of the number on left and X coordinate of the Connect button on right
        # Get the proxy number coordinates
        try:
            number_element_name = f"{element_name}_{proxy_number}"
            number_coords = self.get_element_by_image(element_name=number_element_name)
            x_number, y_number = number_coords

            # Get the proxy's Connect button coordinates
            connect_coords = self.get_element_by_image(element_name=element_name)
            x_connect, y_connect = connect_coords
            self.LOGGER.info(f'Clicking element: {number_element_name}, Coordinates: ({x_connect}, {y_number})')

            # Click Connect button in the extension to change proxy
            pyautogui.moveTo(x_connect, y_number)
            sleep(0.5)
            pyautogui.click()
            self.LOGGER.info(f'Clicked element: {number_element_name}')
            self.LOGGER.info(f"Proxy Changed")
            sleep(3)
        except:
            pass

    # Search product on Amazon
    def search_product(self, product):
        product_name = product["ProductName"]
        product_asin = product["ASIN"]
        is_sponsored = product["Sponsored"]
        self.LOGGER.info(f'Searching product: {product_name} | ASIN: {product["ProductName"]} | Sponsored: {product["Sponsored"]}')
        amz_base_url = 'https://www.amazon.com'
        google_base_url = 'https://www.google.com'

        # Random scrolls for product page
        scrolls = [3, 5, 9, 12]
        waits = [3, 5, 9, 12]

        # Open browser settings, clear cache
        self.clear_cache()

        # change proxy
        self.change_proxy()
        sleep(3)

        # Open Amazon in chrome
        self.LOGGER.info(f'Opening Amazon')
        webbrowser.open_new(amz_base_url)
        sleep(50)

        # Switch to and click the amazon search bar
        # Click Search Amazon, if found
        self.LOGGER.info(f'Clicking Search Amazon')
        if self.click_element(element_name="AMZSearchBar"):
            self.LOGGER.info(f'Search Amazon Clicked ')
            sleep(3)
        # Otherwise switch to the search bar using 7 tabs
        else:
            pyautogui.press(['tab', 'tab', 'tab', 'tab', 'tab', 'tab', 'tab'])

        # Enter the product name in the search bar
        self.LOGGER.info(f'Typing product: {product_name} in the search bar')
        pyautogui.typewrite(product_name)
        sleep(3)

        # Switch to search icon and click to perform the search
        self.LOGGER.info(f'Performing search')
        pyautogui.press(['tab'])
        sleep(0.5)
        pyautogui.press('enter')
        sleep(10)

        # Click Search Icon to perform the search
        # self.click_element(element_name="search_icon")
        # sleep(3)
        # pyautogui.press('enter')

        # Copy page source, view page source by pressing CTLR + U
        self.LOGGER.info(f'Copying page source')
        pyautogui.hotkey('ctrl', 'u')
        sleep(10)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        sleep(3)

        # Paste page source from clipboard
        page_source = pyperclip.paste()

        # Close the page source tab
        pyautogui.hotkey('ctrl', 'w')

        # create a soup object of the page source
        soup = BeautifulSoup(page_source, 'html.parser')
        organic_product = None
        sponsored_product = None
        # Find the div which includes title and the word "sponsored" if any
        self.LOGGER.info(f'Finding product URL')
        for product in soup.find_all("div", {"class": 'a-section a-spacing-none a-spacing-top-small s-title-instructions-style'}):

            self.LOGGER.info(f"Product ASIN Matched {product_asin}: {product_asin in str(product)}")
            # Filter products based on ASIN
            if product_asin in str(product):

                # Get sponsored products if is_sponsored
                self.LOGGER.info(f"Product Sponsored: {is_sponsored}")
                if is_sponsored:

                    # Check for sponsored products with keyword "Sponsored"
                    self.LOGGER.info(f"Sponsored Tag Matched: {'Sponsored' in product}")
                    if "Sponsored" in product.text:
                        # Get 3nd a tag to get link
                        product_url = f'{amz_base_url}{product.find_all("a")[2]["href"]}'
                        self.LOGGER.info(f"Sponsored Product URL: {product_url}")
                        sponsored_product = product_url
                        break
                # Get Organic products
                else:
                    # Skip sponsored products by keyword "Sponsored"
                    if "Sponsored" in product.text:
                        self.LOGGER.info(f"Skipping Sponsored Product URL")

                    # Get Organic products only
                    else:
                        # Get first link
                        product_url = f'{amz_base_url}{product.find_all("a")[0]["href"]}'
                        self.LOGGER.info(f"Organic Product URL: {product_url}")
                        organic_product = product_url

        if organic_product is not None:
            self.LOGGER.info(f"Searching Organic Product: {organic_product}")
            # Switch to the chrome search bar and enter the product URL
            pyautogui.hotkey('ctrl', 'l')
            sleep(3)
            pyautogui.write(organic_product)
            sleep(3)
            pyautogui.press('enter')
            sleep(20)
        elif sponsored_product is not None:
            self.LOGGER.info(f"Searching Sponsored Product: {sponsored_product}")
            # Switch to the chrome search bar and enter the product URL
            pyautogui.hotkey('ctrl', 'l')
            sleep(3)
            pyautogui.write(sponsored_product)
            sleep(3)
            pyautogui.press('enter')
            sleep(20)

        # Randomly scroll up and down for a couple of times
        for wait in waits:
            scroll = random.choice(scrolls)
            pyautogui.scroll(scroll)
            sleep(wait)

    # Process the products
    def process_products(self):
        products = pd.read_csv(self.file_products, index_col=None)
        # Process products from Products.csv
        for i, product in enumerate(products.iloc):
            self.LOGGER.info(f'Processing product No: {i} | Product Name: {product["ProductName"]} | ASIN: {product["ProductName"]} | Sponsored: {product["Sponsored"]}')
            self.search_product(product=product)

    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        # Print ASCII Art
        self.banner()
        self.process_products()


if __name__ == '__main__':
    AMZBot().main()
