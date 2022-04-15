import uuid
from os.path import join
from datetime import datetime
from qrcode import make

from src.qr.web3_prcs import get_raw_msg, get_signed_message, submit_signature
from src.db.db import get_user_details


async def get_access_token(discord_id: int, engine):
    """Uses the signed msg, raw msg and the ronin address of the user to get an access token"""
    user_address, user_private_key = get_user_details(discord_id, engine)

    if user_private_key=="None":
        return None

    raw_msg = await get_raw_msg()
    # print(raw_msg)  #!DEBUG

    signed_msg = await get_signed_message(raw_msg, private_key=user_private_key)
    # print(signed_msg)  #!DEBUG

    access_token = await submit_signature(
        signed_msg, msg=raw_msg, account_address=user_address
    )
    # print(access_token)  #!DEBUG
    return access_token


async def create_qr_code(discord_id: int, engine) -> str:
    """creates a qr code image file, to be used inside a cmd, after that the qr gets deleted."""
    access_token = await get_access_token(discord_id, engine)
    # print(access_token)  #!DEBUG

    if access_token is None:
        return None

    qr_file_name = f"qr_{discord_id}_{str(uuid.uuid4())[0:8]}.png"
    # print(qr_file_name)  #!DEBUG
    save_dir_tup = ("src", "qr", "images")
    save_path = join(*save_dir_tup, qr_file_name)
    # print(save_path)  #!DEBUG

    make(access_token).save(save_path)

    return save_path

    # TODO SEND TO USER THEN DELETE QR
