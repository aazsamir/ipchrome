import repository
import structurizer
import validator
import m3utransformer
import datetime
import argparse

STREAMS_URL = "https://iptv-org.github.io/api/streams.json"
CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"
OUTPUT_DIR = "./var"

class Args:
    def __init__(
            self,
            streams_url: str,
            channels_url: str,
            output_dir: str,
            fetch: bool,
            merge: bool,
            filter: bool,
            timeout: int,
            allowed_languages: list,
            allowed_broadcast_areas: list,
            banned_endings: list,
            forced_endings: list,
            verbose: bool,
        ):
        self.streams_url = streams_url
        self.channels_url = channels_url
        self.output_dir = output_dir
        self.fetch = fetch
        self.merge = merge
        self.filter = filter
        self.timeout = timeout
        self.allowed_languages = allowed_languages
        self.allowed_broadcast_areas = allowed_broadcast_areas
        self.banned_endings = banned_endings
        self.forced_endings = forced_endings
        self.verbose = verbose

    def create_from_parser_namespace(args: argparse.Namespace):
        return Args(
            streams_url=args.streams_url,
            channels_url=args.channels_url,
            output_dir=args.output_dir,
            fetch=args.fetch,
            merge=args.merge,
            filter=args.filter,
            timeout=args.timeout,
            allowed_languages=args.allowed_languages,
            allowed_broadcast_areas=args.allowed_broadcast_areas,
            banned_endings=args.banned_endings,
            forced_endings=args.forced_endings,
            verbose=args.verbose
        )

    def create_parser():
        parser = argparse.ArgumentParser(description='IPChrome')
        parser.add_argument('--fetch', 
            type=Args.str2bool,
            help='Fetch data or use existing data. Default: True',
            default=True
        )
        parser.add_argument('--streams_url',
            type=str,
            help='URL to streams data. Default: https://iptv-org.github.io/api/streams.json',
            default=STREAMS_URL
        )
        parser.add_argument('--channels_url',
            type=str,
            help='URL to channels data. Default: https://iptv-org.github.io/api/channels.json',
            default=CHANNELS_URL
        )
        parser.add_argument('--output_dir',
            type=str,
            help='Output directory. Default: ./var',
            default=OUTPUT_DIR
        )
        parser.add_argument('--merge',
            type=Args.str2bool,
            help='Merge streams and channels data. Default: True',
            default=True
        )
        parser.add_argument('--filter',
            type=Args.str2bool,
            help='Filter channels. Default: True',
            default=True
        )
        parser.add_argument('--timeout',
            type=int,
            help='Timeout in seconds. Default: 3s',
            default=3
        )
        parser.add_argument('--allowed_languages',
            nargs="+",
            type=str,
            help='Allowed languages. Default: None',
            default=None
        )
        parser.add_argument('--allowed_broadcast_areas',
            nargs="+",
            type=str,
            help='Allowed broadcast areas. Default: None',
            default=None
        )
        parser.add_argument('--banned_endings',
            nargs="+",
            type=str,
            help='Banned endings. Default: None',
            default=None
        )
        parser.add_argument('--forced_endings',
            nargs="+",
            type=str,
            help='Forced endings. Default: None',
            default=None
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output. Default: False',
            default=False
        )

        return parser
    
    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    
    def __str__(self):
        return f"[Args:\n\tfetch={self.fetch}\n\tstreams_url={self.streams_url}\n\tchannels_url={self.channels_url}\n\toutput_dir={self.output_dir}\n\tmerge={self.merge}\n\tfilter={self.filter}\n\ttimeout={self.timeout}\n\tallowed_languages={self.allowed_languages}\n\tallowed_broadcast_areas={self.allowed_broadcast_areas}\n\tbanned_endings={self.banned_endings}\n\tforced_endings={self.forced_endings}\n\tverbose={self.verbose}\n]"
    
def main(args: Args):
    print('====IPCHROME====')
    print(datetime.datetime.now().__str__())

    if args.fetch:
        print('Fetching data...')
        fetch_data(args)

    data = get_merged(args)
    
    if args.filter:
        print('Filtering data...')
        data = validate(args, data)

    print('Transforming to m3u...')

    m3utransform(data, args)


def fetch_data(args: Args):
    repo = repository.Repository(args.streams_url, args.channels_url, args.output_dir)

    try:
        repo.get_channels()
        repo.get_streams()
    except Exception as e:
        print('Error fetching data. Exiting...')
        if args.verbose:
            print(e)
        exit(1)

    return repo

def get_merged(args: Args):
    struct_service = structurizer.Structurizer(args.output_dir, args.merge)

    try:
        return struct_service.get_data()
    except Exception as e:
        print('Error merging data. Exiting...')
        if args.verbose:
            print(e)
        exit(1)

def validate(args: Args, data: list[structurizer.Stream]) -> list[structurizer.Stream]:
    validator_service = validator.Validator(
        args.timeout,
        args.allowed_languages,
        args.allowed_broadcast_areas,
        args.banned_endings,
        args.forced_endings,
        args.verbose
    )

    try:
        return validator_service.parse_validated(data)
    except Exception as e:
        print('Error validating data. Exiting...')
        if args.verbose:
            print(e)
        exit(1)

def m3utransform(data: list[structurizer.Stream], args: Args):
    outputfile = args.output_dir
    if not outputfile.endswith('/'):
        outputfile += '/'
    outputfile += 'output.m3u'
    try:
        m3u_transformer = m3utransformer.M3UTransformer(outputfile)
        m3u_transformer.save_to_file(data)
    except Exception as e:
        print('Error transforming data. Exiting...')
        if args.verbose:
            print(e)
        exit(1)

if __name__ == '__main__':
    parser = Args.create_parser()
    args = parser.parse_args()
    args = Args.create_from_parser_namespace(args)

    if args.verbose:
        print(args)

    main(args)