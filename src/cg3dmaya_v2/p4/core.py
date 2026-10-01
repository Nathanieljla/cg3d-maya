"""Optional Perforce client construction without import-time connections."""

DEFAULT_PORT = "ssl:azhcprd01.madisoncollege.edu:1666"
DEFAULT_USER = "nalbright_admin"


def create_client(port=DEFAULT_PORT, user=DEFAULT_USER, password="", connect=True):
    """Create and optionally connect a P4Python client.

    P4Python remains optional and is imported only when this function is used.
    """
    from P4 import P4

    client = P4()
    client.port = port
    client.user = user
    client.password = password
    if connect:
        client.connect()
        client.run_login()
    return client
