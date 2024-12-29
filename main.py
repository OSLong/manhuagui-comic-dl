import argparse
import sys
import cli.download as download_cli
import cli.ebook_merger as ebook_merger_cli

def main(args):
    parser = argparse.ArgumentParser()

    sub_parser = parser.add_subparsers(dest='command')

    download_parser = sub_parser.add_parser('download')
    download_cli._init_parser(download_parser)

    # ebook_merger_parser = sub_parser.add_parser('ebook-merger')
    # ebook_merger_cli._init_parser(ebook_merger_parser)

    opts = parser.parse_args()


    sub_args = args[1:]
    if opts.command == 'download':
        download_cli.main(sub_args)
    # elif opts.command == 'ebook-merger':
    #     ebook_merger_cli.main(sub_args)
    else: 
        parser.print_help()

if __name__ == '__main__':
    main(sys.argv[1:])