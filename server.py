import asyncio
import json
from json import JSONDecodeError

from aiohttp import web, WSMsgType, WSMessage
from aiohttp_apispec import setup_aiohttp_apispec, docs, request_schema
import logging
from marshmallow import ValidationError

from message import send_message_to_all, send_message
from schemas import MessageSchema

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()

@docs(
   tags=["telegram"],
   summary="Send message API",
   description="This end-point sends message to telegram bot user/users",
)
@request_schema(MessageSchema())

@routes.post("/")
async def index_get(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except JSONDecodeError:
        return web.json_response({"result": "Request data is invalid"})

    try:
        schema = MessageSchema()
        data = schema.load(payload)
    except ValidationError as e:
        return web.json_response({"result": "Validation Error", "error": e.messages})

    await send_message_to_all(data.get("message"))
    return web.json_response({"result": "OK"})



@docs(
   tags=["websocket"],
   summary="web socketconnection",
   description="This end-point websocket",)
@routes.get("/ws")
async def websockets(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:  # type: WSMessage
        if msg.type == WSMsgType.TEXT:
            if msg.data == "/close":
                await ws.close()
            else:
                data = json.loads(msg.data)
                await send_message_to_all(data['message'])
        elif msg.type == WSMsgType.ERROR:
            logger.error(f"WS connection closed with exception {request.app.ws.exception()}")
    return ws


if __name__ == "__main__":
    app = web.Application()
    setup_aiohttp_apispec(
        app=app, title="mytmsbot Bot documentation", version="v1.0",
        url="/api/docs/swagger.json", swagger_path="/api/docs",
    )
    app.add_routes(routes)
    web.run_app(app, port=5000)
