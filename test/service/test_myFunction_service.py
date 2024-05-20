import json
import subprocess
import pytest
from test.test_base import TestBase
from src.lambda_myfunction import main_method


class TestServiceMyFunction(TestBase):

    def test_service_main_method(self, test_data):
        local_value = str(test_data["number"])
        p = subprocess.Popen( \
            "sls invoke --function myFunction --data '{\"number\": " + \
                local_value + "}'", stdout=subprocess.PIPE, shell=True) 
        (test_result, err) = p.communicate()
        p_status = p.wait()
        json_result = json.loads(test_result)
        final_result = int(json_result["message"])
        assert final_result == 2
