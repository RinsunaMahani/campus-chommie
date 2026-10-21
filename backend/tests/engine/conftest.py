import pytest

from campus_engine.catalogue import load_catalogue


@pytest.fixture(scope="session")
def catalogue():
    return load_catalogue()


@pytest.fixture(scope="session")
def smu(catalogue):
    return catalogue["smu"]


@pytest.fixture
def strong_marks():
    """A learner well above SMU's MBChB minimums (levels 7,7,7,7, LO 7, then 6 and 6 = 47 points)."""
    return {
        "english": 82,
        "mathematics": 81,
        "physical_sciences": 80,
        "life_sciences": 85,
        "life_orientation": 88,
        "geography": 74,
        "home_language": 79,
    }
