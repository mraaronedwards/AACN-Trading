import requests
import json

def retrieve_messsages(channelid):
    headers = {
        'authorization' : 'OTI2MTg0MTY0NDk0MDIwNjU5.GW0f0C.OMg1h2PQKQzORD1zWUGDmGcT4ns_9Gca5fS7Uo' 
    }
    r = requests.get(f'https://discord.com/api/v9/channels/{channelid}/messages', headers = headers)


    messages = json.loads(r.text)

    for message in messages:
        Author = message['author']
        if Author['username'] == 'Bender':
           print(message['content'] + ' | ' + message['timestamp'] + '\n')
            
retrieve_messsages('1247171895648845874')