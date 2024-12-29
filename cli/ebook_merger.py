import argparse
import sys

def _init_parser(parser: argparse.ArgumentParser):
    parser.add_argument('-t', '--test')
    pass

def main(args):
    parser = argparse.ArgumentParser()
    _init_parser(parser=parser)
    opts = parser.parse_args(args=args)

    

    pass

if __name__ == '__main__':
    main(sys.argv)