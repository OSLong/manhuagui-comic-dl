from glob import glob
from textual import log
import os
import re

class EbookMergerService():
    def __init__(self, opts):
        self.opts = opts

    def _extract_number_from_name(self, name):
        pattern = r'(\d+)'
        matched = re.findall(pattern, name)
        if matched:
            return matched[-1]
        return str(99999)

    def _list_epub_in_directory(self):
        
        # log("Run List =========1111========================" , dir(self))
        opts = self.opts

        # when use textual dev run 
        # it add singlequote before path 
        # cause error
        # 
        directory = opts.directory
        if directory.startswith("'") or directory.endswith("'"):
            directory = directory[1:-1]

        pattern = os.path.join(
            directory,
            '**',
            '*.epub',
        )
        # log("Found epub fiel si 111111111111s", directory, pattern)

        epub_files = glob(pattern,recursive=True)
        log("Found epub fiel si s", epub_files, directory, pattern)
        
        result  = []

        for file_path in epub_files:
            file_name = os.path.basename(file_path)
            sequence = self._extract_number_from_name(file_name)
            result += [
                {
                    'sequence': sequence,
                    'path': file_path,
                    'name': file_name
                }
            ]
        #
        # result.sort(
        #     key=lambda item: item.get('sequence')
        # )

        result = sorted(
            result,
            key=lambda item: int(item.get('sequence'))
        )
        return result

    def _merge_epub_files(self, file_paths):
        pass


if __name__ == '__main__':
    # print('dpackgae' ,)
    root_path =  os.path.dirname(os.path.dirname(os.path.realpath(__file__))) 
    
    import sys
    sys.path.append(root_path)

    from cli.ebook_merger import _init_parser
    import argparse
    
    parser = argparse.ArgumentParser()
    _init_parser(parser=parser)
    opts = parser.parse_args()

    service = EbookMergerService(opts=opts)


