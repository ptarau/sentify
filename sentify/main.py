from time import time
import subprocess
import pandas as pd
from docx import Document
from smart_open import open as xopen
from pdfminer.high_level import extract_text
from sentify.wikifetch import page2text
from sentify.segmenter import Segmenter
from sentify.config import CF

from sentify.tools import *


def sentify(doc_type, doc_name, clean=True, store=None, return_timings=False):
    """
    converts a url, a wikipage or a pdf file to
    a list of sentences, ready for NLP or LLM processing
    """
    if store is not None and exists_file(store):
        if return_timings:
            return file2sents(store), 0, 0
        return file2sents(store)

    t1 = time()
    text = textify(doc_type, doc_name)

    t2 = time()

    seg = Segmenter()
    sents = seg.text2sents(text)
    t3 = time()

    if clean:
        sents = sent_cleaner(sents)

    if store is not None:
        sents2file(sents, store)
    if return_timings:
        return sents, t2 - t1, t3 - t2
    return sents


known_types = ("url", "wikipage", "txt", "pdf", "docx", "xlsx", "xls")


def textify(doc_type, doc_name):
    """
    converts a a url, a wikipage or a pdf file to
    a text string
    """

    doc_type = doc_type.lower()
    if doc_type not in known_types:
        print("*** doctype should be one of: ", known_types)
        raise ValueError(f"Unknown doc_type: {doc_type}")

    if doc_type == "txt":
        assert exists_file(doc_name), doc_name
        text = file2text(doc_name)
    elif doc_type == "pdf":
        assert exists_file(doc_name), doc_name
        text = pdf2text(doc_name, minline=4)
    elif doc_type == "docx":
        assert exists_file(doc_name), doc_name
        text = word2text(doc_name)
    elif doc_type in ("xlsx", "xls"):
        assert exists_file(doc_name), doc_name
        text = excel2text(doc_name)
    elif doc_type == "url":
        text = url2text(doc_name)
    else:
        # wikipage
        text = page2text(doc_name)

    text = text.strip()

    assert text and len(text) > 10, f"Unable to extract text from {doc_type} {doc_name}"
    return text


def url2text(url):
    """
    fetches a text or pdf file from a url
    and returns it as a text string
    """
    if url.lower().endswith(".txt"):
        with xopen(url, "r") as f:
            text = f.read()
            return text
    elif url.lower().endswith(".pdf"):
        with xopen(url, "rb") as f:
            text = pdf2text(f)
            return text
    else:
        print("*** expected .txt or .pdf file at: ", url)
        return None


def url2bin(url, binary_fname):
    """
    fetches a binary file (e.g., a pdf) and saves it
    to a local file
    """
    with xopen(url, "rb") as f:
        bs = f.read()
        ensure_path(binary_fname)
        with open(binary_fname, "wb") as g:
            g.write(bs)


def url2file(url, fname):
    """
    fetches a text or pdf file from a url
    and saves it as a text file
    """
    text = url2text(url)
    ensure_path(fname)
    text2file(text, fname)


def alt_pdf2text(pdf_or_stream, minline=4, trace=1):
    """
    extracts a text string from a PDF file using pdfminer
    """
    if trace:
        print("!!! ENTER pdf2text")
    text = extract_text(pdf_or_stream)
    if trace:
        print("!!! EXITED pdf2text", len(text))
    # print("PDF EXTRACTED:",text)
    text = pdf_cleaner(text, minline=minline)
    return text


def pdf2text(pdf_or_stream, minline=4, trace=1):
    """
    pdf to txt conversion with external tool - if availble
    (on Mac, install pdftotext as part of "poppler tools")
    otherwise, we use pdfminer
    """

    if (
        exists_file("/usr/bin/pdftotext") or exists_file("/opt/local/bin/pdftotext")
    ) or exists_file("/opt/homebrew/bin//pdftotext"):

        if trace:
            print("!!! ENTER pdf2text")
        try:
            txt = "__temp__.txt"
            pdf = "__temp__.pdf"
            if not isinstance(pdf_or_stream, str):
                bs = pdf_or_stream.read()
                with open(pdf, "wb") as g:
                    g.write(bs)
            else:
                pdf = pdf_or_stream

            subprocess.run(["pdftotext", "-q", pdf, txt])

            if exists_file(pdf):
                remove_file(pdf)
            text = file2text(txt)
            remove_file(txt)
            if trace:
                print("!!! pdftotext used")
        except FileNotFoundError:
            text = extract_text(pdf_or_stream)
            if trace:
                print("!!! pdftotext failed, pdfminer used")
    else:
        text = extract_text(pdf_or_stream)
        if trace:
            print("!!! only pdfminer available, used")

    text = pdf_cleaner(text, minline=minline)
    if trace:
        print("!!! EXITED pdf2text", len(text))
    return text


def word2text(textfilename):
    document = Document(textfilename)
    full_text = []
    for paragraph in document.paragraphs:
        # print("!!! PARAGRAPH:", paragraph.text)
        full_text.append(paragraph.text)
    return "\n".join(full_text)


def excel2text(filename):
    df = pd.read_excel(filename)
    text = df.to_csv(sep="\t", index=False, encoding="utf-8")
    text = text.replace("\n", " .\n")
    return text


def pdf2tname(pdf, tname, minline=4, minsize=32):
    text = pdf2text(pdf, minline=minline)
    text2file(text, tname)
    if os.path.getsize(tname) > minsize:
        return True
    os.remove(tname)
    return False


def test_main():
    print()
    url = "https://raw.githubusercontent.com/ptarau/recursors/main/TODO.txt"
    fname = CF.OUT + "txt.txt"
    sents = sentify("url", url)
    print(sents)
    if sents:
        sents2file(sents, fname)
    print()
    url = "https://aclanthology.org/W04-3252.pdf"
    print(url)
    sents = sentify("url", url)
    fname = CF.OUT + "pdf.txt"
    sents2file(sents, fname)
    print()

    page = "logic_programming"
    print(page)
    sents = sentify("wikipage", page)
    outfname = CF.OUT + f"{page}.txt"
    sents2file(sents, outfname)
    print()

    infname = outfname
    sents = sentify("txt", infname, clean=False)
    outfname = CF.OUT + "same.txt"
    print(infname, "=>", outfname)
    sents2file(sents, outfname)
    print()

    url = "https://arxiv.org/pdf/1909.07328.pdf"
    infname = CF.IN + "soft_unif.pdf"
    url2bin(url, infname)
    print(url, infname)
    sents = sentify("pdf", infname, clean=True)
    outfname = CF.OUT + "soft_unif.txt"
    sents2file(sents, outfname)
    print()

    url = "https://filesamples.com/samples/document/docx/sample3.docx"
    infname = CF.IN + "msword.docx"
    url2bin(url, infname)
    print(url, infname)
    sents = sentify("docx", infname, clean=True)
    outfname = CF.OUT + "msword.txt"
    sents2file(sents, outfname)
    print()

    url = "https://filesamples.com/samples/document/xlsx/sample3.xlsx"
    infname = CF.IN + "xlsx"
    url2bin(url, infname)
    print(url, infname)
    sents = sentify("xlsx", infname, clean=True)
    outfname = CF.OUT + "excel.txt"
    sents2file(sents, outfname)
    print()


def test_bad1():
    url = "https://www-public.imtbs-tsp.eu/~gibson/Teaching/CSC4504/ReadingMaterial/KnuthMoore75.pdf"
    sents = sentify("url", url)
    assert sents, url


def test_bad():
    fname = "OUT/same.txt"
    sents = sentify("txt", fname)
    print("RES SENTS:", len(sents))


def timings(url="https://www.gutenberg.org/cache/epub/2600/pg2600.txt"):
    t1 = time()
    print(url)
    sents = sentify("url", url)
    t2 = time()
    print("TIME sentify:", round(t2 - t1, 2), "sents:", len(sents))


if __name__ == "__main__":
    test_main()
    # timings()
    # test_bad()
