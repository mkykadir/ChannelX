from app import User, Channel, Member
import datetime
from datetime import timedelta
import time
from smsGateway import smsGateway

email = 'mur.ozkok96@gmail.com'
password = 'itusesms'
sms_handler = smsGateway(email,password) 

while True:
    print("###################SMS PERIYODU BASLIYOR##################")
    messages = sms_handler.getMessages()
    simdi = datetime.datetime.fromtimestamp(time.time()) + timedelta(hours=-7)#received sms times are set for gmt-4 due to sms api, difference is handled there.
    for it in messages["response"]["result"]:
        if it["status"]=="received":
            first_message = it
            break
    
    print(simdi)
    #print(first_message)
    
    device_id = 68189#Device ID in SMS Gateway API
    new_messages = list()
    if first_message["status"]=="received" and datetime.datetime.fromtimestamp(first_message["received_at"]) >= (simdi+timedelta(minutes=-20)) :
        for m in messages["response"]["result"]:#getmessages method of api lists all messages sent, received and pending
            if m["status"]!="received":          #we only use received messages, so others is unnecessary
                continue
                
            if datetime.datetime.fromtimestamp(m["received_at"]) > (simdi+timedelta(minutes=-20)):
                new_messages.append(m)
        for nm in new_messages:
            message_content = nm["message"].split(":")  #SMS Format: "channelname:message"
            if(len(message_content)<=1):
                continue
            ch_name = message_content[0]
            #print(message_content)
            msg = message_content[1]
            members = Member.query.filter_by(channelName = ch_name).all()
            numbers=list()#for sms sending phase
            for member in members:
                users = User.query.filter_by(username = member.memberName).all()
                for user in users:
                    if user.phone == nm["contact"]["number"]:
                        sender = user.username
                        msg = sender+":"+ch_name+":"+msg
                        print(member.memberName)
                        continue
                    if member.prefersEmail:
                        print("Email de gonderecegiz bir gun!!!")#Burası düzenlenecek
                    if member.prefersPhone:
                        #sms_handler.sendMessageToNumber(user.phone,msg,device_id)
                        numbers.append(user.phone)
                        print(member.memberName)
            print(numbers)
            for number in numbers:
                sms_handler.sendMessageToNumber(number,msg,device_id)                  

    else:
        print("There is no new message sent to channel!")
    time.sleep(60)