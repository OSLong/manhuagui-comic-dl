import argparse
import sys
# from app import ebook_merger_app
from app import ebook_merger_app_v2
from textual import log

def _init_parser(parser: argparse.ArgumentParser):
    # parser.add_argument('-t', '--test')
    parser.add_argument(
        '-d', '--directory', 
        help='Epub Directory',
        required=True,
        type=str
    )
    parser.add_argument(
        '-od', '--output-dir', 
        help='Epub Directory',
        default='./',
        type=str
    )
    pass

def main(args):
    parser = argparse.ArgumentParser()
    _init_parser(parser=parser)
    opts = parser.parse_args(args=args)

    # app = ebook_merger_app.EbookMergerApp(opts)
    app = ebook_merger_app_v2.EbookMergerAppV2(opts)
    app.run()



if __name__ == '__main__':
    main(sys.argv)