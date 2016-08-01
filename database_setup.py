from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from collections import OrderedDict

Base = declarative_base()


# Holds User Information
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False,  primary_key=True)
    picture = Column(String(250))


# Holds Category Information
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Serialized object creation
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        ordered_cat = OrderedDict()
        ordered_cat["id"] = self.id
        ordered_cat["name"] = self.name
        return ordered_cat

# Holds Item Details
class Item(Base):
    __tablename__ = 'item'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Serialized object creation
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        ordered_item = OrderedDict()
        ordered_item["cat_id"] = self.category_id
        ordered_item["description"] = self.description
        ordered_item["id"] = self.id
        ordered_item["title"] = self.title
        ordered_item["owner"] = self.user.email
        ordered_item["user_id"] = self.user.id
        return ordered_item

engine = create_engine('sqlite:///itemcatalog.db')


Base.metadata.create_all(engine)
