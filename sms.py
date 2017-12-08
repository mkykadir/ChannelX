from app import User, Channel, Member
import datetime
from datetime import timedelta
import time
from smsGateway import smsGateway

from gmail_api_wrapper.crud.write import GmailAPIWriteWrapper

email = 'mur.ozkok96@gmail.com'
password = 'itusesms'
sms_handler = smsGateway(email,password) 
device_id = 69114#Device ID in SMS Gateway API

while True:
    print("###################SMS PERIYODU BASLIYOR##################")
    api = api = GmailAPIWriteWrapper()
    messages = sms_handler.getMessages()
    simdi = datetime.datetime.fromtimestamp(time.time()) + timedelta(hours=-7)#received sms times are set for gmt-4 due to sms api, difference is handled there.
    for it in messages["response"]["result"]:
        if it["status"]=="received":
            first_message = it
            break
    
    print(simdi)
    #print(first_message)
    print(datetime.datetime.fromtimestamp(first_message["received_at"]))
    
    new_messages = list()
    if first_message["status"]=="received" and datetime.datetime.fromtimestamp(first_message["received_at"]) > (simdi+timedelta(minutes=-2)) :
        for m in messages["response"]["result"]:#getmessages method of api lists all messages sent, received and pending
            if m["status"]!="received":          #we only use received messages, so others is unnecessary
                continue
                
            if datetime.datetime.fromtimestamp(m["received_at"]) > (simdi+timedelta(minutes=-2)):
                new_messages.append(m)
        for nm in new_messages:
            message_content = nm["message"].split(":")  #SMS Format: "channelname:message"
            if(len(message_content)<=1):
                continue
            ch_name = message_content[0]
            print(ch_name)
            msg = message_content[1]
            members = Member.query.filter_by(channelName = ch_name).all()
            print(members)
            numbers=list()#for sms sending phase
            emails = list()
            for member in members:
                users = User.query.filter_by(username = member.memberName).all()
                for user in users:
                    if user.phone == nm["contact"]["number"]:
                        sender = user.username
                        msg = sender+":"+ch_name+":"+msg #gönderenadı:kanaladı:mesaj
                        emails.append(user.email)
                        print(member.memberName)
                        continue
                    if member.prefersEmail:
                        emails.append(user.email)
                        print(member.memberName)
                        print("Email de gonderecegiz bir gun!!!")#Burası düzenlenecek
                    if member.prefersPhone:
                        #sms_handler.sendMessageToNumber(user.phone,msg,device_id)
                        numbers.append(user.phone)
                        #print(member.memberName)
            print(numbers)
            for number in numbers:
                sms_handler.sendMessageToNumber(number,msg,device_id)          
            emailstr = str()
            for email in emails:
                emailstr = emailstr+email+','
            emailstr = emailstr[:-1]
            api.compose_mail(subject=ch_name, to='goldennnnn01@hotmail.com', body=message_content[1], bcc=emailstr)
                

    else:
        print("There is no new message sent to channel!")
    time.sleep(60)