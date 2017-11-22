#!/usr/bin/env python
#-*-coding:utf-8-*-
from gmail_api_wrapper.crud.read import GmailAPIReadWrapper
from gmail_api_wrapper.crud.write import GmailAPIWriteWrapper
from app import User, Channel, Member
import base64
import re

gmail_api = GmailAPIReadWrapper()
api = GmailAPIWriteWrapper()

# Check unread messages. Returns a list of dicts in the below format

dicts = gmail_api.check_new_mail()


new_message = 0
result=""
for x in dicts:
    new_message = new_message +1
    str1 = str(base64.b64decode(x['base64_msg_body']))
    #str1,str2 = str1.split("b'") #Baştaki gereksiz b' kısmını kestim.
    #str2.strip("\n'") #Sondaki gereksiz ' kısmını kestim
    #Sondaki \r\n silinecek.
    #Türkçe karekter desteklenmiyor.
    #print(x)
    #print("\n")
    
if new_message > 0:
    result = re.search('<(.*)>', x['from'])
    #from kısmındaki gereksiz veriden kurtulup sadece mail kısmını elde ettik
    r = Member.query.filter_by(channelName=x['subject']).all()
    for t in r:
        s = User.query.filter_by(username=t.memberName).all()
        #s = username'i t.memberName olan satırların hepsi. her bir username için dönüyor.
        for z in s:
            #her bir username için, onların e-maili dönüyor.
            #bir username bir maile sahip olduğu için x=z eşitliği var
            if(z.email == result.group(1)):
                continue
            api.compose_mail(subject=x['subject'], body=str1, to=z.email)
            #kanala mesaj gonderenın mailine gelince continue deyip mesajın geri atılmamasını sağladık
else:
    print("Kanala atilan yeni bir mesaj bulunmamaktadir")
            


    

  



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
