from __future__ import unicode_literals

import sys

import simplejson as json
import requests_mock
from minfraud.errors import HTTPError, InvalidRequestError, AuthenticationError, InsufficientFundsError, MinFraudError
from minfraud.models import Insights, Score
from minfraud.webservice import Client

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest


class BaseTest(object):
    def setUp(self):
        self.client = Client(42, 'abcdef123456')
        with open('tests/data/full-request.json', 'r') as file:
            content = file.read()
        self.full_request = json.loads(content)
        with open('tests/data/{}-response.json'.format(self.type),
                  'r') as file:
            self.response = file.read()

    base_uri = 'https://minfraud.maxmind.com/minfraud/v2.0/'

    def test_200(self):
        self.assertEqual(self.cls(json.loads(self.response)),
                         self.create_success())

    def test_200_with_no_body(self):
        with self.assertRaisesRegex(
            MinFraudError,
            "Received a 200 response but could not decode the response as JSON: b''"):
            self.create_success(text='')

    def test_200_with_invalid_json(self):
        with self.assertRaisesRegex(
            MinFraudError,
            "Received a 200 response but could not decode the response as JSON: b'{'"):
            self.create_success(text='{')

    def test_insufficient_funds(self):
        with self.assertRaisesRegex(InsufficientFundsError, 'out of funds'):
            self.create_error(
                text='{"code":"INSUFFICIENT_FUNDS","error":"out of funds"}')

    def test_invalid_auth(self):
        for error in ('AUTHORIZATION_INVALID', 'LICENSE_KEY_REQUIRED',
                      'USER_ID_REQUIRED'):
            with self.assertRaisesRegex(AuthenticationError, 'Invalid auth'):
                self.create_error(
                    text=
                    u'{{"code":"{0:s}","error":"Invalid auth"}}'.format(error))

    def test_invalid_request(self):
        with self.assertRaisesRegex(InvalidRequestError, 'IP invalid'):
            self.create_error(
                text='{"code":"IP_ADDRESS_INVALID","error":"IP invalid"}')

    def test_400_with_invalid_json(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON body: b?'{blah}'"):
            self.create_error(text='{blah}')

    def test_400_with_no_body(self):
        with self.assertRaisesRegex(HTTPError,
                                    'Received a 400 error with no body'):
            self.create_error()

    def test_400_with_unexpected_content_type(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON body: b?'plain'"):
            self.create_error(headers={'Content-Type': 'text/plain'},
                              text='plain')

    def test_400_with_unexpected_content_type(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON body: b?'plain'"):
            self.create_error(text='plain')

    def test_400_with_unexpected_json(self):
        with self.assertRaisesRegex(
            HTTPError,
            'Error response contains JSON but it does not specify code or error keys: b?\'{"not":"expected"}\''):
            self.create_error(text='{"not":"expected"}')

    def test_300_error(self):
        with self.assertRaisesRegex(
            HTTPError, 'Received an unexpected HTTP status \(300\) for'):
            self.create_error(status_code=300)

    def test_500_error(self):
        with self.assertRaisesRegex(HTTPError,
                                    'Received a server error \(500\) for'):
            self.create_error(status_code=500)

    @requests_mock.mock()
    def create_error(self, mock, status_code=400, text='', headers=None):
        if headers is None:
            headers = {
                'Content-Type':
                'application/vnd.maxmind.com-error+json; charset=UTF-8; version=2.0'
            }
        mock.post(self.base_uri + self.type,
                  status_code=status_code,
                  text=text,
                  headers=headers)
        return getattr(self.client, self.type)(self.full_request)

    @requests_mock.mock()
    def create_success(self, mock, text=None, headers=None):
        if headers is None:
            headers = {
                'Content-Type':
                'application/vnd.maxmind.com-minfraud-{}+json; charset=UTF-8; version=2.0'.format(
                    self.type)
            }
        if text is None:
            text = self.response
        mock.post(self.base_uri + self.type,
                  status_code=200,
                  text=text,
                  headers=headers)
        return getattr(self.client, self.type)(self.full_request)


class TestInsights(BaseTest, unittest.TestCase):
    type = 'insights'
    cls = Insights


class TestScore(BaseTest, unittest.TestCase):
    type = 'score'
    cls = Score