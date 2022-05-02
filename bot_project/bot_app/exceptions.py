"""Collection of slack bot error exception."""


class QueryDoesNotExist(Exception):
    """Raise QueryDoesNotExist if record is not found in the database."""