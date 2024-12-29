
import sys
import argparse

from mhg.comic import Comic, Chapter
from mhg.chapter_type import CHAPTER_TYPE
import datetime

def _init_parser(parser):
    parser.add_argument(
        '-i', '--comic-id',
          type=str,
          required=True, 
          help='manhuagui comic id',
    )
    parser.add_argument(
        '--include-volume', 
        help='Download Volume ',
        type=bool,
        nargs='?',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--include-extra', 
        help='Download Extra ',
        type=bool,
        nargs='?',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--include-episode', 
        help='Download Episode ',
        type=bool,
        nargs='?',
        const=True,
        default=False,
    )
    parser.add_argument(
        '--include-undefined', 
        help='Download Undefined Type ',
        type=bool,
        nargs='?',
        const=True,
        default=False,
    )

    parser.add_argument(
        '--export-to-epub', 
        help='Export to Epub',
        type=bool,
        nargs='?',
        const=True,
        default=False,
    )

    parser.add_argument(
        '--use-sample', 
        help='Use Jigokuraku Sample to download , Currently , i on test about Ebook Export , so no need call to manhuagui.',
        type=bool,
        nargs='?',
        const=True,
        default=False,
    )

    parser.add_argument(
        '--start-from', 
        help='Start From Chapters',
        type=int,
        default=1
    )


def main(args):
    parser = argparse.ArgumentParser(
        prog='python main.py',
        description="Manhuagui Comic Downloader",
    )

    _init_parser(parser=parser)


    opts = parser.parse_args(args)
    
    comic = Comic(opts)
    comic.process()


    # comic.comic_name = 'Hello world'
    # chapter = Chapter(
    #     comic=comic,
    #     name='Chapter 1',
    #     type=CHAPTER_TYPE.VOLUME,
    #     page_count=10,
    #     url='https://tw.manhuagui.com/comic/27739/529325.html'
    # )
    # chapter.process()

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print('Start at : ', str(start_time))

    main(sys.args)
    
    end_time = datetime.datetime.now()
    print("End at : ", str(end_time))
    print("Elapsed : ", str(end_time - start_time))
    