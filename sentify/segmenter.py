import spacy


def get_nlp(lang):
    if lang in ('en', 'ca', 'au'):
        return spacy.load('en_core_web_sm')
    else:
        return None


def file2string(fname):
    with open(fname, 'r') as f:
        return f.read()


class Segmenter:
    def __init__(self, lang='en'):
        self.lang = lang
        self.nlp = get_nlp(self.lang)

    def text2sents(self, text):
        assert self.nlp is not None
        assert text
        text = " ".join(text.split())
        doc = self.nlp(text)
        sents = [str(s) for s in doc.sents]
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
