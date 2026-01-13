from datetime import datetime, timedelta, timezone

import sqlalchemy
from .session import SqlAlchemyBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    ADMIN = 1
    USER = 2
    HAVE_ACCESS = 1
    DONT_HAVE_ACCESS = 0

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    role = sqlalchemy.Column(sqlalchemy.Integer, default=USER, nullable=False)
    access = sqlalchemy.Column(sqlalchemy.Integer, default=DONT_HAVE_ACCESS, nullable=False)

    scripts = relationship('Scripts', back_populates='user', cascade='all, delete-orphan')


class Scripts(SqlAlchemyBase):
    __tablename__ = 'scripts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'), index=True, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone(timedelta(hours=3))))
    script_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('scripts.id'), nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(50), index=True)
    success = sqlalchemy.Column(sqlalchemy.Boolean)

    user = relationship('Users', back_populates='scripts')
    cards = relationship('Cards', back_populates='script', cascade='all, delete-orphan')
    categories = relationship('Categories', back_populates='script', cascade='all, delete-orphan')
    keywords = relationship('Keywords', back_populates='script', cascade='all, delete-orphan')
    products = relationship('Products', back_populates='script', cascade='all, delete-orphan')


class Categories(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    script_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('scripts.id'), index=True, nullable=False)

    script = relationship('Scripts', back_populates='categories')
    keywords = relationship('Keywords', back_populates='category', cascade='all, delete-orphan')
    products = relationship('Products', back_populates='category', cascade='all, delete-orphan')
    lots = relationship('Lots', back_populates='category', cascade='all, delete-orphan')


class Keywords(SqlAlchemyBase):
    __tablename__ = 'keywords'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(512), nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('categories.id'), index=True, nullable=False)
    script_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('scripts.id'), index=True, nullable=False)

    category = relationship('Categories', back_populates='keywords')
    script = relationship('Scripts', back_populates='keywords')


class Products(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    article = sqlalchemy.Column(sqlalchemy.String(255), index=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('categories.id'), index=True, nullable=False)
    script_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('scripts.id'), index=True, nullable=False)

    category = relationship('Categories', back_populates='products')
    script = relationship('Scripts', back_populates='products', cascade='all, delete-orphan')
    lots = relationship('Lots', back_populates='product', cascade='all, delete-orphan')


class Cards(SqlAlchemyBase):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.String(100), index=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    region = sqlalchemy.Column(sqlalchemy.String(255))
    link = sqlalchemy.Column(sqlalchemy.String(1024), nullable=False)
    extracted_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone(timedelta(hours=3))))
    script_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('scripts.id'), nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(50), index=True)
    relevant = sqlalchemy.Column(sqlalchemy.Boolean)

    script = relationship('Scripts', back_populates='cards')
    lots = relationship('Lots', back_populates='card', cascade='all, delete-orphan')


class Lots(SqlAlchemyBase):
    __tablename__ = 'lots'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    article = sqlalchemy.Column(sqlalchemy.String(255), index=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text)
    count = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    card_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('cards.id'), index=True, nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('categories.id'), index=True)
    status = sqlalchemy.Column(sqlalchemy.String(50), index=True)
    match_product_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('products.id'), index=True)

    card = relationship('Cards', back_populates='lots')
    product = relationship('Products', back_populates='lots')
    category = relationship('Categories', back_populates='products')
