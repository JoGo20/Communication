import asyncio
import json
import websockets
from enum import Enum

class States(Enum):
    INIT = 1
    READY = 2
    IDLE = 3
    THINK = 4
    
class Game:
    def __init__(self):
        self.State = States.INIT    
        self.GameConfig = None
        self.PlayerColor = None
        self.Socket = None
        self.Name = None
        
GameInfo = Game()

async def ReadyState():
    print("I am Ready!")
    global GameInfo
    
    response = await GameInfo.Socket.recv()
    response = json.loads(response)
    print(response)
    if(response['type'] == 'START'):
        # State = States.READY
        GameInfo.GameConfig = response['configuration']
        GameInfo.PlayerColor = response['color']
        print(GameInfo.GameConfig['initialState']['turn'])
        print( GameInfo.PlayerColor == GameInfo.GameConfig['initialState']['turn'])
        if GameInfo.PlayerColor == GameInfo.GameConfig['initialState']['turn']:
            GameInfo.State = States.THINK
        else:
            GameInfo.State = States.IDLE
        print(GameInfo.PlayerColor)
    elif response['type'] == 'END':
        print("End")
    else:
        print("Nothing")
            
    pass
async def IdleState():
    global GameInfo
    print("Idle")
    pass
async def ThinkState():
    global GameInfo
    print("Thinking")
    pass


async def InitState():
    print("let's start!")
    global GameInfo
    GameInfo.Socket = await websockets.connect('ws://localhost:8080') 
        
    response = await GameInfo.Socket.recv()
    print(response)
    
    x = await GameInfo.Socket.send(json.dumps({'type': 'NAME', 'name': 'Yara&Ezzat'}))   
    GameInfo.State = States.READY


async def main():
    global GameInfo
    print("Welcome !")
    while(1):
        print(GameInfo.State)
        if GameInfo.State == States.INIT:
            await InitState()
        elif  GameInfo.State == States.READY:
            await ReadyState()
        elif  GameInfo.State == States.IDLE:
            await IdleState()
        elif  GameInfo.State == States.THINK:
            await ThinkState()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    