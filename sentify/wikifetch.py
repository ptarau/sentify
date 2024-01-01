import wikipediaapi
from sentify.segmenter import segment_text
from sentify.tools import ensure_path, sent_cleaner
from sentify.config import CF

import logging

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)


def page2text(page_name, lang='en'):
    print('PROCESSING WIKI FOR:', page_name)
    wiki_wiki = wikipediaapi.Wikipedia(
        language=lang,
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    page = wiki_wiki.page(page_name)
    text = page.text
    if not text:
        print('NO WIKY ENTRY FOR:', page_name)
        return None
    return text


def page2file(page_name, lang='en'):
    text = page2text(page_name, lang=lang)

    if not text:
        print('*** NO TEXT FROM:', page_name)
        return None

    sents = segment_text(text)

    cleans = sent_cleaner(sents)

    fname = page_name.lower().replace(' ', '_').replace('.', '_')
    if cleans:
        path = CF.DATA + f'{fname}.txt'
        ensure_path(path)
        ground_truth_file = path
        with open(ground_truth_file, 'w') as f:
            for x in cleans:
                print(x, file=f)
        return ground_truth_file
    else:
        print('*** NO FILE GENERATED FOR:', page_name)
        return None


def run_wikifetch():
    page2file('Logic programming')
    page2file('Computational thinking')
    page2file('Artificial general intelligence')
    page2file('Expansion of the universe')
    page2file('No such page')


if __name__ == "__main__":
    pass
    run_wikifetch()
