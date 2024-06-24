#!/usr/bin/env python

"""Main script."""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket
from loguru import logger

from vicon_nexus_unity_stream_py._utils import process_return_value

try:
    from vicon_dssdk import ViconDataStream
except ImportError:
    logger.error("Make sure vicon DataStreamSDK is installed: Follow the instructions in https://www.vicon.com/software/datastream-sdk/\n")
    #raise

app = FastAPI()
CLIENT = None
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5001

#parameters
TICK_RATE = 0.01

@app.websocket("/marker/")
async def websocket_endpoint(websocket: WebSocket):
    global CLIENT
    await websocket.accept()

    while CLIENT.IsConnected and CLIENT.GetFrame():
        data = get_data(CLIENT, "marker")
        await websocket.send_json(data)
        await asyncio.sleep(TICK_RATE)  


def get_vicon_instance(connection=None):
    """Returns the vicon client instance."""
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


def get_data(client: ViconDataStream.Client, data_type: str) -> dict:
    """Proces and return payload data from vicon client."""
    stream: dict[str, dict] = {}
    if data_type == "marker":
        for subject_name in client.GetSubjectNames():
            data = {}
            marker_segment_data = {}
            marker_data = {}
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
        for subject_name in client.GetSubjectNames():
            data = {}
            segment_data = {}
            for segment in client.GetSegmentNames(subject_name):
                translation, _ = client.GetSegmentGlobalTranslation(subject_name, segment)
                rotation, _ = client.GetSegmentGlobalRotationQuaternion(subject_name, segment)
                segment_data[segment] = translation + rotation
            data['data'] = segment_data
            stream[subject_name] = data
            
    processed_stream = process_return_value(stream)
    logger.info(f"Proccessed data / frame:{client.GetFrameNumber()} / subjects:" + str(list(stream.keys())))
    return processed_stream


def start_server(connection="localhost:801", host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Launch the server process"""
    global CLIENT
    CLIENT = get_vicon_instance(connection)

    uvicorn.run(app, host=host, port=port)


def test_connection(connection="localhost:801"):
    client = get_vicon_instance(connection)
    try:
        while client.IsConnected():
            if client.GetFrame():
                logger.info(get_data(client, 'test'))

    except ViconDataStream.DataStreamException as e:
        logger.error( f'Error: {e}' )


# TODO: revisit offline data processing
# LINES = []
# IDX = 0
# PLAY_MODE = False
# PLAY_INDEX = None
# PLAY_TS = None

# def _init_api_static(connection=None, host="127.0.0.1", port="5000", input_file=None, use_json=False):
#     app = Flask("vicon-ds")
#     api = Api(app)

#     if input_file is None or len(input_file) == 0:
#         logger.error("`input_file` cannot be empty")
#         return

#     _lines = []
#     with open(input_file) as f:
#         for l in f.readlines():
#             if len(l.strip()) == 0:
#                 continue
#             _lines.append(l.rstrip().split(",", maxsplit=1))

#     global LINES
#     LINES = pd.DataFrame(_lines)
#     LINES[1] = LINES[1].apply(lambda x: x if len(x) > 0 else None)
#     LINES = LINES.dropna()
#     LINES[0] = pd.to_numeric(LINES[0])

#     # TODO: better validation?
#     class ViconMarkerStreamProcess(Resource):
#         def _set_index(self, idx):
#             global IDX
#             if idx >= LINES.index.max():
#                 IDX = 0
#             elif idx < 0:
#                 IDX = int(LINES.index.max())
#             else:
#                 IDX = idx

#         def get(self, process=None, param=None):
#             ret_val = self._get(process, param)
#             return process_return_value(ret_val, use_json=True)

#         def _get(self, process=None, param=None):
#             global IDX, PLAY_MODE, PLAY_INDEX, PLAY_TS
#             if process is None or process == "index":
#                 return send_file(Path(__file__).parent / "static" / "index.html")
#             elif process == "n":
#                 self._set_index(IDX + 1)
#                 return IDX
#             elif process == "p":
#                 self._set_index(IDX - 1)
#                 return IDX
#             elif process == "s":
#                 if param is None:
#                     return "param cannot be empty. Use: /offline/s/<frame-number>", 404
#                 try:
#                     self._set_index(int(param))
#                     return IDX
#                 except:
#                     return "param should be a number. Use: /offline/s/<frame-number>", 404
#             elif process == "t":
#                 PLAY_MODE = not PLAY_MODE
#                 if PLAY_MODE:
#                     PLAY_INDEX = LINES.iloc[IDX, 0]
#                     PLAY_TS = datetime.now().timestamp()
#                 else:
#                     self._set_index(int(LINES[LINES.iloc[:, 0] == PLAY_INDEX].index[0]))
#                 return PLAY_MODE
#             return "Process not recognized. Available processes: offline/n  = Next, offline/p = Previous, offline/s/<frame-number> = jump to frame-number, offline/t = toggle play mode", 404

#     class ViconMarkerStream(Resource):
#         def get(self, data_type, subject_name):
#             ret_val = self._get(data_type, subject_name)
#             fpsDisplay.update(subject_name)
#             return process_return_value(ret_val, use_json)

#         def _get(self, data_type, subject_name):
#             global PLAY_INDEX, PLAY_TS
#             if subject_name == 'test':
#                 if PLAY_MODE:
#                     index = LINES.iloc[:, 0]
#                     diff = (index - PLAY_INDEX)
#                     min_val = index[diff > 0].min()
#                     ts = datetime.now().timestamp()
#                     if ts - PLAY_TS >= 0:
#                         PLAY_INDEX = min_val
#                         PLAY_TS = ts
#                     if min_val == index.max():
#                         PLAY_INDEX = index.min()
#                         PLAY_TS = datetime.now().timestamp()
#                     return json.loads(LINES[index == PLAY_INDEX].iloc[0, 1])
#                 else:
#                     return json.loads(LINES.iloc[IDX, 1])
#             return "Only works for subject `test`", 404

#     # api.add_resource(ViconMarkerStream, '/<string:data_type>/<string:subject_name>')
#     # api.add_resource(ViconMarkerStreamProcess, '/offline/<string:process>', '/offline/<string:process>/<string:param>', '/offline')
#     # print(f"Go to `http://{host}:{port}/offline/index` to access the web UI")
#     # app.run(host=host, port=int(port))
            
