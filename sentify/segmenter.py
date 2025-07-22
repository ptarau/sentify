from time import time
import os
from collections import Counter
import pysbd
from sentify.tools import file2text


class Segmenter:

    def __init__(self, lang="en", max_chunk_size=10000):
        # approx 10 pages max chunk
        self.lang = lang
        self.max_chunk_size = max_chunk_size
        self.nlp = pysbd.Segmenter(language=lang, clean=False)
        self.times = Counter()

    def chunkify(self, text):
        # Split the text into chunks of self.max_chunk_size
        chunks = [
            text[i : i + self.max_chunk_size]
            for i in range(0, len(text), self.max_chunk_size)
        ]
        # print("*** TEXT LEN:", len(text), "CHUNKS:", len(chunks))
        return chunks

    def preprocess(self, text):
        text = text.replace("\u3002", ".")  # for Chinese dot

        chunks = self.chunkify(text)

        sentss = []
        for chunk in chunks:
            chunk = " ".join(chunk.split())
            sents = self.nlp.segment(chunk)
            sentss.append(sents)
        # print('!!! TEXT:', len(text), 'CHUNKS:', len(chunks), 'SENTS:', sum(map(len, sentss)))
        assert sentss, f"No good sentences after preprocessing text of len={len(text)}"
        return sentss

    def text2sents(self, text):
        t1 = time()
        assert self.nlp is not None
        assert text, text
        xss = self.preprocess(text)
        sents = [x.strip() for xs in xss for x in xs if x]
        t2 = time()
        self.times["text2sents"] += t2 - t1
        assert sents
        return sents


def segment_text(text):
    seg = Segmenter()
    return seg.text2sents(text)


def test_segmenter_():
    seg = Segmenter()
    print(
        seg.text2sents(
            """Dr. Cat, 3.14 years old, sits on the mat. 
         Mr. Dog, old and Texas-based, barks at her.

         """
        )
    )

    print(
        seg.text2sents(
            """
            Who cares? 

            I do!

        """
        )
    )

    print("TIMES:", seg.times)


def test_segmenter(fname="~/tmp/lost-time.txt"):
    # replace this with your own large file test
    fname = os.path.expanduser(fname)
    seg = Segmenter(max_chunk_size=10000)
    text = file2text(fname)
    sents = seg.text2sents(text)
    print("SENTS:", len(sents))
    print("TIMES:", seg.times)
    # print(sents[-10:])


if __name__ == "__main__":
    test_segmenter()
