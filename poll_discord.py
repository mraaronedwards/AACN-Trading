import asyncio
import json
import websockets

token = "OTI2MTg0MTY0NDk0MDIwNjU5.GW0f0C.OMg1h2PQKQzORD1zWUGDmGcT4ns_9Gca5fS7Uo"  
channel_id = "1334347783435714563"


async def connect_discord():
    while True:
        try:
            async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
                await ws.send(json.dumps({"op": 2, "d": {"token": token, "intents": 32767, "properties": {}}})) # Correct intents

                while True:
                    message = await ws.recv()
                    message = json.loads(message)

                    op_code = message.get('op')
                    event_type = message.get('t')
                    event_data = message.get('d')

                    if op_code == 0 and event_type == 'READY':
                        print("Connected and Ready!")
                        # No need for separate presence update with correct intents in identify payload
                    elif op_code == 0 and event_type == 'MESSAGE_CREATE' and event_data['channel_id'] == channel_id:
                        print(event_data['content'] + ' | ' + event_data['timestamp'] + '\n')
                    elif op_code == 10:  # Heartbeat
                        heartbeat_interval = event_data['heartbeat_interval']
                        await ws.send(json.dumps({"op": 1, "d": None}))  # Respond immediately
                        await asyncio.sleep(heartbeat_interval * 0.001 * 0.75)  # Then sleep for a bit less than the interval
                        await ws.send(json.dumps({"op": 1, "d": None}))  # Send another heartbeat

        except websockets.exceptions.ConnectionClosedError:
            print("WebSocket connection closed. Reconnecting...")
            await asyncio.sleep(5)

asyncio.run(connect_discord())