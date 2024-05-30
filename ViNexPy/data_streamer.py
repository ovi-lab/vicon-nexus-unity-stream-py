import sys
import json
import msgpack
import os
from multiprocessing import Pool
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

def _init_api(connection=None, host="127.0.0.1", port="5000", use_json=False):
    try:
        global client
        client = get_client(connection)
    except Exception as e:
        print("Failed to connect to client")
        client = None   

    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "message": "Hello, this is a message",
            "timestamp": "Hello"
        }
        print("Executing")
        await websocket.send_json(get_data(client, "marker", "right"))
        await asyncio.sleep(0.001)  



    api.add_resource(ViconMarkerStream, '/<string:data_type>/<string:subject_name>')
    try:
        app.run(host=host, port=int(port))
    finally:
        pass

def get_client(connection=None):
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
    _init_api('localhost:801', '127.0.0.1', '5000', False)
    uvicorn.run(app, host="127.0.0.1", port=5000)