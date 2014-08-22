from sqlalchemy.orm import sessionmaker

class Session(object):
    def __init__(this, a_val):
        this.engine = a_val
        this.session = None

    def __call__(this):
        if not this.session:
            this.session = sessionmaker(bind = this.engine)

        return this.session()

