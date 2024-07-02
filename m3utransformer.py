from structurizer import Stream, ChannelGroup

class M3UTransformer:
    def __init__(self, output_file: str):
        self.output_file = output_file

    def save_to_file(self, data: list[Stream]) -> None:
        with open(self.output_file, "w") as f:
            f.write(self.transform(data))

    def transform(self, data: list[Stream]) -> str:
        m3u = "#EXTM3U\n"

        for stream in data:
            if len(stream.channel_group.categories) > 0:
                category = stream.channel_group.categories[0]
            else:
                category = "undefined"
            m3u += f"#EXTINF:-1 tvg-id=\"{stream.channel}\" tvg-logo=\"{stream.channel_group.logo}\" group-title=\"{category}\", {stream.channel_group.name}\n"
            m3u += f"{stream.url}\n"

        return m3u