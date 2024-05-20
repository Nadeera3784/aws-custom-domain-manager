import boto3
from moto import mock_s3
from test.test_base import TestBase
from src.lambda_myfunction import main_method
from src.lambda_myfunction import lambda_handler


class TestUnitMyFunction(TestBase):

    def test_unit_lambda_handler(self, test_data):
        testResults = lambda_handler(test_data, {})
        assert testResults["message"] == 2

    def test_unit_main_method(self, test_data):
        testResults = main_method(test_data["number"])
        assert testResults["message"] == 2

    # kept here for future reference about S3 mocking
    # @mock_s3
    # def test_function(self, test_data):        
    #     s3 = boto3.resource('s3', region_name='us-east-1')
    #     s3.create_bucket(Bucket='first_bucket')
    #     s3.create_bucket(Bucket='second_bucket')
    #     testResults = lambda_handler(test_data, {})
    #     assert testResults['statusCode'] == 200
    #     assert testResults["message"] == 2
