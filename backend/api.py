
# REFERENCE:
# https://github.com/googleapis/python-video-live-stream/blob/502ba94ba8f6e1fead910732b810cee0526bf71b/samples/snippets

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud.video import live_stream_v1
from google.cloud.video.live_stream_v1.services.livestream_service import (
    LivestreamServiceClient,
)
from google.protobuf import duration_pb2 as duration
import os

from pydantic import BaseModel


# Constants
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
PROJECT_ID = ""
LOCATION = ""
PROJECT_NUMBER = ""
OPERATION_ID = ""


# STEP 1 : CREATE AN INPUT ENDPOINT
client = LivestreamServiceClient()


def create_channel(
    project_id: str, location: str, channel_id: str, input_id: str, output_uri: str
) -> str:
    """Creates a channel.
    Args:
        project_id: The GCP project ID.
        location: The location in which to create the channel.
        channel_id: The user-defined channel ID.
        input_id: The user-defined input ID.
        output_uri: Uri of the channel output folder in a Cloud Storage bucket."""

    parent = f"projects/{project_id}/locations/{location}"
    input = f"projects/{project_id}/locations/{location}/inputs/{input_id}"
    name = f"projects/{project_id}/locations/{location}/channels/{channel_id}"

    channel = live_stream_v1.types.Channel(
        name=name,
        input_attachments=[
            live_stream_v1.types.InputAttachment(
                key="my-input",
                input=input,
            ),
        ],
        output=live_stream_v1.types.Channel.Output(
            uri=output_uri,
        ),
        elementary_streams=[
            live_stream_v1.types.ElementaryStream(
                key="es_video",
                video_stream=live_stream_v1.types.VideoStream(
                    h264=live_stream_v1.types.VideoStream.H264CodecSettings(
                        profile="high",
                        width_pixels=1280,
                        height_pixels=720,
                        bitrate_bps=3000000,
                        frame_rate=30,
                    ),
                ),
            ),
            live_stream_v1.types.ElementaryStream(
                key="es_audio",
                audio_stream=live_stream_v1.types.AudioStream(
                    codec="aac", channel_count=2, bitrate_bps=160000
                ),
            ),
        ],
        mux_streams=[
            live_stream_v1.types.MuxStream(
                key="mux_video",
                elementary_streams=["es_video"],
                segment_settings=live_stream_v1.types.SegmentSettings(
                    segment_duration=duration.Duration(
                        seconds=2,
                    ),
                ),
            ),
            live_stream_v1.types.MuxStream(
                key="mux_audio",
                elementary_streams=["es_audio"],
                segment_settings=live_stream_v1.types.SegmentSettings(
                    segment_duration=duration.Duration(
                        seconds=2,
                    ),
                ),
            ),
        ],
        manifests=[

            live_stream_v1.types.Manifest(
                file_name="main.mpd",
                type_="DASH",
                mux_streams=["mux_video", "mux_audio"],
                max_segment_count=5,
            ),
        ],
    )
    operation = client.create_channel(
        parent=parent, channel=channel, channel_id=channel_id
    )
    response = operation.result(600)
    print(f"Channel: {response.name}")

    return response


def create_input(project_id: str, location: str, input_id: str) -> str:
    parent = f"projects/{project_id}/locations/{location}"

    input = live_stream_v1.types.Input(
        type_="RTMP_PUSH",
    )
    operation = client.create_input(
        parent=parent, input=input, input_id=input_id)
    response = operation.result(900)
    ob = {
        "name": response.name,
        "type_enum": response.type_,
        "type": response.Type(response.type_.value).name,
        "tier_enum": response.tier,
        "tier": response.Tier(response.tier.value).name,
        "uri": response.uri
    }

    return ob


def create_channel_event(
    project_id: str, location: str, channel_id: str, event_id: str
) -> str:
    """Creates a channel event.
    Args:
        project_id: The GCP project ID.
        location: The location of the channel.
        channel_id: The user-defined channel ID.
        event_id: The user-defined event ID."""

    parent = f"projects/{project_id}/locations/{location}/channels/{channel_id}"
    name = f"projects/{project_id}/locations/{location}/channels/{channel_id}/events/{event_id}"

    event = live_stream_v1.types.Event(
        name=name,
        ad_break=live_stream_v1.types.Event.AdBreakTask(
            duration=duration.Duration(
                seconds=30,
            ),
        ),
        execute_now=True,
    )

    response = client.create_event(
        parent=parent, event=event, event_id=event_id)
    print(f"Channel event: {response.name}")

    return response


# FIXME: API CODE START
app = FastAPI()
origins = [
    "*"
]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)


@app.get("/")
async def root():
    return {"status": "RUNNING"}


class CreateInputEndpoint(BaseModel):
    input_id: str


@app.post("/create/endpoint", status_code=200)
async def create_input_endpoint(endpoint: CreateInputEndpoint):
    response = create_input(project_id=PROJECT_ID, location=LOCATION,
                            input_id=endpoint.input_id)
    return {"endpoint": response}


@app.delete("/delete/endpoints/{input_id}", status_code=200)
async def delete_endpoint(input_id):
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/inputs/{input_id}"
    operation = client.delete_input(name=name)
    operation.result(600)
    return {"status": "DELETED", "input_id": input_id}


@app.get("/list/endpoints", status_code=200)
async def list_input_endpoints():
    request = live_stream_v1.ListInputsRequest(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}")
    page_result = client.list_inputs(request=request)
    res = []
    for response in page_result:
        ob = {
            "name": response.name,
            "type_enum": response.type_,
            "type": response.Type(response.type_.value).name,
            "tier_enum": response.tier,
            "tier": response.Tier(response.tier.value).name,
            "uri": response.uri
        }
        res.append(ob)
    return res


class CreateChannel(BaseModel):
    channel_id: str
    input_id: str
    output_uri: str


@app.post("/create/channel", status_code=200)
async def create_channel_endpoint(channel: CreateChannel):
    response = create_channel(project_id=PROJECT_ID, location=LOCATION,
                              channel_id=channel.channel_id,
                              input_id=channel.input_id,
                              output_uri=channel.output_uri)

    return {"status": "CREATED CHANNEL", "response": response.name}


@app.delete("/delete/channels/{channel_id}", status_code=200)
async def delete_channel(channel_id):
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/channels/{channel_id}"
    operation = client.delete_channel(name=name)
    operation.result(600)
    return {"status": "DELETED", "channel_id": channel_id}


class ChannelEvent(BaseModel):
    channel_id: str
    event_id: str


@app.post("/create/channel/event", status_code=200)
async def channel_event(item: ChannelEvent):
    response = create_channel_event(
        project_id=PROJECT_ID, location=LOCATION, channel_id=item.channel_id, event_id=item.event_id)
    return {"status": "INSERTED EVENT", "response": response.name}


def start_channel(project_id: str, location: str, channel_id: str) -> None:
    """Starts a channel.
    Args:
        project_id: The GCP project ID.
        location: The location of the channel.
        channel_id: The user-defined channel ID."""

    name = f"projects/{project_id}/locations/{location}/channels/{channel_id}"
    operation = client.start_channel(name=name)
    operation.result(900)
    print("channel started")
    return {"status": "CHANNEL STARTED"}


@app.get("/channel/{channel_id}/start", status_code=200)
async def startChannel(channel_id):
    response = start_channel(project_id=PROJECT_ID,
                             location=LOCATION, channel_id=channel_id)
    return response


def stop_channel(project_id: str, location: str, channel_id: str) -> None:

    name = f"projects/{project_id}/locations/{location}/channels/{channel_id}"
    operation = client.stop_channel(name=name)
    operation.result(600)
    print("Stopped channel")
    return {"status": "CHANNEL STOPPED"}


@app.get("/channel/{channel_id}/stop", status_code=200)
async def stopChannel(channel_id):
    response = stop_channel(project_id=PROJECT_ID,
                            location=LOCATION, channel_id=channel_id)
    return response


def list_channels(project_id: str, location: str) -> list:

    parent = f"projects/{project_id}/locations/{location}"
    page_result = client.list_channels(parent=parent)
    print("Channels:")

    responses = []
    for response in page_result:
        print(response.name)
        responses.append(response.name)

    return responses


@app.get("/list/channels", status_code=200)
async def listChannels():
    response = list_channels(project_id=PROJECT_ID, location=LOCATION)
    return response


def get_channel(project_id: str, location: str, channel_id: str) -> str:
    """Gets a channel.
    Args:
        project_id: The GCP project ID.
        location: The location of the channel.
        channel_id: The user-defined channel ID."""

    client = LivestreamServiceClient()

    name = f"projects/{project_id}/locations/{location}/channels/{channel_id}"
    response = client.get_channel(name=name)
    print(f"Channel: {response}")

    return {"name": response.name, "state_enum": response.streaming_state, "state": live_stream_v1.Channel.StreamingState(response.streaming_state.value).name}


@app.get("/channels/{channel_id}", status_code=200)
async def getChannel(channel_id):
    response = get_channel(project_id=PROJECT_ID,
                           location=LOCATION, channel_id=channel_id)
    return response


# FIXME: API CODE END
