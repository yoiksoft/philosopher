"""Testing configurations.
"""

import pytest
from starlette.config import environ
from starlette.testclient import TestClient

environ["TESTING"] = "TRUE"


@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
  """Create a clean test database.
  """


@pytest.fixture()
def client():
  """Make a client available to test cases.
  """

  from app import app  # pylint: disable=import-outside-toplevel
  with TestClient(app) as test_client:
    yield test_client
