from os import path
from datetime import datetime
from sqlmodel import Session, Field, SQLModel, create_engine, select
from sqlalchemy.exc import NoResultFound
from typing import Optional
from asyncio import run


class MysticUser(SQLModel, table=True):
    discord_id: Optional[int] = Field(default=None, primary_key=True)
    ronin_address: str
    private_key: str


class Warning(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    time: datetime
    user_id: Optional[int] = Field(default=None, foreign_key="mysticuser.discord_id")
    reason: str


def connect_to_db(debug=False):
    path_to_db = path.join("src", "db", "mystic-titans-db.db")

    sqlite_url = (
        f"sqlite:///{path_to_db}" if not debug else f"sqlite:///mystic-titans-db.db"
    )

    engine = create_engine(sqlite_url)  #!DEBUG ", echo=True)"
    print("        +sqlite db")
    return engine


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


def check_user_exists(discord_id: int, engine):
    with Session(engine) as session:
        statement = select(MysticUser).where(MysticUser.discord_id == discord_id)
        results = session.exec(statement)

        try:
            user = results.one()
            return user
        except NoResultFound:
            return None


def connect_user_db(
    discord_id: int,
    ronin_address: str,
    private_key: str,
    engine,
):
    if check_user_exists(discord_id, engine):
        return None

    else:
        user = MysticUser(
            discord_id=discord_id, ronin_address=ronin_address, private_key=private_key
        )

        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user


def disconnect_user_db(discord_id: int, engine):
    with Session(engine) as session:
        user = check_user_exists(discord_id, engine)

        if not user:
            return False
        else:
            session.delete(user)
            session.commit()
            return True


def get_address(discord_id: int, engine):
    if not check_user_exists(discord_id, engine):
        return None

    else:
        with Session(engine) as session:
            statement = select(MysticUser).where(MysticUser.discord_id == discord_id)
            results = session.exec(statement)

            result_address = f"0x{((results.one()).ronin_address)[6:]}"
            return result_address


def get_private_key(discord_id: int, engine):
    if not check_user_exists(discord_id, engine):
        return None

    else:
        with Session(engine) as session:
            statement = select(MysticUser).where(MysticUser.discord_id == discord_id)
            user_result: MysticUser = session.exec(statement).one()

            user_private_key = user_result.private_key
            return bool(user_private_key)


def get_user_details(discord_id: int, engine):
    if not check_user_exists(discord_id, engine):
        return None

    else:
        with Session(engine) as session:
            statement = select(MysticUser).where(MysticUser.discord_id == discord_id)
            user_result: MysticUser = session.exec(statement).one()

            user_address = f"0x{(user_result.ronin_address)[6:]}"
            user_private_key = user_result.private_key
            return (user_address, user_private_key)


def add_warn_db(discord_id: int, reason: str, engine):
    if not check_user_exists(discord_id, engine):
        return None

    else:
        warning = Warning(
            id=f"{discord_id}+{datetime.utcnow()}",
            user_id=discord_id,
            time=datetime.utcnow(),
            reason=reason,
        )

        with Session(engine) as session:
            session.add(warning)
            session.commit()
            session.refresh(warning)
        return warning


def get_warns(discord_id: int, engine):
    if not check_user_exists(discord_id, engine):
        return False

    else:
        with Session(engine) as session:
            statement = select(Warning).where(Warning.user_id == discord_id)
            results = session.exec(statement)

            warnings_list = results.all()

            if len(warnings_list) < 1:
                return None
            else:
                return warnings_list


def clr_warns(discord_id: int, engine):
    with Session(engine) as session:
        warns = get_warns(discord_id, engine)

        if warns is None:
            return None
        elif warns == False:
            return False

        else:
            for warn in warns:
                session.delete(warn)

        session.commit()
        return True


def add_private_key_db(discord_id, engine, private_key: str):
    if not check_user_exists(discord_id, engine):
        return None

    else:
        with Session(engine) as session:
            statement = select(MysticUser).where(MysticUser.discord_id == discord_id)
            results = session.exec(statement)

            user = results.one()
            user.private_key = private_key
            session.add(user)

            session.commit()
            session.refresh(user)

            return user.private_key


#!DEBUGGING
async def main():
    engine = connect_to_db(debug=True)
    print(engine)

    # print(disconnect_user_db(747449468864954438, engine))
    # print(
    #     connect_user_db(
    #         discord_id=747449468864954438,
    #         ronin_address="ronin:26d252724d08a30151ab5c87bd6b4fb5eadb1500",
    #         private_key="qwerty",
    #         engine=engine,
    #     )
    # )
    print(check_user_exists(747449468864954438, engine=engine))

    print(get_address(engine=engine, discord_id=747449468864954438))
    print(get_warns(engine=engine, discord_id=747449468864954438))
    print(clr_warns(engine=engine, discord_id=747449468864954438))
    # print(await UserData.fetch_grind_info(747449468864954438, engine))
    quit()
    print(check_user_exists(76543786543, engine=engine))

    # ? no warning
    print(
        connect_user_db(
            discord_id=12345,
            ronin_address="hgjhgfdfds",
            private_key="ujykjhgfhgtrf",
            engine=engine,
        )
    )
    print(check_user_exists(12345, engine=engine))

    # print("<==============>")

    # print(disconnect_user_db(discord_id=76543786543))
    # print(check_user_exists(discord_id=76543786543))
    # print(disconnect_user_db(discord_id=76543786543))
    # print(check_user_exists(discord_id=76543786543))

    # print("<==============>")

    # print(add_warn_db(discord_id=8765, reason="oh man"))
    # print(add_warn_db(discord_id=76543786543, reason="oh man"))
    # print(add_warn_db(discord_id=76543786543, reason="oh hell naw"))
    # print(add_warn_db(discord_id=76543786543, reason="mf bish"))

    print("<==============>")

    print(get_warns(discord_id=12345765, engine=engine))
    print(get_warns(discord_id=12345, engine=engine))
    print(get_warns(discord_id=76543786543, engine=engine))


if __name__ == "__main__":
    run(main())
