from fastapi import FastAPI, WebSocket
from datetime import datetime

import sys
import json
import msgpack
import pandas as pd
from pathlib import Path
from datetime import datetime

from flask import Flask, send_file, make_response
from flask_restful import Resource, Api
from loguru import logger
from alive_progress import alive_bar

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
tick_rate = 0.01

#Runs every tick rate
@app.websocket("/marker/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while client.IsConnected and client.GetFrame():
        data = get_data(client, "marker")
        await websocket.send_json(data)
        await asyncio.sleep(tick_rate)  

def get_vicon_instance(connection=None):
    if connection is None:
        connection = 'localhost:801'
    client = ViconDataStream.Client()

    while not client.IsConnected():
        client.Connect(connection)
    client.SetStreamMode(ViconDataStream.Client.StreamMode.EClientPullPreFetch)
    client.EnableSegmentData()
    client.EnableMarkerData()
    client.GetAxisMapping()
    return client

def get_data(client: ViconDataStream.Client, data_type: str):
        
    if data_type == "marker":
        
        stream = {}
        for subject_name in client.GetSubjectNames():
            data = {}
            marker_segment_data = {}
            marker_data = {}
            print(f"{subject_name} : {client.GetLatencyTotal()} : {client.GetFrameNumber()}")
            for marker, segment in client.GetMarkerNames(subject_name):
                try:
                    marker_segment_data[segment].append(marker)
                except KeyError:
                    marker_segment_data[segment] = [marker]
                marker_data[marker] = client.GetMarkerGlobalTranslation(subject_name, marker)[0]
            data['data'] = marker_data
            data['hierachy'] = marker_segment_data
            stream[subject_name] = data
            

        
    elif data_type == "segment":
        segment_data = {}
        for segment in client.GetSegmentNames(subject_name):
            translation, status = client.GetSegmentGlobalTranslation(subject_name, segment)
            rotation, status = client.GetSegmentGlobalRotationQuaternion(subject_name, segment)
            segment_data[segment] = translation + rotation
        data['data'] = segment_data
            
    return stream




if __name__ == "__main__":
    #_init_api('localhost:801', defaultHost, defaultPort, False)
    client = get_vicon_instance()
    
    uvicorn.run(app, host = defaultHost, port = defaultPort)
