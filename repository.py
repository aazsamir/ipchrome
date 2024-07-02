import requests
import json

class Repository:
    def __init__(
            self,
            streams_url: str,
            channels_url: str,
            output_dir: str,
        ) -> None:
        self.streams_url = streams_url
        self.channels_url = channels_url
        self.output_dir = output_dir

    def get_streams(self):
        streams = requests.get(self.streams_url).json()
        with open(f"{self.output_dir}/streams.json", "w") as f:
            f.write(json.dumps(streams, indent=4))

    def get_channels(self):
        channels = requests.get(self.channels_url).json()
        with open(f"{self.output_dir}/channels.json", "w") as f:
            f.write(json.dumps(channels, indent=4))
