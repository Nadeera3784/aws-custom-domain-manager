import pytest


class TestBase():

    @pytest.fixture()
    def test_data(self):
        return {"number": 1}