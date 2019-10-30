# PyAssemblyAI

I did not notice an official sdk exists - https://github.com/AssemblyAI/assemblyai-python-sdk

repo is now archived


________________________________

python api for [AssemblyAI](https://www.assemblyai.com/)

# install

    pip install pyassemblyai
    
# usage

```python
from pyassemblyai import AssemblyAI

key = "xxxx"
filepath = "some_speech.wav"
engine = AssemblyAI(key)

# the automatic way
transcript = engine.stream_file(filepath)  # Paid

transcript = engine.transcribe_file(filepath) # text string

print(transcript)

# you can also send wav data directly, i.e. from microphone
with open(filepath, "rb") as f:
    data = f.read()
transcript_data = engine.transcribe_audiodata(data, raw=True) # json


# the semi automatic way
url = engine.upload_file(filepath) # string
print(url)
transcript_id = engine.transcribe_url(url) # string
print(transcript_id)
transcript = engine.get_transcript(transcript_id) # string
print(transcript)

# the raw way for full control
# NOTE no error checking, always check for "error" key in json
url = engine.upload_file(filepath, raw=True)
print(url)
transcript_id = engine.transcribe_url(url['upload_url'], raw=True)
print(transcript_id)
transcript = engine.get_transcript(transcript_id["id"], raw=True)
while transcript["status"] != "completed":
    transcript = engine.get_transcript(transcript_id["id"], raw=True)
    print(transcript)
print(transcript["text"])

```
