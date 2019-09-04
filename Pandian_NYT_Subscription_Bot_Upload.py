#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 10:17:29 2019

@author: pandian_krishna
NYT Subscription Service WebScraper
"""

import requests
import csv
import smtplib
import time
from bs4 import BeautifulSoup
from email.message import EmailMessage
from datetime import date
from datetime import datetime, timedelta
from validate_email import validate_email

new_york_times = "https://www.nytimes.com"


'''
This function will be the one parsing all the data and links we will need.
It utilizes Beautiful soup and the datetime library to check all the articles 
that were published in those days. This function will also write all that 
information to a text file to be accessed later.
'''

def parse_articles():
    today_parsed = date.today()
    yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y/%m/%d')
    today = today_parsed.strftime("%Y/%m/%d")   #Gets the recent dates
    #print("today =", today)
    #print("yesterday=", yesterday)
    
    result = requests.get(new_york_times)   #gets the current html
    src = result.content
    soup = BeautifulSoup(src, "lxml")       
    links = soup.find_all('a', href = True) #gets all a tags 
    
    list_of_links = []
    title = []
    
    for link in links:
        if today in link['href']:
            #print(new_york_times + link['href'])
            list_of_links.append(new_york_times + link['href']) #checks if it's today's news
        if yesterday in link['href']:
            #print(new_york_times + link['href'])
            list_of_links.append(new_york_times + link['href']) #checks if yesterdays news
    #print(list_of_links)
    for page in list_of_links:
        link_reversed = page[::-1]  #parses so we can get the title of the article
        #print(link_reversed)
        string = 0
        while(link_reversed[string] != '.'):
            string += 1
        string += 2
        #print(string)
        link_reversed = page[len(link_reversed)-string::-1]
        #print(page)
        #print(link_reversed)
        title_length = 0
        while link_reversed[title_length] != '/':
            title_length += 1
        title_length += 1
        link_reversed = page[len(link_reversed) - 1:len(link_reversed) - title_length:-1]
        actual_title = link_reversed[::-1]
        actual_title = actual_title.replace("-", " ")
        #print(actual_title.upper())
        title.append(actual_title.upper())
    text = 'Here is Your Activity Feed for Today:\n'
    for i in range(len(title)):
        text = text + ('<a href = "{}">{}\n</a>').format(list_of_links[i],title[i]) #formats as html string
    email = open("email.txt", 'w')
    email.write(text)
    email.close()
    
    
    
    
    
'''
This function will serve as the subscription based adding software. This will 
validate emails to see if the emails and times inputted are valid. It will write 
to a csv file each email address and their valid times.
'''
    
def addUserInformation():
    email_good = False   #initializes 2 constants that make sure it iterates
    time_good = False
    
    while not email_good:
        receiving_id = input('Please enter Your Email: ')
        valid_email = validate_email(receiving_id)  #checks if input is valid
        if valid_email == False:
            print('Invalid Input')
        else:
            print('Valid Email')
            email_good = True
            
    while not time_good:
        time_to_receive = input('What time of day would you like to be notified? HH:MM: ') #checks if input is valid
         
        try:
            int(time_to_receive[0:2])
            int(time_to_receive[3:])
            if int(time_to_receive[0:2]) > 23 or int(time_to_receive[0:2]) < 0 or int(time_to_receive[3:]) > 59 or int(time_to_receive[3:]) < 0 or time_to_receive[2] != ':':
                print('Invalid Input')
            else:
                print('Valid Time')
                time_good = True
        except:
            print('Invalid input')
    
    with open('information.csv', 'a') as csv_file: #pushes data to csv file
        csv_opened = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        csv_opened.writerow([receiving_id, time_to_receive])
        #print('wrote to csv file')
    csv_opened.close()
    #print('completed')
    
    
'''
This Function serves as a way to place all the contents of the email together 
and ensures that we are sending the email to the correct person. Here we use SMTP
server connection to access our email account so we are able to send and format emails.
'''
        
def testSend(email_string):
    message = EmailMessage()
    message['From'] = '' #use the email you would like
    message['to'] = email_string
    message['Subject'] = "NYT Daily Report"
    body = ' ' #defining a string
    smtp = smtplib.SMTP('smtp.gmail.com', 587) #create server session

    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    
    with open("email.txt", "r") as send_email:  #make string html
        body = send_email.readlines()
        stringlist = "\n\n\n".join(x for x in body)
        #print(stringlist)
        message.add_alternative(stringlist, subtype='html')
        
        
    smtp.login('','') #add User Information
    smtp.send_message(message)
    smtp.quit() #Quit Server Session
'''
This function exists to check whether at the given moment if there are any users 
that should be receiving their daily checkup of information. It also contains a time.sleep()
to ensure that a user doesn't receive the same email multiple times.
'''
    

def sendEmail():        
    current_time = datetime.strftime(datetime.now(), "%H:%M")
    #print(current_time)
    #current_time = "13:00"
    with open('information.csv', 'r') as csv_file:
        #print(len(csv_file))
        for row in csv_file:
            if current_time in row: #checks if a time is in the csv
                #print('spotted')
                char = 0
                while row[char] != ',':
                    char += 1
                char -= 1
                email_name = row[1:char] #gets the email address
                parse_articles()
                testSend(email_name)
                time.sleep(60)
'''
This is a sub function to get the number or rows of our csv file so we can iterate 
that many times for checking.
'''
                
def GetSize():
    with open('information.csv', 'r') as csv_file:
        size = sum(1 for row in csv_file) #gets the size of csv file
        #print(size)
        return size
        
        