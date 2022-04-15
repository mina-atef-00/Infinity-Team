from requests import post
from json import loads
import qrcode
from web3.auto import w3
from eth_account.messages import encode_defunct


async def get_raw_msg():
    """Function to get message to sign from axie"""

    # ? An exemple of a request_body needed
    request_body = {
        "operationName": "CreateRandomMessage",
        "variables": {},
        "query": "mutation CreateRandomMessage {\n  createRandomMessage\n}\n",
    }

    # ? Send the request
    r = post(
        url="https://axieinfinity.com/graphql-server-v2/graphql",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        },
        data=request_body,
    )
    # print(r) #!DEBUG
    # ? Load the data into json format
    json_data = loads(r.text)
    # ? Return the message to sign
    return json_data["data"]["createRandomMessage"]


async def get_signed_message(raw_msg: str, private_key: str):
    """Function to sign the message got from get_raw_msg function"""

    # ? Load the private key from the DataBase in Hex
    private_key = bytearray.fromhex(private_key)
    msg = encode_defunct(text=raw_msg)

    # ? Sign the message with the private key
    hex_sign = w3.eth.account.sign_message(msg, private_key=private_key)

    # ? Return the signature
    return hex_sign


async def submit_signature(signed_msg, msg, account_address):
    """Function to submit the signature and get authorization"""

    # ? An example of a request_body needed
    request_body = {
        "operationName": "CreateAccessTokenWithSignature",
        "variables": {
            "input": {
                "mainnet": "ronin",
                "owner": account_address,
                "message": msg,
                "signature": signed_msg["signature"].hex(),
            }
        },
        "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!) {\n  createAccessTokenWithSignature(input: $input) {\n    newAccount\n    result\n    accessToken\n    __typename\n  }\n}\n",
    }

    # ? Send the request
    r = post(
        url="https://axieinfinity.com/graphql-server-v2/graphql",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        },
        json=request_body,
    )
    # ? Load the data into json format
    json_data = loads(r.text)

    # ? Return the accessToken value
    return json_data["data"]["createAccessTokenWithSignature"]["accessToken"]
