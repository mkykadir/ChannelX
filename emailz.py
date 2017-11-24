#!/usr/bin/env python
#-*-coding:utf-8-*-
from gmail_api_wrapper.crud.read import GmailAPIReadWrapper
from gmail_api_wrapper.crud.write import GmailAPIWriteWrapper
from app import User, Channel, Member
from celery import Celery
import base64
import re
import time
import os

while True:
    gmail_api = GmailAPIReadWrapper()
    api = GmailAPIWriteWrapper()

    # Check unread messages. Returns a list of dicts in the below format

    dicts = gmail_api.check_new_mail()
    new_message = 0
    result=""
    str2=''

    for x in dicts:
        new_message = new_message +1
        str1 = str(base64.b64decode(x['base64_msg_body']).decode('utf-8'))
        
        if new_message > 0:
            result = re.search('<(.*)>', x['from'])
            #from kısmındaki gereksiz veriden kurtulup sadece mail kısmını elde ettik
            r = Member.query.filter_by(channelName=x['subject']).all()
            #r = channelName'ı x['subject'] olan memberların hepsi
            for t in r:
                s = User.query.filter_by(username=t.memberName).all()
                #s = username'i t.memberName olan satırların hepsi. her bir username için dönüyor.
                for z in s:
                    if(z.email == result.group(1)):
                        str1 = z.username + ': ' + str1     #Mesajın gönderenin emailinden username'ini bulup body'nin başına ekliyorum.
                        continue                            #Mesaj gönderen, mesajın iletileceği kişiler arasında yer almasın diye bunu es geçiyorum
                    str2 = z.email + ',' + str2 + ','
                    str2 = str2[:-1]
            api.compose_mail(subject=x['subject'], to='goldennnnn01@hotmail.com', body=str1, bcc=str2)
                
        else:
            print("Kanala atilan yeni bir mesaj bulunmamaktadir")
            os.pause(30)
        
               


    

  


'''

>>> [

        {
            'subject': 'Sample Subject',
            'base64_msg_body': 'base64string',
            'from': 'exapmle@mail_server.com'
            'date': '2017-09-16T10:57:12.4323'
        },
    ]






# Check new mail from specific sender. Returns a list of dicts above
gmail_api.check_new_mail(sender='example@mail_server.com')



# Alternatively, you get all unread messages from a specific sender
gmail_api.get_unread_messages(sender='example@mail_server.com')

>>> [

        {
            'subject': 'Sample Subject',
            'base64_msg_body': 'base64string',
            'from:' 'exapmle@mail_server.com'
            'date': '2017-09-16T10:57:12.4323'
        },
    ]




# Get all labels present. Returns a list of strings
gmail_api.get_labels()

>>> ['INBOX', 'UNREAD', 'SPAM', 'DRAFTS']



# Get total message count. Returns a formatted json object
gmail_api.get_total_messages()

>>> {
        'Total Messages': 2017,
        'Total Threads': 123,
        'Email Address': 'example@mail_server.com'
    }


# Get a list of messages. Defaults to INBOX if no label is specified
gmail_api.list_messages()

>>> [

        {
            'subject': 'Sample Subject',
            'base64_msg_body': 'base64string',
            'from:' 'exapmle@mail_server.com'
            'date': '2017-09-16T10:57:12.4323'
        },
    ]


# Get a list of messages in DRAFTS and SPAM
gmail_api.list_messages(labels=['DRAFTS', 'SPAM'])

>>> [

        {
            'subject': 'Sample Subject',
            'base64_msg_body': 'base64string',
            'from:' 'exapmle@mail_server.com'
            'date': '2017-09-16T10:57:12.4323'
        },
    ]


# Get a specific message. `message_id` passed must be a google message id object
gmail_api.get_message('message_id')'''
