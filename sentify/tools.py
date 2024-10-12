import os


def ensure_path(fname):
    """
    makes sure path to directory and directory exist
    """
    if '/' not in fname: return
    d, _ = os.path.split(fname)
    os.makedirs(d, exist_ok=True)


def exists_file(fname):
    """tests  if it exists as file or dir """
    return os.path.exists(fname)


def remove_file(fname):
    return os.remove(fname)


def text2file(text, fname):
    ensure_path(fname)
    with open(fname, 'w') as g:
        g.write(text)


def file2text(fname):
    with open(fname, 'r') as f:
        text = f.read()
        return text


def sents2file(sents, fname):
    assert sents, 'no sentences written to: ' + fname
    assert isinstance(sents, list), 'expected list of sents, got: ' + str(type(sents))
    ensure_path(fname)
    with open(fname, 'w') as f:
        for x in sents:
            print(x, file=f)


def file2sents(fname):
    with open(fname, 'r') as f:
        return list(f.readlines())


def pdf_cleaner(text, minline=4):
    assert text
    text = text.replace('-\n', '')
    lines = []
    for para in text.split('\n\n'):
        for line in para.split('\n'):
            if len(line) < minline: continue
            if line.isnumeric(): continue
            lines.append(line)
        lines.append('\n')
    text = "\n".join(lines)
    return text


def is_capitalized(s):
    return s and s[0] == s[0].capitalize()


def sent_cleaner(sents, minlen=10):
    cleans = []
    good = "'~:;=/*()[]{},.?!-+" + '"'
    keep = "$%"

    for s in sents:
        s = s.strip()
        if len(s)<minlen:
            continue
        cap = int(is_capitalized(s))
        for g in good:
            s = s.replace(g, ' ')
        for g in keep: s = s.replace(g, ' ' + g + ' ')
        xs = s.split()
        raw = len(xs)

        xs = [x.strip() for x in xs if x.isalnum() or x in keep]
        cleaned = len(xs)

        if cleaned > 5 - cap and cleaned / raw > 0.8 - cap / 10: # and len(xs[-1]) > 3:
            clean = " ".join(xs)
            cleans.append(clean + ".")
    if not cleans:
        print('*** NO CLEAN SENT FOUND IN:', sents)
    return cleans
