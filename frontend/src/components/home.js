import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import ReactPlayer from "react-player";

const BASE_URL = "http://localhost:8000/";
const STREAM_URL = ""; //Find this file inside the gcs directory and copy the Public URL. You would need the same in future.

export default function Home() {
  const [endpoint, setEndpoint] = useState("");
  const [channel, setChannel] = useState("");
  const [gcs_storage_uri, setGCSUri] = useState("");
  const [response, setResponseData] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    console.log(response);
  }, [response]);

  return (
    <div>
      <div className="flex flex-row">
        <div className="w-6/12">
          <div className="flex space-x-10">
            <input
              type="text"
              id="endpoint_name"
              onChange={(e) => setEndpoint(e.target.value)}
              class="bg-gray-50 mb-10 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-6/12 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="Input Endpoint Name"
              required
            />
            <input
              type="text"
              id="channel_name"
              onChange={(e) => setChannel(e.target.value)}
              class="bg-gray-50 border mb-10 border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-6/12 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="Input Channel Name"
              required
            />
            <input
              type="text"
              id="storage_gcs_uri"
              onChange={(e) => setGCSUri(e.target.value)}
              class="bg-gray-50 border mb-10 border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-8/12 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="Storage GCS URI (gs://<bucket_name>)"
              required
            />
          </div>
          <div className="space-y-5 space-x-5 flex ">
            <button
              onClick={() => createInputEndpoint()}
              className="bg-white w-6/12  hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 1 <br /> Create Input Endpoint
            </button>
          </div>

          <br />
          <div className="space-y-5 space-x-5">
            <button
              onClick={() => listEndpoints()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 2 <br /> List Endpoints
            </button>
          </div>
          <br />
          <div className="space-y-5 space-x-5">
            <button
              onClick={() => createChannel()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 3 <br /> Create Channel
            </button>
          </div>
          <br />
          <div className="space-y-5 space-x-5">
            <button
              onClick={() => listChannels()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 4 <br /> List Channels
            </button>
          </div>
          <br />
          <div className="space-y-5 space-x-5">
            <button
              onClick={() => startChannel()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 5 <br /> Start Channel & Start OBS (stream the input)
            </button>
          </div>
          <br />
          <div className="space-y-5 space-x-5">
            <button
              onClick={() => stopChannel()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 6 <br /> Stop Channel
            </button>
          </div>
          <br />
          <div className="space-y-5 space-x-5">
            <button
              onClick={() => deleteChannel()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 7 <br /> Delete Channel
            </button>
          </div>
          <div className="space-y-10 mt-5 space-x-5">
            <button
              onClick={() => deleteEndpoint()}
              className="bg-white w-6/12 hover:bg-orange-400 rounded-lg px-2 py-2 font-semibold text-black hover:text-black-500"
            >
              Step 8 <br /> Delete Input Endpoint
            </button>
          </div>
        </div>

        <div className="w-6/12 mt-20 mr-4 ">
          <h3 className="text-amber-400 font-semibold p-3">JSON Output</h3>
          {loading ? (
            <pre className="text-white w-3/6 ">Loading Response...</pre>
          ) : (
            <pre className="text-white json-format bg-slate-500 rounded-md text-m p-4">
              {JSON.stringify(response, null, 2)}
            </pre>
          )}
          <h3 className="text-amber-400 font-semibold p-3">
            Livestream Video Player
          </h3>
          <ReactPlayer
            url={STREAM_URL}
            config={{
              file: {
                attributes: {
                  crossOrigin: "true",
                },
              },
            }}
            controls={true}
            height={512}
            width={720}
          />
        </div>
      </div>
    </div>
  );

  async function createInputEndpoint() {
    var payload = {
      input_id: endpoint,
    };
    setLoading(true);
    try {
      var response = await axios.post(BASE_URL + "create/endpoint", payload);
      console.log(
        "🚀 ~ file: home.js:94 ~ createInputEndpoint ~ response:",
        response.data
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }
  async function createChannel() {
    var payload = {
      channel_id: channel,
      input_id: endpoint,
      output_uri: gcs_storage_uri,
    };
    setLoading(true);
    try {
      var response = await axios.post(BASE_URL + "create/channel", payload);
      console.log(
        "🚀 ~ file: home.js:108 ~ createChannel ~ response:",
        response.data
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }

  async function startChannel() {
    setLoading(true);
    try {
      var response = await axios.get(
        BASE_URL + "channel/" + channel + "/start"
      );
      console.log(
        "🚀 ~ file: home.js:128 ~ startChannel ~ response:",
        response.data
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }

  async function listEndpoints() {
    setLoading(true);
    try {
      var response = await axios.get(BASE_URL + "list/endpoints");
      console.log(
        "🚀 ~ file: home.js:197 ~ listEndpoints ~ response:",
        response
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }

  async function listChannels() {
    setLoading(true);
    try {
      var response = await axios.get(BASE_URL + "list/channels");
      console.log(
        "🚀 ~ file: home.js:197 ~ listChannels ~ response:",
        response
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }

  async function stopChannel() {
    setLoading(true);
    try {
      var response = await axios.get(BASE_URL + "channel/" + channel + "/stop");
      console.log(
        "🚀 ~ file: home.js:138 ~ stopChannel ~ response:",
        response.data
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }

  async function deleteChannel() {
    setLoading(true);
    try {
      var response = await axios.delete(
        BASE_URL + "delete/channels/" + channel
      );
      console.log(
        "🚀 ~ file: home.js:148 ~ deleteChannel ~ response:",
        response.data
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }
  async function deleteEndpoint() {
    setLoading(true);
    try {
      var response = await axios.delete(
        BASE_URL + "delete/endpoints/" + endpoint
      );
      console.log(
        "🚀 ~ file: home.js:155 ~ deleteEndpoint ~ response:",
        response.data
      );
      setResponseData(response.data);
      setLoading(false);
    } catch (error) {
      handleError(error);
    }
  }
  function setResponseAndLoading(setResponseData, response, setLoading) {}
  function handleError(error) {
    console.log("Error", error);
    setResponseData({ error: error.message });
    setLoading(false);
  }
}
