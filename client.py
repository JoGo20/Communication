import asyncio
import json
import websockets
from enum import Enum
import random
import threading 
import sys

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
    
    def GetGameConfig(self):
        return self.GameConfig
        
GameInfo = Game()

async def ReadyState():
    print("I am Ready!")
    global GameInfo
    
    response = await GameInfo.Socket.recv()
    response = json.loads(response)
    if(response['type'] == 'START'):
        # State = States.READY
        GameInfo.GameConfig = response['configuration']
        GameInfo.PlayerColor = response['color']
        print(GameInfo.GameConfig['initialState']['turn'])
        print(GameInfo.PlayerColor)
        print(GameInfo.GameConfig['moveLog'])
        MoveLog = GameInfo.GameConfig['moveLog']
        # print(GameInfo.PlayerColor == GameInfo.GameConfig['initialState']['turn'])
        if ( (GameInfo.PlayerColor == GameInfo.GameConfig['initialState']['turn'] and len(MoveLog) % 2 == 0) or (GameInfo.PlayerColor != GameInfo.GameConfig['initialState']['turn'] and len(MoveLog) % 2 != 0)) :
            GameInfo.State = States.THINK
        else:
            GameInfo.State = States.IDLE
        # print(GameInfo.PlayerColor)
    elif response['type'] == 'END':
        print("End")
    else:
        print("Nothing")
            
    pass
async def IdleState():
    global GameInfo
    print("Idle")
    
    Msg = await GameInfo.Socket.recv() 
    Msg = json.loads(Msg)
    print(Msg)
    if Msg['type'] == "MOVE" :
        GameInfo.State = States.THINK
        
    elif Msg['type'] == 'END' :
        GameInfo.State = States.READY
    
    pass

def MakeMove():
    PassMove = {'type' : 'pass'}
    ResignMove = {'type': 'resign'}
    
    x = random.randrange(0,20)
    y = random.randrange(0,20)
    
    PlaceMove = {
                    'type' : 'place',
                    'point': { 
                                'row':x,
                                'column':y
                            }
                 
                }
    
    return PlaceMove
    

async def ThinkState():
    global GameInfo
    print("Thinking")
    # while 1:
    #     print('x')
    #     pass
    Msg = None
    while True:    
        # x =  input('Enter move')
        MsgToSend = {
                        'type': 'MOVE',
                        'move': MakeMove()
                    }
        
        print(MsgToSend)
        x = await GameInfo.Socket.send( json.dumps(MsgToSend) )
        
        Msg = await GameInfo.Socket.recv()
        Msg = json.loads(Msg)
        print(Msg)
        if Msg['type'] == 'END':
            GameInfo.State = States.READY
            return
        elif Msg['type'] == "VALID":
            GameInfo.State = States.IDLE
            return
    
    pass


async def InitState(name):
    
    global GameInfo
    GameInfo.Socket = await websockets.connect('ws://localhost:8080',ping_interval=100) 
    print("let's start!")
    t2 = threading.Thread(target=ping_pong_handler).start()  # ping pong
    
    response = await GameInfo.Socket.recv()
    # asyncio.get_event_loop().run_until_complete(Pong())
    print(response)
    
    x = await GameInfo.Socket.send(json.dumps({'type': 'NAME', 'name': str(name)}))   
    GameInfo.State = States.READY
    
async def ping_pong():
    global GameInfo
    print("Ping")
    while True:
        try:
            await GameInfo.Socket.pong()
            await asyncio.sleep(0.5)
        except Exception as e:
            print(e)
            return

def ping_pong_handler():
    asyncio.new_event_loop().run_until_complete(ping_pong())

async def main(name):
    global GameInfo
    while(1):
        try:
            if GameInfo.State == States.INIT:
                await InitState(name)
            elif  GameInfo.State == States.READY:
                await ReadyState()
            elif  GameInfo.State == States.IDLE:
                await IdleState()
            elif  GameInfo.State == States.THINK:
                await ThinkState()
        except:
            GameInfo.State = States.INIT

if __name__ == "__main__":
    name = sys.argv[1]
    asyncio.get_event_loop().run_until_complete(main(name))
    