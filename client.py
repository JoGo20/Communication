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
    # print(response['configuration']['initialState']['turn'])
    if(response['type'] == 'START'):
        # State = States.READY
        GameInfo.GameConfig = response['configuration']
        GameInfo.PlayerColor = response['color']
        print(GameInfo.GameConfig['initialState']['turn'])
        print(GameInfo.PlayerColor)
        # print(GameInfo.PlayerColor == GameInfo.GameConfig['initialState']['turn'])
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
    PlaceMove = {
                    'type' : 'place',
                    'point': { 
                                'row':-1,
                                'column':-1 
                            }
                 
                }
    
    return ResignMove
    

async def ThinkState():
    global GameInfo
    print("Thinking")
    while 1:
        pass
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

async def Pong():
    global GameInfo
    
    while True :
            GameInfo.Socket.pong()
        

async def InitState():
    print("let's start!")
    global GameInfo
    GameInfo.Socket = await websockets.connect('ws://localhost:8080',ping_interval=1000) 
    
    
    response = await GameInfo.Socket.recv()
    asyncio.get_event_loop().run_until_complete(Pong())
    print(response)
    
    x = await GameInfo.Socket.send(json.dumps({'type': 'NAME', 'name': 'Ezzat'}))   
    GameInfo.State = States.READY


async def main():
    global GameInfo
    # print("Welcome !")
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
    