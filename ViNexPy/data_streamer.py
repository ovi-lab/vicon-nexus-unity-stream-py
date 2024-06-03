from fastapi import FastAPI, WebSocket
from datetime import datetime

import uvicorn
import asyncio

try:
    from vicon_dssdk import ViconDataStream
except ImportError:
    print("Make sure vicon DataStreamSDK is installed: Follow the instructions in https://www.vicon.com/software/datastream-sdk/\n")
    #raise


app = FastAPI()
defaultHost = '0.0.0.0'
defaultPort = 5001

#parameters
tick_rate = 0.01\

#Runs every tick rate
@app.websocket("/marker/{subject_name}")
async def websocket_endpoint(websocket: WebSocket, subject_name):
    await websocket.accept()
    
    while client.IsConnected and client.GetFrame():
        data1 = get_data(client, "marker", "HWD")
        await websocket.send_json(data1)
        data = get_data(client, "marker", "right")
        await websocket.send_json(data)
        await asyncio.sleep(tick_rate)  

def get_vicon_instance(connection=None):
    if connection is None:
        connection = 'localhost:801'
    client = ViconDataStream.Client()

    while not client.IsConnected():
        client.Connect(connection)
    client.SetStreamMode(ViconDataStream.Client.StreamMode.EClientPull)
    client.EnableSegmentData()
    client.EnableMarkerData()
    client.GetAxisMapping()
    return client

def get_data(client: ViconDataStream.Client, data_type, subject_name):
    data = {}

    if data_type == "marker":
        marker_segment_data = {}
        marker_data = {}
        print(client.GetLatencyTotal(), subject_name, client.GetFrameNumber())
        for marker, segment in client.GetMarkerNames(subject_name):
            try:
                marker_segment_data[segment].append(marker)
            except KeyError:
                marker_segment_data[segment] = [marker]
            marker_data[marker] = client.GetMarkerGlobalTranslation(subject_name, marker)[0]
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
    #_init_api('localhost:801', defaultHost, defaultPort, False)
    client = get_vicon_instance()
    
    uvicorn.run(app, host = defaultHost, port = defaultPort)