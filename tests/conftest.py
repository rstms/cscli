# pytest fixtures

import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def project():
    project = Path().stem
    breakpoint()
    return project
