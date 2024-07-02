import requests
from structurizer import Stream, ChannelGroup


class Validator:
    def __init__(
        self,
        timeout: int,
        allowed_languages: list,
        allowed_broadcast_areas: list,
        banned_endings: list,
        forced_endings: list,
        verbose: bool,
    ):
        self.timeout = timeout
        self.allowed_languages = allowed_languages
        self.allowed_broadcast_areas = allowed_broadcast_areas
        self.banned_endings = banned_endings
        self.forced_endings = forced_endings
        self.verbose = verbose

    def parse_validated(self, merged_data: list[Stream]) -> list[Stream]:
        validated = []

        for stream in merged_data:
            if self._check_empty_channel(stream) \
                    and self._check_banned_endings(stream) \
                and self._check_channel_group(stream) \
                    and (
                    self._check_language(stream)
                    or self._check_broadcast_area(stream)
                    or self._check_forced_endings(stream)):
                validated.append(stream)
                merged_data.remove(stream)

        if self.timeout is not None and self.timeout > 0:
            self._patch_timeout()
            for valid in validated:
                if not self._is_alive(valid.url):
                    validated.remove(valid)

        return validated

    def _check_empty_channel(self, stream: Stream) -> bool:
        return stream.channel != ""

    def _check_channel_group(self, stream: Stream) -> bool:
        return stream.channel_group is not None

    def _check_language(self, stream: Stream) -> bool:
        if self.allowed_languages is None:
            return False

        if stream.channel_group.languages is not None:
            for language in stream.channel_group.languages:
                if language in self.allowed_languages:
                    return True

        return False

    def _check_broadcast_area(self, stream: Stream) -> bool:
        if self.allowed_broadcast_areas is None:
            return False

        if stream.channel_group.broadcast_area is not None:
            for area in stream.channel_group.broadcast_area:
                if area in self.allowed_broadcast_areas:
                    return True

        return False

    def _check_banned_endings(self, stream: Stream) -> bool:
        if self.banned_endings is None:
            return False

        for banned_ending in self.banned_endings:
            if stream.channel.endswith(banned_ending):
                return False

        return True

    def _check_forced_endings(self, stream: Stream) -> bool:
        if self.forced_endings is None:
            return False

        for forced_ending in self.forced_endings:
            if stream.channel.endswith(forced_ending):
                return True

        return False

    def _patch_timeout(self):
        import platform
        import socket
        import urllib3.connection

        platform_name = platform.system()
        orig_connect = urllib3.connection.HTTPConnection.connect

        def patch_connect(self):
            orig_connect(self)
            if platform_name == "Linux" or platform_name == "Windows":
                self.sock.setsockopt(
                    socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                self.sock.setsockopt(socket.IPPROTO_TCP,
                                     socket.TCP_KEEPIDLE, 1),
                self.sock.setsockopt(socket.IPPROTO_TCP,
                                     socket.TCP_KEEPINTVL, 3),
                self.sock.setsockopt(socket.IPPROTO_TCP,
                                     socket.TCP_KEEPCNT, 5),
            elif platform_name == "Darwin":
                TCP_KEEPALIVE = 0x10
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, 3)

        urllib3.connection.HTTPConnection.connect = patch_connect

    def _is_alive(self, stream: str) -> bool:
        r = None
        try:
            r = requests.get(stream, timeout=self.timeout, stream=True)
            r.raise_for_status()
            if self.verbose:
                print(f"Stream {stream} is alive.")
            r.close()

            return True
        except requests.exceptions.HTTPError as errh:
            if self.verbose:
                print(f"Stream {stream} is dead. Http Error: {str(errh)}")
        except requests.exceptions.ConnectionError as errc:
            if self.verbose:
                print(f"Stream {stream} is dead. Error Connecting: {str(errc)}")
        except requests.exceptions.Timeout as errt:
            if self.verbose:
                print(f"Stream {stream} is dead. Timeout Error: {str(errt)}")
        except Exception as e:
            if self.verbose:
                print(f"Stream {stream} is dead. Error: {str(e)}")
        
        if r is not None:
            r.close()
        return False
