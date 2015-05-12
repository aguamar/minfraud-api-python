from __future__ import unicode_literals

import sys

from minfraud.models import *

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest


class TestModels(unittest.TestCase):
    def test_billing_address(self):
        address = BillingAddress(self.address_dict)
        self.check_address(address)

    def test_shipping_address(self):
        address_dict = self.address_dict
        address_dict['is_high_risk'] = False
        address_dict['distance_to_billing_address'] = 200

        address = ShippingAddress(address_dict)
        self.check_address(address)
        self.assertEqual(False, address.is_high_risk)
        self.assertEqual(200, address.distance_to_billing_address)

    @property
    def address_dict(self):
        return {
            'is_in_ip_country': True,
            'latitude': 43.1,
            'longitude': 32.1,
            'distance_to_ip_location': 100,
            'is_postal_in_city': True
        }

    def check_address(self, address):
        self.assertEqual(True, address.is_in_ip_country)
        self.assertEqual(True, address.is_postal_in_city)
        self.assertEqual(100, address.distance_to_ip_location)
        self.assertEqual(32.1, address.longitude)
        self.assertEqual(43.1, address.latitude)

    def test_credit_card(self):
        cc = CreditCard({
            'issuer': {'name': 'Bank'},
            'country': 'US',
            'is_issued_in_billing_address_country': True,
            'is_prepaid': True
        })

        self.assertEqual('Bank', cc.issuer.name)
        self.assertEqual('US', cc.country)
        self.assertEqual(True, cc.is_prepaid)
        self.assertEqual(True, cc.is_issued_in_billing_address_country)

    def test_geoip2_country(self):
        country = GeoIP2Country(is_high_risk=True, iso_code='US')
        self.assertEqual(True, country.is_high_risk)
        self.assertEqual('US', country.iso_code)

    def test_geoip2_location(self):
        time = "2015-04-19T12:59:23-01:00"
        location = GeoIP2Location(local_time=time, latitude=5)
        self.assertEqual(time, location.local_time)
        self.assertEqual(5, location.latitude)

    def test_ip_location(self):
        time = "2015-04-19T12:59:23-01:00"
        loc = IPLocation({
            'country': {'is_high_risk': True},
            'location': {'local_time': time}
        })

        self.assertEqual(time, loc.location.local_time)
        self.assertEqual(True, loc.country.is_high_risk)

    def test_insights(self):
        id = "b643d445-18b2-4b9d-bad4-c9c4366e402a"
        insights = Insights({
            'id': id,
            'ip_location': {'country': {'iso_code': 'US'}},
            'credit_card': {'is_prepaid': True},
            'shipping_address': {'is_in_ip_country': True},
            'billing_address': {'is_in_ip_country': True},
            'credits_remaining': 123,
            'risk_score': 0.01,
            'warnings': [{"code": "INVALID_INPUT"}]
        })

        self.assertEqual('US', insights.ip_location.country.iso_code)
        self.assertEqual(True, insights.credit_card.is_prepaid)
        self.assertEqual(True, insights.shipping_address.is_in_ip_country)
        self.assertEqual(True, insights.billing_address.is_in_ip_country)
        self.assertEqual(id, insights.id)
        self.assertEqual(123, insights.credits_remaining)
        self.assertEqual(0.01, insights.risk_score)
        self.assertEqual("INVALID_INPUT", insights.warnings[0].code)

    def test_issuer(self):
        phone = '132-342-2131'

        issuer = Issuer({
            'name': 'Bank',
            'matches_provided_name': True,
            'phone_number': phone,
            'matches_provided_phone_number': True
        })

        self.assertEqual('Bank', issuer.name)
        self.assertEqual(True, issuer.matches_provided_name)
        self.assertEqual(phone, issuer.phone_number)
        self.assertEqual(True, issuer.matches_provided_phone_number)

    def test_score(self):
        id = 'b643d445-18b2-4b9d-bad4-c9c4366e402a'
        insights = Insights({
            'id': id,
            'credits_remaining': 123,
            'risk_score': 0.01,
            'warnings': [{'code': 'INVALID_INPUT'}],
        })

        self.assertEqual(id, insights.id)
        self.assertEqual(123, insights.credits_remaining)
        self.assertEqual(0.01, insights.risk_score)
        self.assertEqual('INVALID_INPUT', insights.warnings[0].code)

    def test_warning(self):
        code = 'INVALID_INPUT'
        msg = 'Input invalid'

        warning = Warning(
            {'code': code,
             'warning': msg,
             'input': ["first", "second"]})

        self.assertEqual(code, warning.code)
        self.assertEqual(msg, warning.warning)
        self.assertEqual(['first', 'second'], warning.input)
