import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse

from nejma.ext.starlette import WebSocketEndpoint

app = Starlette()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>ws</title>
    </head>
    <body>
        <h1>Nejma ⭐ Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>username : </label><input type="text" id="username" autocomplete="off"/><br/>
            <label>room id : </label><input type="text" id="roomId" autocomplete="off"/><br/>
            <label>message : </label><input type="text" id="messageText" autocomplete="off"/><br/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var data = JSON.parse(event.data);
                message.innerHTML = `<strong>${data.username} :</strong> ${data.message}`;
                messages.appendChild(message);
            };
            function sendMessage(event) {
                var username = document.getElementById("username");
                var room = document.getElementById("roomId");
                var input = document.getElementById("messageText");
                var data = {
                    "room_id": room.value, 
                    "username": username.value,
                    "message": input.value,
                };
                ws.send(JSON.stringify(data));
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""


@app.route("/")
class Homepage(HTTPEndpoint):
    async def get(self, request):
        return HTMLResponse(html)


@app.websocket_route("/ws")
class Echo(WebSocketEndpoint):
    encoding = "json"

    async def on_receive(self, websocket, data):
        room_id = data['room_id']
        message = data['message']
        username = data['username']

        if message.strip():
            group = f"group_{room_id}"

            self.channel_layer.add(group, self.channel)

            payload = {
                "username": username,
                "message": message,
                "room_id": room_id
            }
            await self.channel_layer.group_send(group, payload)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
