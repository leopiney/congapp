import json
import pprint
import traceback

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from conga.game import Game

app = FastAPI()

game = Game()


valid_actions = [
    "add_player",
    "start_match",
    "player_turn_pick",
    "player_turn_throw",
    "player_finish_attempt",
]

sockets = []


# with open("game.json") as f:
#     game_json = json.load(f)
#     game = game.from_dict(game_json)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    sockets.append(websocket)

    print(f"Added new socket. Total: {len(sockets)}")

    while True:
        try:
            data = await websocket.receive_json()
            print(f"Received message {data}")

            for player in game.players:
                player.update_state()

            if "action" in data and data["action"] in valid_actions:
                action = getattr(game, data["action"])
                params = data["action_params"] if "action_params" in data else {}
                action(**params)

            if data["action"] in ["player_turn_throw", "start_match"]:
                for player in game.players:
                    player.update_state()
                    player.sort_cards()

            pprint.pprint(game.to_dict())

            with open("game.json", "w") as f:
                json.dump(game.to_dict(), f)

            for i, socket in enumerate(sockets):
                await socket.send_json({"game": game.to_dict()})

        except WebSocketDisconnect as ex:
            print(f"Socket diconnected, removing it: {ex}")
            sockets.remove(websocket)
            break

        except Exception as ex:
            print(f"Unexpected error ({ex.__class__.__name__}): {ex}")
            print(traceback.format_exc())
            await websocket.send_json({"game": game.to_dict(), "error": str(ex)})
