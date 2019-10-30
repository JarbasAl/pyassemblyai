import requests
import base64
from time import sleep


class AssemblyAI:
    stream_api_url = 'https://api.assemblyai.com/v2/stream'
    transcribe_api_url = "https://api.assemblyai.com/v2/transcript"
    upload_api_url = 'https://api.assemblyai.com/v2/upload'

    def __init__(self, api_token, wait_time=1):
        self.token = api_token
        self.wait_time = wait_time

    @staticmethod
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    def upload_file(self, filename, raw=False):
        assert filename.endswith(".wav")
        headers = {'authorization': self.token}
        response = requests.post(self.upload_api_url,
                                 headers=headers,
                                 data=self.read_file(filename)).json()
        if raw:
            return response
        if response.get("error"):
            return response["error"]
        return response['upload_url']

    def upload_audiodata(self, data, raw=False):
        headers = {'authorization': self.token}
        response = requests.post(self.upload_api_url,
                                 headers=headers,
                                 data=data)
        if raw:
            return response.json()
        return response.json()['upload_url']

    def transcribe_url(self, url, raw=False):
        payload = "{\"audio_url\": \"" + url + "\"}"
        headers = {
            'authorization': self.token,
            'content-type': "application/json"
        }

        response = requests.request("POST", self.transcribe_api_url,
                                    data=payload, headers=headers).json()
        if raw:
            return response
        if response.get("error"):
            return response["error"]
        return response["id"]

    def get_transcript(self, transcript_id, raw=False):
        url = self.transcribe_api_url + "/" + transcript_id

        headers = {
            'authorization': self.token,
            'content-type': "application/json"
        }

        response = requests.request("GET", url, headers=headers).json()
        if raw:
            return response
        while response["status"] != "completed":
            if response.get("error"):
                return response["error"]
            response = self.get_transcript(transcript_id, raw=True)
        return response["text"]

    def transcribe_file(self, filename, raw=False):
        url = self.upload_file(filename)
        transcript_id = self.transcribe_url(url)
        if raw:
            transcript = self.get_transcript(transcript_id["id"], raw=True)
            while transcript["status"] != "completed":
                sleep(self.wait_time)
                transcript = self.get_transcript(transcript_id, raw=True)
            return transcript
        return self.get_transcript(transcript_id)

    def transcribe_audiodata(self, data, raw=False):
        url = self.upload_audiodata(data)
        transcript_id = self.transcribe_url(url)
        if raw:
            transcript = self.get_transcript(transcript_id, raw=True)
            if transcript.get("error"):
                return transcript["error"]
            while transcript["status"] != "completed":
                sleep(self.wait_time)
                transcript = self.get_transcript(transcript_id, raw=True)
            return transcript
        return self.get_transcript(transcript_id)

    def stream_file(self, filename, word_boost=None, boost_param="default", raw=False):
        """
        Include the "word_boost": ["foo", "cancel my plan"] parameter to
        boost the likelihood of keywords/phrases important for your application.

        You can also set the parameter "boost_param" to "low" "default" or "high" to
        control the weight applied to the words/phrases in your "word_boost" list.

        Each string in your array must be between 1-6 words, and your array
        can only contain up to 150 words/phrases for now.
        Enabling this feature may have a small impact on latency (which grows the bigger the list is).
        """
        # read the binary data from a wav file
        with open(filename, 'rb') as _in:
            # strip off wav headers
            data = _in.read()
        return self.stream_audiodata(data, word_boost, boost_param, raw)

    def stream_audiodata(self, data, word_boost=None, boost_param="default", raw=False):
        """
        Include the "word_boost": ["foo", "cancel my plan"] parameter to
        boost the likelihood of keywords/phrases important for your application.

        You can also set the parameter "boost_param" to "low" "default" or "high" to
        control the weight applied to the words/phrases in your "word_boost" list.

        Each string in your array must be between 1-6 words, and your array
        can only contain up to 150 words/phrases for now.
        Enabling this feature may have a small impact on latency (which grows the bigger the list is).
        """
        assert boost_param in ["low", "default", "high"]
        headers = {'authorization': self.token}
        # strip off wav headers
        data = data[44:]
        # base64 encode the binary data so it
        # can be included as a JSON parameter
        data = base64.b64encode(data)
        # send the data to the /v2/stream endpoint
        json_data = {'audio_data': data.decode("utf-8")}
        if word_boost:
            json_data["word_boost"] = word_boost
            json_data["boost_param"] = boost_param
        response = requests.post(self.stream_api_url, json=json_data, headers=headers).json()
        if raw:
            return response
        if response.get("error"):
            return response["error"]
        return response["text"]


if __name__ == "__main__":
    key = "xxx"
    filepath = "/home/user/data/synthetic_data/data/en/lights_off/lights_off-Salli-strong_low_pitch-polly.wav"
    engine = AssemblyAI(key)
    # the automatic way

    transcript = engine.stream_file(filepath, raw=True)

    transcript = engine.transcribe_file(filepath)

    # you can send wav data directly, i.e. from microphone
    with open(filepath, "rb") as f:
        data = f.read()
    transcript_data = engine.transcribe_audiodata(data, raw=True)
    print(transcript_data)

    # the semi automatic way
    url = engine.upload_file(filepath)
    print(url)
    transcript_id = engine.transcribe_url(url)
    print(transcript_id)
    transcript = engine.get_transcript(transcript_id)
    print(transcript)

    # the raw way for full control
    url = engine.upload_file(filepath, raw=True)
    print(url)
    transcript_id = engine.transcribe_url(url['upload_url'], raw=True)
    print(transcript_id)
    transcript = engine.get_transcript(transcript_id["id"], raw=True)
    while transcript["status"] != "completed":
        transcript = engine.get_transcript(transcript_id["id"], raw=True)
        print(transcript)
    print(transcript["text"])
