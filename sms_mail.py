from app import User, Channel, Member
import datetime
from datetime import timedelta
import time
from smsGateway import smsGateway
from gmail_api_wrapper.crud.read import GmailAPIReadWrapper
from gmail_api_wrapper.crud.write import GmailAPIWriteWrapper
import base64
import re

email = 'kyazoglu@hotmail.com'
password = 'premium111'
sms_handler = smsGateway(email,password) 
device_id = 69089#Device ID in SMS Gateway API

while True:
    print("###################SMS ve E-mail Periyodu Başlıyor##################")
    gmail_api = GmailAPIReadWrapper()
    api = GmailAPIWriteWrapper()
    messages = sms_handler.getMessages()
    simdi = datetime.datetime.fromtimestamp(time.time()) + timedelta(hours=-7)#received sms times are set for gmt-4 due to sms api, difference is handled there.
    for it in messages["response"]["result"]:
        if it["status"]=="received":
            first_message = it
            break
   
    
    new_messages = list()
    #SMS okuma işi başlıyor
    if first_message["status"]=="received" and datetime.datetime.fromtimestamp(first_message["received_at"]) > (simdi+timedelta(minutes=-50)) :
        for m in messages["response"]["result"]:#getmessages method of api lists all messages sent, received and pending
            if m["status"]!="received":          #we only use received messages, so others is unnecessary
                continue
                
            if datetime.datetime.fromtimestamp(m["received_at"]) > (simdi+timedelta(minutes=-50)):
                new_messages.append(m)
        for nm in new_messages:
            message_content = nm["message"].split(":")  #SMS Format: "channelname:message"
            if(len(message_content)<=1):
                continue
            ch_name = message_content[0]
            msg = message_content[1]
            members = Member.query.filter_by(channelName = ch_name).all()
            numbers=list()#for sms sending phase
            emails = list()
            for member in members:
                users = User.query.filter_by(username = member.memberName).all()
                for user in users:
                    if user.phone == nm["contact"]["number"]:
                        sender = user.username
                        msg = sender+":"+ch_name+": #Message: "+msg #gönderenadı:kanaladı:mesaj
                        emails.append(user.email)
                        continue
                    if member.prefersEmail:
                        emails.append(user.email)
                    if member.prefersPhone:
                        #sms_handler.sendMessageToNumber(user.phone,msg,device_id)
                        numbers.append(user.phone)
                        #print(member.memberName)
            for number in numbers:
                sms_handler.sendMessageToNumber(number,msg,device_id)          
            emailstr = str()
            for email in emails:
                emailstr = emailstr+email+','
            emailstr = emailstr[:-1]
            api.compose_mail(subject=ch_name, to='goldennnnn01@hotmail.com', body=message_content[1], bcc=emailstr)

    #Email-okuma işi başlıyor     
    dicts = gmail_api.check_new_mail()
    new_message = 0
    result=""
    str2=''
    emails = list()
    numbers=list()#for sms sending phase

    for x in dicts:
        new_message = new_message +1
        
    if new_message > 0 and x['base64_msg_body'] != []:
        str1 = str(base64.urlsafe_b64decode(x['base64_msg_body']).decode('utf-8'))
        result = re.search('<(.*)>', x['from'])
        #from kısmındaki gereksiz veriden kurtulup sadece mail kısmını elde ettik
        r = Member.query.filter_by(channelName=x['subject']).all()
        #r = channelName'ı x['subject'] olan memberların hepsi
        for t in r:
            s = User.query.filter_by(username=t.memberName).all()
            #s = username'i t.memberName olan satırların hepsi. her bir username için dönüyor.
            for z in s:
                if(z.email == result.group(1)):
                    str1 = z.username + ': #Message: ' + str1     #Mesajın gönderenin emailinden username'ini bulup body'nin başına ekliyorum.
                    continue                            #Mesaj gönderen, mesajın iletileceği kişiler arasında yer almasın diye bunu es geçiyorum
                
                if t.prefersEmail:
                    str2 = z.email + ',' + str2 + ','
                    str2 = str2[:-1]
                if t.prefersPhone:
                    numbers.append(z.phone)
                index = str1.find(":") + 1
                str5 = str1[:index] + x['subject'] + ":" + str1[index:]
               
        for number in numbers:
            sms_handler.sendMessageToNumber(number,str5,device_id)          
        
        str2 = str2[:-1] #Bcc listesinin en sonundaki fazlalık virgülü sildim.
        #print("SMS olarak gönderilen mesaj body'si: " + str5)
        #print("Email olarak gönderilen mesaj body'si: " + str1)
        #print("Email konusu:  " + x['subject'])
        #print("Email bcc'si:  " + str2)
        api.compose_mail(subject=x['subject'], body=str1, to='goldennnnn01@hotmail.com', cc='', bcc=str2)
                
    else:
        print("There is no new message sent to channel!")
    time.sleep(60)
