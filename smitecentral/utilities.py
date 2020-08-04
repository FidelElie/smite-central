import re
import json

def get_credentials(key):
    """ Get Credential From Stored JSON File.

    Parameters
    ----------
    key: str
        Dictionary key to access the desired credential.

    Returns
    -------
        Value for desired key

    Comments
    --------
        Remember to exclude your credentials.json file from version control.
    """
    with open("credentials.json", "r") as credentials_file:
        credentials_data = json.load(credentials_file)

    try:
        return credentials_data[key]
    except KeyError:
        raise KeyError(f"Credential {key} was not found in file.")


