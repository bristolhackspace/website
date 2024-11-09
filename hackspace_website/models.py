import enum
from sqlalchemy import types, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression
from typing import Optional, List
import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    migrate = Migrate(app, db)


class UTCDateTime(types.TypeDecorator):

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is None:
            return
        if value.utcoffset() is None:
            raise ValueError("Got naive datetime while timezone-aware is expected")
        return value.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, engine):
        if value is not None:
            return value.replace(tzinfo=datetime.timezone.utc)


class BannedIp(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip_addr: Mapped[str] = mapped_column(types.String(120), unique=True, index=True)
    expiry: Mapped[Optional[datetime.datetime]] = mapped_column(UTCDateTime)


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(types.String(120))
    email: Mapped[str] = mapped_column(types.String(200))
    subject: Mapped[str] = mapped_column(types.String(200))
    message: Mapped[str] = mapped_column(types.String(2000))
    ip_addr: Mapped[str] = mapped_column(types.String(120))
    user_agent: Mapped[str] = mapped_column(types.String(120))
    honeypot_triggered: Mapped[bool] = mapped_column(types.Boolean)
    received: Mapped[datetime.datetime] = mapped_column(UTCDateTime)
    sent: Mapped[Optional[datetime.datetime]] = mapped_column(UTCDateTime)
