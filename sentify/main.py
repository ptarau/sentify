from smart_open import open as xopen
from pdfminer.high_level import extract_text
from sentify.wikifetch import page2text
from sentify.segmenter import Segmenter
from sentify.config import CF
from sentify.tools import *


def sentify(doc_type, doc_name, clean=True, store=None):
    """
    converts a url, a wikipage or a pdf file to
    a list of sentences, ready for NLP or LLM processing
    """
    if store is not None and exists_file(store):
        return file2sents(store)

    text = textify(doc_type, doc_name)

    seg = Segmenter()
    sents = seg.text2sents(text)

    if clean:
        sents = sent_cleaner(sents)

    if store is not None:
        sents2file(sents, store)

    return sents


known_types = ('url', 'wikipage', 'txt', 'pdf')


def textify(doc_type, doc_name):
    """
    converts a a url, a wikipage or a pdf file to
    a text string
    """

    doc_type = doc_type.lower()
    if doc_type not in known_types:
        print('*** doctype should be one of: ', known_types)
        return None

    if doc_type == 'txt':
        assert exists_file(doc_name), doc_name
        text = file2text(doc_name)
    elif doc_type == 'pdf':
        assert exists_file(doc_name), doc_name
        text = pdf2text(doc_name, minline=4)
    elif doc_type == 'url':
        text = url2text(doc_name)
    else:
        # wikipage
        text = page2text(doc_name)

    return text


def url2text(url):
    """
    fetches a text or pdf file from a url
    and returns it as a text string
    """
    if url.lower().endswith('.txt'):
        with xopen(url, 'r') as f:
            text = f.read()
            return text
    elif url.lower().endswith('.pdf'):
        with xopen(url, 'rb') as f:
            text = pdf2text(f)
            return text
    else:
        print('*** expected .txt or .pdf file at: ', url)
        return None


def url2bin(url, binary_fname):
    """
    fetches a binary file (e.g., a pdf) and saves it
    to a local file
    """
    with xopen(url, 'rb') as f:
        bs = f.read()
        ensure_path(binary_fname)
        with open(binary_fname, 'wb') as g:
            g.write(bs)


def url2file(url, fname):
    """
    fetches a text or pdf file from a url
    and saves it as a text file
    """
    text = url2text(url)
    ensure_path(fname)
    text2file(text, fname)


def pdf2text(pdf_or_stream, minline=4):
    """
    extracts a text string from a PDF file using pdfminer
    """
    text = extract_text(pdf_or_stream)
    text = pdf_cleaner(text, minline=minline)
    return text


def pdf2tname(pdf, tname, minline=4, minsize=32):
    text = pdf2text(pdf, minline=minline)
    text2file(text, tname)
    if os.path.getsize(tname) > minsize:
        return True
    os.remove(tname)
    return False


def test_main():
    url = 'https://raw.githubusercontent.com/ptarau/recursors/main/TODO.txt'
    fname = CF.OUT + 'txt.txt'
    sents = sentify('url', url)
    print(sents)
    if sents:
        sents2file(sents, fname)

    url = 'https://aclanthology.org/W04-3252.pdf'
    sents = sentify('url', url)
    fname = CF.OUT + 'pdf.txt'
    sents2file(sents, fname)

    page = 'logic_programming'
    sents = sentify('wikipage', page)
    outfname = CF.OUT + f'{page}.txt'
    sents2file(sents, outfname)

    infname = outfname
    sents = sentify('txt', infname, clean=False)
    outfname = CF.OUT + 'same.txt'
    sents2file(sents, outfname)

    url = 'https://arxiv.org/pdf/1909.07328.pdf'
    infname = CF.IN + "soft_unif.pdf"
    url2bin(url, infname)
    sents = sentify('pdf', infname, clean=True)
    outfname = CF.OUT + 'soft_unif.txt'
    sents2file(sents, outfname)


if __name__ == "__main__":
    test_main()
