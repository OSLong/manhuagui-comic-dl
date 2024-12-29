from glob import glob
from textual import log
import os

class EbookMergerService():
    def __init__(self, opts):
        self.opts = opts

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
            result += [
                {
                    'path': file_path,
                    'name': os.path.basename(file_path)
                }
            ]
        return result


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

    print(f"""
view serchfiel 
          ==============
          {service._list_epub_in_directory()}
        """)
