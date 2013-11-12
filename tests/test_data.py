from datetime import date, datetime, timedelta

from unittest2 import TestCase

from authorize.data import Address, CreditCard, BankAccount
from authorize.exceptions import AuthorizeInvalidError


TEST_CARD_NUMBERS = [
    ('amex', '370000000000002'),
    ('mc', '5555555555554444'),
    ('mc', '5105105105105100'),
    ('discover', '6011000000000012'),
    ('visa', '4007000000027'),
    ('visa', '4012888818888'),
    ('diners', '38000000000006'),
]

TEST_BANK_ACCOUNT = {'first_name': "Enoon", 'last_name': 'Erehwon',
                     'bank_name': "Knab Bank, NLC",
                     'routing_number': 211073473, 'account_number': 12341234123,
                     'customer_type': 'individual', 'account_type': 'checking',
                     'routing_number_type': 'ABA', 'echeck_type': 'WEB'}
TEST_BANK_ACCOUNT_NUMBERS = [
    ('0110-9966-0', '1234'),
    ('0110-9966-0', '12345678901234567'),
    (111050295, 1234),
    (111050295, 12345678901234567),
]

class CreditCardTests(TestCase):
    def setUp(self):
        self.YEAR = date.today().year + 10

    def test_basic_credit_card(self):
        credit_card = CreditCard('4111-1111-1111-1111', self.YEAR, 1, '911')
        repr(credit_card)

    def test_credit_card_validation(self):
        # Expiration in the past fails
        expired = date.today() - timedelta(days=31)
        self.assertRaises(AuthorizeInvalidError, CreditCard,
            '4111111111111111', expired.year, expired.month, '911')

        # CVV in wrong format fails
        self.assertRaises(AuthorizeInvalidError, CreditCard,
            '4111111111111111', self.YEAR, 1, 'incorrect')

        # Invalid credit card number fails
        self.assertRaises(AuthorizeInvalidError, CreditCard,
            '4111111111111112', self.YEAR, 1, '911')

        # Test standard test credit card numbers that should validate
        for card_type, card_number in TEST_CARD_NUMBERS:
            CreditCard(card_number, self.YEAR, 1, '911')

    def test_credit_card_type_detection(self):
        for card_type, card_number in TEST_CARD_NUMBERS:
            credit_card = CreditCard(card_number, self.YEAR, 1, '911')
            self.assertEqual(credit_card.card_type, card_type)

    def test_credit_card_expiration(self):
        credit_card = CreditCard('4111111111111111', self.YEAR, 1, '911')
        self.assertEqual(credit_card.expiration,
            datetime(self.YEAR, 1, 31, 23, 59, 59))

    def test_credit_card_safe_number(self):
        credit_card = CreditCard('4111111111111111', self.YEAR, 1, '911')
        self.assertEqual(credit_card.safe_number, '************1111')


class BankAccountTests(TestCase):
    def setUp(self):
        pass

    def _bank_account(self, **kwargs):
        """Update test acct from kwargs and return :class:`BankAccount`"""
        return BankAccount(**dict(TEST_BANK_ACCOUNT, **kwargs))

    def test_individual_checking_account(self):
        bank_account = self._bank_account(customer_type='individual',
                                          account_type='checking')
        repr(bank_account)

    def test_individual_savings_account(self):
        bank_account = self._bank_account(customer_type='individual',
                                          account_type='savings')
        repr(bank_account)
    
    def test_business_checking_account(self):
        bank_account = self._bank_account(customer_type='business',
                                          account_type='businessChecking',
                                          company_name='Seatec Astronomy')
        repr(bank_account)

    def test_bank_account_first_and_last_name_validation(self):
        """Ensure missing first or last name fails"""
        self.assertRaises(AuthorizeInvalidError, BankAccount, first_name=None)
        self.assertRaises(AuthorizeInvalidError, BankAccount, first_name='')
        self.assertRaises(AuthorizeInvalidError, BankAccount, last_name=None)
        self.assertRaises(AuthorizeInvalidError, BankAccount, last_name='')

    def test_bank_account_bank_name_validation(self):
        """Ensure missing bank name fails"""
        self.assertRaises(AuthorizeInvalidError, BankAccount, bank_name=None)
        self.assertRaises(AuthorizeInvalidError, BankAccount, bank_name='')

    def test_bank_account_customer_type_validation(self):
        """Ensure missing or invalid customer_type fails"""
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, customer_type=None)
        self.assertRaises(AuthorizeInvalidError, BankAccount, customer_type='')
        self.assertRaises(AuthorizeInvalidError, BankAccount, customer_type='X')

    def test_bank_account_account_type_validation(self):
        """Ensure missing or invalid account type fails"""
        self.assertRaises(AuthorizeInvalidError, BankAccount, account_type=None)
        self.assertRaises(AuthorizeInvalidError, BankAccount, account_type='')
        self.assertRaises(AuthorizeInvalidError, BankAccount, account_type='X')

    def test_bank_account_routing_number_type_validation(self):
        """Ensure missing or invalid routing number type fails"""
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number_type=None)
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number_type='')
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number_type='X')

    def test_bank_account_echeck_type_validation(self):
        """Ensure missing or invalid eCheck type fails"""
        self.assertRaises(AuthorizeInvalidError, BankAccount, echeck_type=None)
        self.assertRaises(AuthorizeInvalidError, BankAccount, echeck_type='')
        self.assertRaises(AuthorizeInvalidError, BankAccount, echeck_type='X')

    def test_bank_account_routing_number_validation(self):
        """Ensure missing or invalid routing number fails"""

        # Missing routing number fails
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number=None)
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number='')
        # Invalid routing number length fails
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number=12341234)
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number=1234567890)
        # Invalid account number length fails
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number=123)
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number=123456789012345678)
        # Alpha values in routing number fails
        self.assertRaises(AuthorizeInvalidError,
                          BankAccount, routing_number='01100001X')
        # Test standard test bank routing numbers that should validate
        for aba_number, acct_number in TEST_BANK_ACCOUNT_NUMBERS:
            bank_account = self._bank_account(routing_number=aba_number,
                                              account_number=acct_number)
            self.assertEquals(bank_account.routing_number,
                              str(aba_number).replace('-', ''))

    def test_bank_account_safe_number(self):
        bank_account = self._bank_account(account_number='12345678912345678')
        self.assertEqual(bank_account.safe_number, '*************5678')


class AddressTests(TestCase):
    def test_basic_address(self):
        address = Address('45 Rose Ave', 'Venice', 'CA', '90291')
        repr(address)
