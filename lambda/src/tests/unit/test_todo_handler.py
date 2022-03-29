import json
import unittest
from unittest import mock

import pytest
from todo_handler import main

# from todo_handler import main


def mocked_dynamodb_get_items():
    return dict({
        "Items": [{
            "todo": "todo 1"
        }]
    })


def mocked_sqs_send_message(message):
    return "1"


@pytest.mark.usefixtures("mock_api_gateway_events")
class TodoHandlerTest(unittest.TestCase):
    @mock.patch('todo_handler.main.dynamodb_get_items', mocked_dynamodb_get_items)
    @mock.patch('todo_handler.main.sqs_send_message', mocked_sqs_send_message)
    def test_lambda_handler_get(self):

        ret = main.lambda_handler(self.event.get_event, "")
        data = json.loads(ret["body"])

        assert ret["statusCode"] == 200
        assert len(data) == 1

    @mock.patch('todo_handler.main.dynamodb_get_items', mocked_dynamodb_get_items)
    @mock.patch('todo_handler.main.sqs_send_message', mocked_sqs_send_message)
    def test_lambda_handler_post(self):

        ret = main.lambda_handler(self.event.post_event, "")
        data = json.loads(ret["body"])

        assert ret["statusCode"] == 201
        assert "todo" in ret["body"]
        assert data["todo"] == "todo 1"

# def test_lambda_handler_get(apigw_event):
#     # arrange
#     mocked_dynamodb_get_items = patch('todo_handler.main.dynamodb_get_items')
#     mocked_sqs_send_message = patch('todo_handler.main.dynamodb_get_items')
#     mock_dynamo = mocked_dynamodb_get_items.start()
#     mock_sqs = mocked_sqs_send_message.start()
#     mock_dynamo.return_value = Mock({
#         "Items": [{
#             "todo": "todo 1"
#         }]
#     })

#     mock_sqs.return_value = Mock("111111")

#     # action
#     ret = main.lambda_handler(apigw_event, "")
#     data = json.loads(ret["body"])

#     # assert
#     assert ret["statusCode"] == 200
#     assert len(data) == 1


# def test_lambda_handler_post(apigw_post_event):
#     # arrange
#     mocked_dynamodb_get_items = patch('todo_handler.main.dynamodb_get_items')
#     mocked_sqs_send_message = patch('todo_handler.main.dynamodb_get_items')
#     mock_dynamo = mocked_dynamodb_get_items.start()
#     mock_sqs = mocked_sqs_send_message.start()
#     mock_dynamo.return_value = Mock({
#         "Items": [{
#             "todo": "todo 1"
#         }]
#     })

#     mock_sqs.return_value = Mock("111111")

#     # action
#     ret = main.lambda_handler(apigw_post_event, "")
#     data = json.loads(ret["body"])

#     # assert
#     assert ret["statusCode"] == 201
#     assert "todo" in ret["body"]
#     assert data["todo"] == "todo 1"
