from sqlalchemy import (
    Column,
    Index,
    Integer,
    Unicode,

)

from .meta import Base


class Entry(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    body = Column(Unicode)
    creation_date = Column(Unicode)

    def to_json(self):
        """JSON."""
        return {
            "title": self.title,
            "body": self.body,
            "creation_date": self.creation_date,
        }

Index('my_index', Entry.id, unique=True, mysql_length=255)
