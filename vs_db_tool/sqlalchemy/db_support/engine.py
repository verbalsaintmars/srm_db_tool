import sqlalchemy as alchemy
from sqlalchemy import create_engine


class Engine(object):
    """
        Wrapper over create_engine
        Get Engine instance
    """

    def __init__(this):
        this.ECHO = None
        this.ENCODING = None
        this.URL = None

    def SetEcho(this, a_echo):
        this.echo = a_echo

    def GetEcho(this):
        return this.echo

    def SetEncoding(this, a_enc):
        this.encoding = a_enc

    def GetEncoding(this):
        return this.encoding

    def SetURL(this, a_url):
        this.url = a_url

    def GetURL(this):
        return this.url

    ENCODING = property(GetEncoding, SetEncoding)
    ECHO = property(GetEcho, SetEcho)
    URL = property(GetURL, SetURL)

    def GetEngine(this):
        return create_engine(this.URL, encoding = this.ENCODING, echo = this.ECHO)
