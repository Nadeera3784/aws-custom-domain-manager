from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from test.test_base import TestBase
from src.lambda_myfunction import main_method


class TestUIMyFunction(TestBase):

    def test_ui_lambda_handler(self, test_data):
        assert 1==1

        # Kept here for future reference
        # driver = webdriver.Firefox()
        # driver.get("http://www.python.org")
        # assert "Python" in driver.title
        # elem = driver.find_element_by_name("q")
        # elem.clear()
        # elem.send_keys("pycon")
        # elem.send_keys(Keys.RETURN)
        # assert "No results found." not in driver.page_source
        # driver.close()