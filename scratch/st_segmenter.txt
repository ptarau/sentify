from pathlib import Path
import stanza
from sentify.tools import exists_file

STANZA_REUSE_RESOURCES = 2  # hidden deep down in Stanza


def home_dir():
    return str(Path.home())


def get_nlp(lang='en',batch=64):
    if not exists_file(home_dir() + '/stanza_resources/' + lang):
        stanza.download(lang)
    return stanza.Pipeline(processors='tokenize',
                           download_method=STANZA_REUSE_RESOURCES,
                           logging_level='CRITICAL',
                           use_gpu=False, tokenize_batch_size=batch)


class Segmenter:

    def __init__(self, lang='en'):
        self.lang = lang
        self.nlp = get_nlp()

    def text2sents(self, text):
        assert self.nlp is not None
        assert text

        doc = self.nlp(text)

        sents = []
        for sent in doc.sentences:

            toks = []
            for token in sent.tokens:
                toks.append(token.text)

            sent_text = " ".join(toks)

            sents.append(sent_text)
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
