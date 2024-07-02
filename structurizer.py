import json
import datetime


class ChannelGroup:
    def __init__(
        self,
        id: str,
        name: str,
        country: str,
        broadcast_area: list[str],
        languages: list[str],
        categories: list[str],
        is_nsfw: bool,
        logo: str,
    ):
        self.id = id
        self.name = name
        self.country = country
        self.broadcast_area = broadcast_area
        self.languages = languages
        self.categories = categories
        self.is_nsfw = is_nsfw
        self.logo = logo

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "broadcast_area": self.broadcast_area,
            "languages": self.languages,
            "categories": self.categories,
            "is_nsfw": self.is_nsfw,
            "logo": self.logo
        }

    def from_dict(data: dict):
        return ChannelGroup(
            data["id"],
            data["name"],
            data["country"],
            data["broadcast_area"],
            data["languages"],
            data["categories"],
            data["is_nsfw"],
            data["logo"]
        )


class Stream:
    def __init__(
        self,
        channel: str,
        url: str,
        channel_group: ChannelGroup
    ):
        self.channel = channel
        self.url = url
        self.channel_group = channel_group

    def to_dict(self):
        return {
            "channel": self.channel,
            "url": self.url,
            "channel_group": self.channel_group.to_dict()
        }

    def from_dict(data: dict):
        return Stream(
            data["channel"],
            data["url"],
            ChannelGroup.from_dict(data["channel_group"])
        )


class Structurizer:
    def __init__(self, filedir: str, merge: bool):
        self.filedir = filedir
        self.merge = merge

    def get_data(self):
        if self.merge:
            print('Merging streams and channels data...')
            start = datetime.datetime.now()
            self._merge()
            print(f'Merging done in {datetime.datetime.now() - start}')

        return self.get_merged()

    def _merge(self):
        streams = self._streams()
        channels = self._channels()

        merged = []

        for stream in streams:
            for channel in channels:
                if stream["channel"] == channel["id"]:
                    stream['channel_group'] = channel
                    merged.append(Stream.from_dict(stream))

        self._save_merged(merged)

    def _save_merged(self, data: list[Stream]):
        with open(f"{self.filedir}/merged.json", "w") as f:
            f.write(json.dumps([stream.to_dict()
                    for stream in data], indent=4))

    def _streams(self):
        with open(f"{self.filedir}/streams.json", "r") as f:
            return json.load(f)

    def _channels(self):
        with open(f"{self.filedir}/channels.json", "r") as f:
            return json.load(f)

    def get_merged(self) -> list[Stream]:
        with open(f"{self.filedir}/merged.json", "r") as f:
            return [Stream.from_dict(stream) for stream in json.load(f)]
