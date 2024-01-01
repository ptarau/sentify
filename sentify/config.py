class ConfigDict:
    """
    meta-dict generator

    wraps a dict object d to support d.x=...
    notation instead of d['x']= ...
    it also gives back the usual dict view
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return str(self.__dict__)

    def as_dict(self):
        return self.__dict__


CF = ConfigDict(
    IN='./IN/',
    OUT='./OUT/',
    DATA='./DATA/'
)
