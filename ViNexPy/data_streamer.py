from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.responses import HTMLResponse
import asyncio

try:
    from vicon_dssdk import ViconDataStream
except ImportError:
    print("Make sure vicon DataStreamSDK is installed: Follow the instructions in https://www.vicon.com/software/datastream-sdk/\n")
    #raise


app = FastAPI()
defaultHost = "0.0.0.0"
defaultPort = "5001"

#parameters
tick_rate = 0.01

def _init_api(connection=None, host=defaultHost, port=defaultPort, use_json=False):
    try:
        global client
        client = get_vicon_instance(connection)
    except Exception as e:
        print("Failed to connect to client")
        client = None   


#Runs every      
@app.websocket("/marker/{subject_name}")
async def websocket_endpoint(websocket: WebSocket, subject_name):
    await websocket.accept()
    while True:
        data = get_data
        print("Executing")
        await websocket.send_json(get_data(client, "marker", subject_name))
        await asyncio.sleep(tick_rate)  

def get_vicon_instance(connection=None):
    if connection is None:
        connection = 'localhost:801'
    client = ViconDataStream.Client()

    print('Connecting...')
    while not client.IsConnected():
        client.Connect(connection)
    print('Connected to vicon data stream')
    client.EnableSegmentData()
    client.EnableMarkerData()
    logger.info(client.GetAxisMapping())
    return client

def get_data(client, data_type, subject_name):
    data = {}
    # logger.info(*[n for n in client.__dir__() if "G" in n], sep="\n")
    # slogger.info(client.GetSegmentNames(subject_name))
    if data_type == "marker":
        marker_segment_data = {}
        marker_data = {}
        for marker, segment in client.GetMarkerNames(subject_name):
            try:
                marker_segment_data[segment].append(marker)
            except KeyError:
                marker_segment_data[segment] = [marker]
            marker_data[marker] = client.GetMarkerGlobalTranslation(subject_name, marker)[0]
            # logger.info(client.GetMarkerGlobalTranslation(subject_name, marker))
        data['data'] = marker_data
        data['hierachy'] = marker_segment_data
        
    elif data_type == "segment":
        segment_data = {}
        for segment in client.GetSegmentNames(subject_name):
            translation, status = client.GetSegmentGlobalTranslation(subject_name, segment)
            rotation, status = client.GetSegmentGlobalRotationQuaternion(subject_name, segment)
            segment_data[segment] = translation + rotation
        data['data'] = segment_data
            
    return data




if __name__ == "__main__":
    _init_api('localhost:801', defaultHost, defaultPort, False)
    uvicorn.run(app, host = defaultHost, port = defaultPort)