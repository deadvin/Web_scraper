import firebase_admin
from firebase_admin import credentials, messaging
import keys.keys as keys

cred = credentials.Certificate("keys/key.json")
firebase_admin.initialize_app(cred)
tokens = keys.firebase_tokens

def sendPush_twitter(title, msg, link, topic):

    # message = messaging.MulticastMessage(
    #     notification=messaging.Notification(
    #         title=title,
    #         body=msg
    #     ),
    #     data=dataObject,
    #     tokens=tokens,
    # )

    message = messaging.Message(
        data={

            'title': title,
            'text': msg,
            'link': link,
            'topic': topic,
        },
        topic=topic
    )

    response = messaging.send(message)

    # response = messaging.send_multicast(message)

    print('Successfully sent message:', response)
    print('Title: ' + title)
    print('Text: ' + msg)


def sendPush_price(sym, price, topic):

    message = messaging.Message(
        data={
            'title': sym,
            'text': str(price),
        },
        topic=topic,
    )

    response = messaging.send(message)

    print('Successfully sent message:', response)