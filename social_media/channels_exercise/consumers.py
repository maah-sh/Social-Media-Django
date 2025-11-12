import json

from channels.generic.websocket import AsyncWebsocketConsumer


class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]

        await self.channel_layer.group_add(self.username, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.username, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        receiver_username = text_data_json["receiver_username"]
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            receiver_username, {"type": "inbox.send", "message": message}
        )

    async def inbox_send(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
