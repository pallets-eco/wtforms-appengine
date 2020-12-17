"""py.test shared testing configuration.
This defines fixtures (expected to be) shared across different test
modules.
"""

import pytest
from dsemu import Emulator
from google.cloud import ndb


@pytest.fixture(scope="session")
def emulator():
    with Emulator() as emulator:
        yield emulator


@pytest.fixture(scope="session")
def session_client():
    client = ndb.Client(project="test")
    yield client


@pytest.fixture()
def client(emulator: Emulator, session_client: ndb.Client):
    emulator.reset()
    yield session_client
