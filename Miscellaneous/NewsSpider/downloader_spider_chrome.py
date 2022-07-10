#nv # -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 16:58:31 2020

@author: xwang222
"""
from __future__ import absolute_import
import time
from NewsSpider.items import NewsspiderItem
import scrapy
import keyboard
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import re
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import random
import pyautogui
import io
import sys
#sys.stdout = io.TextIOWrapper(sys.stdout, encoding="utf-8")
Exception_list=[]
# import URL list
#with open("H:\\white paper\\url.txt", "r") as fd:
URL_list = ["https://libraryguides.binghamton.edu/az.php?a=a"]
NewsList = pd.read_csv(r"F:\research projects\Social Network\Data\Newslist_v3.csv")
Newspaper_list = NewsList['Name'].values.tolist()
L1=len(Newspaper_list) 
link1= "https://libraryguides.binghamton.edu/az.php?a=a"
#column_names = CountyList
#Newspaper_list= ["Associated Press: Ithaca Metro Area (NY)","Times Union, The (Albany, NY)"] #"Times Union, The (Albany, NY)",

class DLSpider(scrapy.Spider):
    name = "download_newstext"
    allowed_domains = "https://infoweb-newsbank-com.proxy.binghamton.edu/"

    def start_requests(self):
        for x in URL_list:
        #x="https://infoweb-newsbank-com.proxy.binghamton.edu/apps/news/browse-pub?p=AWNB&t=pubname%3AATUB%21Times%2BUnion%252C%2BThe%2B%2528Albany%252C%2BNY%2529&action=browse&f=advanced"
            yield scrapy.Request(url=x, callback=self.parse)

    def __init__(self):
        global driver
        caps = webdriver.DesiredCapabilities.CHROME.copy()
        caps['acceptInsecureCerts'] = True
        self.driver = webdriver.Chrome(executable_path=r'F:\research projects\Social Network\Scraping Program\spiders\chromedriver.exe',desired_capabilities=caps)

        #self.driver.implicitly_wait(20)
        time.sleep(3)
        #self.reset()
    
    def reset(self):
        self.driver.quit()
        global driver
        caps = webdriver.DesiredCapabilities.CHROME.copy()
        caps['acceptInsecureCerts'] = True
        self.driver = webdriver.Chrome(executable_path=r'F:\research projects\Social Network\Scraping Program\spiders\chromedriver.exe',desired_capabilities=caps)

        #self.driver.implicitly_wait(20)
        time.sleep(3)


    def parse(self, response):
        self.driver.get(response.url)
        self.driver.implicitly_wait(3)
        time.sleep(5)
        DL = self.driver.find_element_by_xpath("//a[@href='https://login.proxy.binghamton.edu/login?url=http://infoweb.newsbank.com/?db=AWNB']")
        DL.click()
        time.sleep(10)
        window_after = self.driver.window_handles[-1]
        self.driver.switch_to_window(window_after)
        e = self.driver.find_element_by_xpath("//*[@id='username']")
        e.send_keys("xxx")
        time.sleep(1)
        e = self.driver.find_element_by_xpath("//*[@id='password']")
        e.send_keys("xxx")
        time.sleep(1)
        e = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div[3]/div/form/section[5]/input[4]")
        time.sleep(10)
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[1]/div[2]/div[1]/ul/li/a")
        e.click()
        time.sleep(10)
        #while j <= L1:
        c=1         # bug stop point
        c1=1        # article index
        c2=0         # bug newspaper index
        for j in range(c2,L1+1):
            #try:
            
            x=Newspaper_list[j]
            e = self.driver.find_element_by_xpath("//*[@id='nbcore-react-browse-table-pane-source-list-page-filter']")
            e.send_keys(x)
            w1=random.randrange(10, 15, 1)
            time.sleep(w1)
            e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/main/div/div/div/div/div/table/tbody/tr/td[1]/span[2]/a")
            e.click()
            w1=random.randrange(10, 15, 1)
            time.sleep(w1)
            e = self.driver.find_element_by_xpath("//*[@id='edit-val-base-0']")
            e.send_keys("unemployment local employment")
            e = self.driver.find_element_by_xpath("//*[@id='edit-gnus-simple-search']/div[2]/button")
            e.click()
            #link1= self.driver.current_url
            w1=random.randrange(10, 15, 1)
            time.sleep(w1)
            try:
                e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[4]/main/div[2]/div/h2")
                item = NewsspiderItem()
                item['source']= x
                item['title']="No results found"
                e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/div[1]/div/div/div[2]/div[2]/ul/li/a")
                e.click()
                w2=random.randrange(1, 5, 1)
                time.sleep(w2)
                
                yield item
                
            except:                  
                e = self.driver.find_element_by_xpath("//*[@id='edit-date-from--2']")
                e.send_keys("2010")
                w2=random.randrange(1, 5, 1)
                time.sleep(w2)
                pyautogui.scroll(-10, x=100, y=100)
                time.sleep(w2)
                e = self.driver.find_element_by_xpath("//*[@id='edit-date-to--2']")
                e.send_keys("2017")
                w2=random.randrange(1, 5, 1)
                time.sleep(w2)
                pyautogui.scroll(-100, x=150, y=100)
                #time.sleep(w2)
                e = self.driver.find_element_by_xpath("//*[@id='search_nav-submit']")
                e.click()
                w2=random.randrange(1, 5, 1)
                time.sleep(w2)
                pyautogui.scroll(-10, x=100, y=100)
                #time.sleep(w2)
                e = self.driver.find_element_by_xpath("//*[@id='navigator-search-sort']/div/div/ul/li[3]/a")
                e.click()
                time.sleep(10)
                pyautogui.scroll(-100, x=150, y=100)
                #time.sleep(w2)
                e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[3]/div[1]/div")
                N = e.text
                L = int(re.search(r'\d+', N).group(0))
                pyautogui.scroll(-10, x=100, y=100)
                #time.sleep(w2)
                TC1 = (c1-1) // 20 
                    #TC2 = c1 % 20
                if TC1 != 0:
                    for k in range(1,TC1+1):
                        e = self.driver.find_element_by_xpath("//a[text()='Next']")
                        e.click()
                        time.sleep(5)
                else:
                    pass
                    
                xpath = "//*[@id='search-hits__hit--"
                xpath += str(c1)
                xpath += "']/div[2]/div/div[2]/div[1]/a/div/div[1]"
                e = self.driver.find_element_by_xpath(xpath)
                e.click()                            
                #e = self.driver.find_element_by_xpath("//*[@id='search-hits__hit--1']/div[2]/div/div[2]/div[1]")
                #e.click()
                w2=random.randrange(1, 5, 1)
                time.sleep(w2)
                item = NewsspiderItem()
                link = ""
                #while i <= L:
                for i in range(c1,L+1):
                # if it has already downloaded 50 items
                    if c>50:
                        c=1
                        #log out
                        self.reset()
                        w0=random.randrange(200, 240, 1)
                        time.sleep(w0)
                        #log back in
                        self.driver.get(link1)
                        self.driver.implicitly_wait(3)
                        time.sleep(5)
                        DL = self.driver.find_element_by_xpath("//a[@href='https://login.proxy.binghamton.edu/login?url=http://infoweb.newsbank.com/?db=AWNB']")
                        DL.click()
                        time.sleep(10)
                        window_after = self.driver.window_handles[-1]
                        self.driver.switch_to_window(window_after)
                        e = self.driver.find_element_by_xpath("//*[@id='username']")
                        e.send_keys("xwang222")
                        time.sleep(1)
                        e = self.driver.find_element_by_xpath("//*[@id='password']")
                        e.send_keys("Z6A9s6y5")
                        time.sleep(1)
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div[3]/div/form/section[5]/input[4]")
                        e.click()
                        time.sleep(10)
                        self.driver.refresh()
                        time.sleep(5)
                        pyautogui.moveTo(400, 350)
                        pyautogui.click(button='left')
                        #e = self.driver.find_element_by_xpath("//a[text()='A-Z Source List']")
                        #e.click()
                        time.sleep(25)                   
                        e = self.driver.find_element_by_xpath("//*[@id='nbcore-react-browse-table-pane-source-list-page-filter']")
                        e.send_keys(x)
                        w1=random.randrange(2, 4, 1)
                        time.sleep(w1)
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/main/div/div/div/div/div/table/tbody/tr/td[1]/span[2]")
                        e.click()
                        w1=random.randrange(10, 15, 1)
                        time.sleep(w1)
                        e = self.driver.find_element_by_xpath("//*[@id='edit-val-base-0']")
                        e.send_keys("unemployment local employment")
                        e = self.driver.find_element_by_xpath("//*[@id='edit-gnus-simple-search']/div[2]/button")
                        e.click()
                        
                        w1=random.randrange(7, 12, 1)
                        time.sleep(w1)
                        pyautogui.scroll(-100, x=150, y=100)
                        #time.sleep(w1)
                        e = self.driver.find_element_by_xpath("//*[@id='edit-date-from--2']")
                        e.send_keys("2010")
                        w2=random.randrange(1, 4, 1)
                        pyautogui.scroll(-100, x=100, y=100)
                        time.sleep(w2)
                        e = self.driver.find_element_by_xpath("//*[@id='edit-date-to--2']")
                        e.send_keys("2017")
                        pyautogui.scroll(-10, x=150, y=100)
                        w2=random.randrange(1, 4, 1)
                        #time.sleep(w2)
                        pyautogui.scroll(-100, x=100, y=100)
                        e = self.driver.find_element_by_xpath("//*[@id='search_nav-submit']")
                        e.click()
                        w2=random.randrange(1, 4, 1)
                        time.sleep(w2)
                        pyautogui.scroll(-100, x=150, y=100)
                        e = self.driver.find_element_by_xpath("//*[@id='navigator-search-sort']/div/div/ul/li[3]/a")
                        e.click()
                        time.sleep(6)
                        TC1 = (c1-1) // 20 
                        #TC2 = c1 % 20
                        if TC1 != 0:
                            for k in range(1,TC1+1):
                                e = self.driver.find_element_by_xpath("//a[text()='Next']")
                                e.click()
                                time.sleep(4)
                        else:
                            pass
                        
                        xpath = "//*[@id='search-hits__hit--"
                        xpath += str(c1)
                        xpath += "']/div[2]/div/div[2]/div[1]/a/div/div[1]"
                        e = self.driver.find_element_by_xpath(xpath)
                        e.click()
                        
                        '''
                        i = c1
                        
                        if c1 < L:
                            # to next page
                            time.sleep(5)
                            e = self.driver.find_element_by_xpath("//*[@id='nbcore-doc-nav__item__next']")
                            e.click()
                        
                        
                        if c1 == L:
                        # to source page
                            e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/header/div/div[2]/div[2]/ul/li/a")
                            e.click()
                        '''
                    else:
                        pass
                    
                           
                    w1=random.randrange(5, 10, 1)
                    time.sleep(w1)
                    # source
                    item['source']= x
                    # number
                    item['Art_num']= i
                    # keywords
                    item['Key']= "unemployment local employment"
                    #Periods
                    item['Period']= "2010-2017"
                    # title
                    try:
                        #pyautogui.scroll(-100, x=150, y=100)
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[2]/main/div[2]/div/div[1]/h1")
                        item['title']=e.text
                        w2=random.randrange(1, 3, 1)
                        time.sleep(w2)
                    except:
                        item['title']="exception"
                    # date
                    try:
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[2]/main/div[2]/div/div[1]/div[1]/div[1]/span[2]")
                        item['date']=e.text
                        #w2=random.randrange(1, 3, 1)
                        #time.sleep(w2)
                    except:
                        item['date']="exception"
                    
                    # loc
                    try:
                        #pyautogui.scroll(-100, x=100, y=100)
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[2]/main/div[2]/div/div[1]/div[1]/div[2]/span[1]")
                        item['loc']=e.text
                        w2=random.randrange(1, 3, 1)
                        time.sleep(w2)
                    except:
                        item['loc']="exception"
                    
                    # sec
                    try:
                        #pyautogui.scroll(-100, x=150, y=100)
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[2]/main/div[2]/div/div[1]/div[1]/div[2]/span[3]")
                        item['sec']=e.text
                        #w2=random.randrange(1, 3, 1)
                        #time.sleep(w2)
                    except:
                        item['sec']="exception"
                        
                    # words
                    try:
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[2]/main/div[2]/div/div[1]/div[1]/div[3]/span")
                        item['words']=e.text
                        w2=random.randrange(1, 3, 1)
                        time.sleep(w2)
                    except:
                        item['words']="exception"
                    # body
                    try:
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[2]/main/div[2]/div/div[1]/div[3]/p")
                        item['body']=e.text
                        #w2=random.randrange(1, 3, 1)
                        #time.sleep(w2)
                    except:
                        item['body']="exception"
                        
                    link= self.driver.current_url
                    item['Link']=link
                    
                    if i < L:                    
                    # to next page
                        try:    
                            pyautogui.moveTo(200, 800)
                            pyautogui.moveTo(425, 400)
                            e = self.driver.find_element_by_xpath("//a[text()='Next']")
                            e.click()  
                            w2=random.randrange(1, 3, 1)
                            time.sleep(w2)
                        #pyautogui.moveTo(425, 400)
                        #pyautogui.click(button='left')
                                                        
                        except:
                            pyautogui.moveTo(425, 400)
                            pyautogui.click(button='left')
                            
                        
                    if i >= L:
                    # to source page
                        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/header/div/div[2]/div[2]/ul/li/a")
                        e.click()
                    
                    c = c+1
                    c1 = c1+1
                    
                    yield item
                        
            c1=1  
   
            #except:
              #   Exception_list.append(x)
              #   e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/header/div/div[2]/div[2]/ul/li/a")
              #   e.click()
              #   pass

        '''
        test = response.xpath("/html/body/div[5]/section[2]/div/div[1]/div[4]/div/div[2]/div[1]/div[4]")
        text = test.xpath("./text()")
        print(text)
        print(test)
        '''
        #for each in response.xpath("//*[@id='s-lg-az-name-a']"):
            #test = each.xpath("./div[1]/div[4]/text()").extract()
         #   print(each)
        
        '''
        time.sleep(10)
        DL = self.driver.find_element_by_xpath("//a[@href='https://login.proxy.binghamton.edu/login?url=http://infoweb.newsbank.com/?db=AWNB']")
        DL.click()
        time.sleep(10)
        window_after = self.driver.window_handles[-1]
        self.driver.switch_to_window(window_after)
        e = self.driver.find_element_by_xpath("//*[@id='username']")
        print(e)
        e.send_keys("xwang222")
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='password']")
        e.send_keys("Z6A9s6y5")
        time.sleep(10)
        e = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div[3]/div/form/section[5]/input[4]")
        time.sleep(10)
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/section[1]/div[2]/div[1]/ul/li/a")
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='nbcore-react-browse-table-pane-source-list-page-filter']")
        e.send_keys("times union")
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='nbcore-react-browse-table-pane-source-list-page-table']/tbody/tr[4]/td[1]/span[2]/a")
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='edit-val-base-0']")
        e.send_keys("unemployment county")
        e = self.driver.find_element_by_xpath("//*[@id='edit-gnus-simple-search']/div[2]/button")
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='edit-date-from--2']")
        e.send_keys("2006")
        time.sleep(5)
        e = self.driver.find_element_by_xpath("//*[@id='edit-date-to--2']")
        e.send_keys("2019")
        time.sleep(5)
        e = self.driver.find_element_by_xpath("//*[@id='search_nav-submit']")
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='navigator-search-sort']/div/div/ul/li[3]/a")
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='search-hits__hit--1']/div[2]/div/div[2]/div[1]")
        e.click()
        time.sleep(10)
        e = self.driver.find_element_by_xpath("//*[@id='document-view--ascii']/div/div[1]/h1")
        title = e.extract()
        print(title)
        '''
        
        
        '''
        //*[@id="main-content"]/div[1]/div[7]/button
        //*[@id="main-content"]/div[1]/div[7]/div/div[2]/div/button[1]
        //*[@id="main-content"]/div[1]/div[2]/div/div[3]/button
        //*[@id="nbcore-doc-nav__item__next"]/a
        /html/body/div[2]/div[4]/section[1]/nav/nav/span[2]
        //*[@id="nbcore-doc-nav__item__next"]
        '''
        '''
        window_after = self.driver.window_handles[-1]
        self.driver.switch_to_window(window_after)
        DL = self.driver.find_element_by_xpath("//*[@id='advancedButton']")
        DL.click()
        '''
        #self.driver.close()
        # window_before = self.driver.window_handles[0]
        # while True:
        '''
        cookies = self.driver.find_element_by_xpath('//div[@class="cookies"]')
        next = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/div[1]/div[2]/span[1]')
        self.driver.execute_script("arguments[0].style.visibility='hidden'", cookies)
        next.click()
        time.sleep(5)
        '''
        '''
        window_after = self.driver.window_handles[-1]
        self.driver.switch_to_window(window_after)

        DL = self.driver.find_element_by_xpath('//*[@id="download"]')
        DL.click()
        time.sleep(6)
        keyboard.press_and_release('enter')
        # self.driver.switch_to_window(window_before)
        # self.driver.close()

        # next.send_keys("\n")

        # self.driver.close()
        # get the data and write it to scrapy items
        # except:
        # break
        
        '''
        
        
