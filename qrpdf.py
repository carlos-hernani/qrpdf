"""
Name: qrpdf

Download papers from arxiv and add their URL in QR format
to easily download them later.

Requirements: arxiv, pymupdf, qrcode, pillow, termcolor

MIT License

Copyright (c) 2021 Carlos Hernani Morales

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
import os, sys, ssl, shutil


import qrcode
import fitz
import arxiv as arx



from dataclasses import dataclass
from typing import List, Optional
from termcolor import colored


@dataclass
class QRpdf:
    urls: str
    site: str = 'arxiv'
    ids: Optional[List[str]] = None

    def __post_init__(self):
        regex = r"https://arxiv.org/abs/\s*(.*)"

        # test_str = """
        # https://arxiv.org/abs/2109.14101
        # https://arxiv.org/abs/2109.14102
        # https://arxiv.org/abs/2109.14103
        # https://arxiv.org/abs/2109.14104
        # https://arxiv.org/abs/2109.14105
        # """

        matches = re.finditer(regex, self.urls, re.MULTILINE)
        #self.urls = [match.group(0) for match in matches]
        self.ids = [match.group(1) for match in matches]
        self.urls = ['https://arxiv.org/abs/'+ id for id in self.ids]
        
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context

    @staticmethod
    def urlqr(url: str, id: str):
        if not os.path.exists('.tempqr'):
            os.mkdir('.tempqr')
        
        qr = qrcode.make(url)
        qr.save('.tempqr/' + id + '.png')
        
    def merge_qr_pdf(self):
        for n, id in enumerate(self.ids):
            in_pdf_file = 'temp'+id + '.pdf'
            out_pdf_file = id + '.pdf'
            img_file = '.tempqr/' + id + '.png'
            image_square = fitz.Rect(0,0, 100, 100)
            pix = fitz.Pixmap(img_file)
            file_handle = fitz.open(in_pdf_file)
            first_page = file_handle[0]
            first_page.insertImage(image_square, pixmap = pix)
            
            file_handle.save(out_pdf_file)
            print(colored(id + ' ... Merged', 'green'))


    def delete_tempfiles(self):
        shutil.rmtree('.tempqr')
        for id in self.ids:
            os.remove('temp'+id + '.pdf')


    def arxiv(self):
        for id in self.ids:
            search = arx.Search(id_list=[id])
            paper = next(search.results())
            # print(paper.title)
            paper.download_pdf('./', filename='temp'+id+'.pdf')
            print(colored(id + ' ... Downloaded', 'green'))


    def main(self):
        str_download = 'Downloading papers: ....'
        print(colored(str_download, 'red'))
        print(colored('='*len(str_download), 'red'))
        self.arxiv()
        str_qr = 'Generating QR codes: ....'
        print(colored(str_qr, 'red'))
        print(colored('='*len(str_qr), 'red'))

        for n, id in enumerate(self.ids):
            print(self.urls[n])
            self.urlqr(self.urls[n], id)
            print(colored(id + ' ... Done', 'green'))
        
        str_pdf = 'Merging QRs & PDFs: ....'
        print(colored(str_pdf, 'red'))
        print(colored('='*len(str_pdf), 'red'))

        self.merge_qr_pdf()
        self.delete_tempfiles()




if __name__ == '__main__':
    urls = sys.stdin.read()
    QRpdf(urls).main()

