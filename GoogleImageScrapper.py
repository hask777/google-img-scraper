# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:01:02 2020

@author: OHyic
"""
#import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#import helper libraries
import time
import urllib.request
import shutil
import os
import requests
import struct
import imghdr
from PIL import Image

class GoogleImageScraper():
    def __init__(self,webdriver_path,image_path, search_key="cat",number_of_images=1,headless=False,min_resolution=(0,0),max_resolution=(1920,1080)):
        #check parameter types
        if (type(number_of_images)!=int):
            print("GoogleImageScraper Error: Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("GoogleImageScraper Notification: Image path not found. Creating a new folder.")
            os.makedirs(image_path)
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"%(search_key)
        self.headless=headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.saved_extension = "png"
        self.valid_extensions = ["jpg","png","jpeg"]
        
    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls = google_image_scraper.find_image_urls()
                
        """
        print("GoogleImageScraper Notification: Scraping for image link... Please wait.")
        image_urls=[]
        count = 0
        options = Options()
        if(self.headless):
            options.add_argument('--headless')
        try:
            driver = webdriver.Chrome(self.webdriver_path, chrome_options=options)
            driver.get(self.url)
            time.sleep(5)
        except:
            print("[-] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")

        for indx in range (1,self.number_of_images+1):
            try:
                #find and click image
                imgurl = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img'%(str(indx)))
                imgurl.click()
                
                #select image from the popup
                time.sleep(1)
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "n3VNCb")))
                images = driver.find_elements_by_class_name("n3VNCb")
                
                for image in images:
                    #only download images that starts with http
                    if(image.get_attribute("src")[:4].lower() in ["http"]):
                        print("%d. %s"%(count,image.get_attribute("src")))
                        image_urls.append(image.get_attribute("src"))
                        count +=1
                        break
                #scroll page to load next image
                driver.execute_script("window.scrollTo(0, "+str(indx*150)+");")
                time.sleep(1)
            except Exception as e:
                print("GoogleImageScraper Skip: Unable to get the link for this photo",e)
        driver.close()
        return image_urls
    
    def save_images(self,image_urls):
        #save images into file directory
        """
            This function takes in an array of image urls and save it into the prescribed image path/directory.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls=["https://example_1.jpg","https://example_2.jpg"]
                google_image_scraper.save_images(image_urls)
                
        """
        print("GoogleImageScraper Notification: Saving Image... Please wait.")
        for indx,image_url in enumerate(image_urls):
            try:
                filename = "%s%s.%s"%(self.search_key,str(indx),self.saved_extension)
                image_path = os.path.join(self.image_path, filename)
                print("%d .Image saved at: %s"%(indx,image_path))
                image = requests.get(image_url)
                if image.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(image.content)
                    image_from_web = Image.open(image_path)
                    image_resolution = image_from_web.size
                    if image_resolution != None:
                        if image_resolution[0]<self.min_resolution[0] or image_resolution[1]<self.min_resolution[1] or image_resolution[0]>self.max_resolution[0] or image_resolution[1]>self.max_resolution[1]:
                            #print("GoogleImageScraper Notification: %s did not meet resolution requirements."%(image_url))
                            os.remove(image_path)
            except Exception as e:
                #print("GoogleImageScraper Error: Failed to be downloaded.")
                pass
        print("GoogleImageScraper Notification: Download Completed.")
        
