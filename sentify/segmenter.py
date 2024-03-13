from pathlib import Path
import pysbd


class Segmenter:

    def __init__(self, lang='en'):
        self.lang = lang
        self.nlp = pysbd.Segmenter(language=lang, clean=False)

    def text2sents(self, text):
        text=" ".join(text.split())
        assert self.nlp is not None
        assert text
        text=text.replace("\u3002",'.') # for Chinese dot

        sents = self.nlp.segment(text)
        return sents


def segment_text(text):
    seg = Segmenter()
    return seg.text2sents(text)


def test_segmenter():
    seg = Segmenter()
    print(seg.text2sents(
        """Dr. Cat, 3.14 years old, sits on the mat. 
         Mr. Dog, old and Texas-based, barks at her.

         """
    ))

    print(seg.text2sents(
        """
            Who cares? 

            I do!

        """
    ))


if __name__ == "__main__":
    test_segmenter()
