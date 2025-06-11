from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    BooleanField,
    AutoField,
)

from .core import BaseModel, pg_db


class User(BaseModel):
    id = AutoField(primary_key=True)
    user_id = IntegerField(unique=True)
    first_name = CharField()
    last_name = CharField(null=True)


class Subscriber(BaseModel):
    user = ForeignKeyField(model=User, on_delete="CASCADE", unique=True)
    chat_id = IntegerField(unique=True)
    signed = BooleanField()


def create_table():
    if User.table_exists() or Subscriber.table_exists():
        print("tables created")
        return

    with pg_db:
        pg_db.create_tables([User, Subscriber])


if __name__ == "__main__":
    create_table()
