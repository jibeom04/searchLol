import requests
 
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
 
myToken = "xoxb-3121161129187-3123495414420-9fTtHcBUPURqtZt49YReRrWn"
 
post_message(myToken,"#일반","Hello slack")
