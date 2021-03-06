"""
This module provides the data structures for describing credit cards and
addresses for use in executing charges.
"""

import calendar
from datetime import datetime
import re

from authorize.exceptions import AuthorizeInvalidError

CARD_TYPES = {
    'visa': r'4\d{12}(\d{3})?$',
    'amex': r'37\d{13}$',
    'mc': r'5[1-5]\d{14}$',
    'discover': r'6011\d{12}',
    'diners': r'(30[0-5]\d{11}|(36|38)\d{12})$'
}

CUSTOMER_TYPES = ('individual', 'business')
ACCOUNT_TYPES = ('checking', 'savings', 'businessChecking')
ROUTING_NUMBER_TYPES = ('ABA', 'IBAN', 'SWIFT')
ECHECK_TYPES = ('ARC', 'BOC', 'CCD', 'PPD', 'TEL', 'WEB')


class CreditCard(object):
    """
    Represents a credit card that can be charged.
    
    Pass in the credit card number, expiration date, CVV code, and optionally
    a first name and last name. The card will be validated upon instatiation
    and will raise an
    :class:`AuthorizeInvalidError <authorize.exceptions.AuthorizeInvalidError>`
    for invalid credit card numbers, past expiration dates, etc.
    """
    def __init__(self, card_number=None, exp_year=None, exp_month=None,
                cvv=None, first_name=None, last_name=None):
        self.card_number = re.sub(r'\D', '', str(card_number))
        self.exp_year = str(exp_year)
        self.exp_month = str(exp_month)
        self.cvv = str(cvv)
        self.first_name = first_name
        self.last_name = last_name
        self.validate()

    def __repr__(self):
        return '<CreditCard {0.card_type} {0.safe_number}>'.format(self)

    def validate(self):
        """
        Validates the credit card data and raises an
        :class:`AuthorizeInvalidError <authorize.exceptions.AuthorizeInvalidError>`
        if anything doesn't check out. You shouldn't have to call this
        yourself.
        """
        try:
            num = map(int, self.card_number)
        except ValueError:
            raise AuthorizeInvalidError('Credit card number is not valid.')
        if sum(num[::-2] + map(lambda d: sum(divmod(d * 2, 10)), num[-2::-2])) % 10:
            raise AuthorizeInvalidError('Credit card number is not valid.')
        if datetime.now() > self.expiration:
            raise AuthorizeInvalidError('Credit card is expired.')
        if not re.match(r'^[\d+]{3,4}$', self.cvv):
            raise AuthorizeInvalidError('Credit card CVV is invalid format.')
        if not self.card_type:
            raise AuthorizeInvalidError('Credit card number is not valid.')

    @property
    def expiration(self):
        """
        The credit card expiration date as a ``datetime`` object.
        """
        return datetime(int(self.exp_year), int(self.exp_month),
            calendar.monthrange(int(self.exp_year), int(self.exp_month))[1],
            23, 59, 59)

    @property
    def safe_number(self):
        """
        The credit card number with all but the last four digits masked. This
        is useful for storing a representation of the card without keeping
        sensitive data.
        """
        mask = '*' * (len(self.card_number) - 4)
        return '{0}{1}'.format(mask, self.card_number[-4:])

    @property
    def card_type(self):
        """
        The credit card issuer, such as Visa or American Express, which is
        determined from the credit card number. Recognizes Visa, American
        Express, MasterCard, Discover, and Diners Club.
        """
        for card_type, card_type_re in CARD_TYPES.items():
            if re.match(card_type_re, self.card_number):
                return card_type


class BankAccount(object):
    """
    Represents a bank account that can be charged.
    
    Pass in a US bank account number, expiration date, CVV code, and optionally
    a first name and last name. The account will be validated upon instantiation
    and will raise an
    :class:`AuthorizeInvalidError <authorize.exceptions.AuthorizeInvalidError>`
    for invalid bank account numbers, past expiration dates, etc.
    """
    def __init__(self, first_name=None, last_name=None, company=None,
                 bank_name=None, routing_number=None, account_number=None,
                 customer_type='individual', account_type='checking',
                 routing_number_type='ABA', echeck_type='WEB'):
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.bank_name = bank_name
        self.routing_number = re.sub(r'[^0-9A-Za-z]', '', str(routing_number))
        self.account_number = re.sub(r'\D', '', str(account_number))
        self.customer_type = customer_type
        self.account_type = account_type
        self.routing_number_type = routing_number_type
        self.echeck_type = echeck_type
        self.validate()

    def __repr__(self):
        return '<BankAccount {0.account_type} ' \
               '{0.routing_number} {0.safe_number}>'.format(self)

    def validate(self):
        """
        Validates the bank account data and raises an
        :class:`AuthorizeInvalidError <authorize.exceptions.AuthorizeInvalidError>`
        if anything doesn't check out. You shouldn't have to call this
        yourself.
        """
        if self.first_name is None or not self.first_name.strip():
            raise AuthorizeInvalidError('First name on account is required.')
        if self.last_name is None or not self.last_name.strip():
            raise AuthorizeInvalidError('Last name on account is required.')
        if self.customer_type == 'business':
            if self.company is None or not self.company.strip():
                raise AuthorizeInvalidError('Company name is required.')
        if self.bank_name is None or not self.bank_name.strip():
            raise AuthorizeInvalidError('Bank name is required.')
        if self.routing_number is None or not self.routing_number.strip():
            raise AuthorizeInvalidError('Routing number is required.')
        if self.account_number is None or not self.account_number.strip():
            raise AuthorizeInvalidError('Account number is required.')
        if self.customer_type is None or not self.customer_type.strip():
            raise AuthorizeInvalidError('Customer type is required.')
        if self.customer_type not in CUSTOMER_TYPES:
            raise AuthorizeInvalidError('Customer type is not valid.')
        if self.account_type is None or not self.account_type.strip():
            raise AuthorizeInvalidError('Bank account type is required.')
        if self.account_type not in ACCOUNT_TYPES:
            raise AuthorizeInvalidError('Bank account type is not valid.')
        if self.routing_number_type is None \
                or not self.routing_number_type.strip():
            raise AuthorizeInvalidError('Routing number type is required.')
        if self.routing_number_type not in ROUTING_NUMBER_TYPES:
            raise AuthorizeInvalidError('Routing number is not valid.')
        if self.echeck_type is None or not self.echeck_type.strip():
            raise AuthorizeInvalidError('eCheck type is required.')
        if self.echeck_type not in ECHECK_TYPES:
            raise AuthorizeInvalidError('eCheck type is not valid.')
        self._validate_account_number(self.account_number)
        self._validate_aba(self.routing_number)

    @staticmethod
    def _validate_account_number(account_number):
        num = map(int, account_number)
        if not (len(num) >= 5 and len(num) <= 17):
            raise AuthorizeInvalidError('Bank account number is not valid.')

    @staticmethod
    def _validate_aba(routing_number):
        """
        Validates a US ABA standard MICR routing number and raises an
        :class:`AuthorizeInvalidError <authorize.exceptions.AuthorizeInvalidError>`
        if anything doesn't check out.
        """
        try:
            num = map(int, routing_number)
        except (ValueError, TypeError):
            raise AuthorizeInvalidError('Bank routing number is not valid.')
        if len(routing_number) != 9:
            raise AuthorizeInvalidError('Bank routing number is not valid.')
        checksum = (7 * (num[0] + num[3] + num[6]) +
                    3 * (num[1] + num[4] + num[7]) +
                    9 * (num[2] + num[5])) % 10
        if num[8] != checksum:
            raise AuthorizeInvalidError('Bank routing number is not valid.')

    @property
    def safe_number(self):
        """
        The bank account number with all but the last four digits masked. This
        is useful for storing a representation of the account without keeping
        sensitive data.
        """
        mask = '*' * (len(self.account_number) - 4)
        return '{0}{1}'.format(mask, self.account_number[-4:])

class Address(object):
    """
    Represents a billing address for a charge. Pass in the street, city, state
    and zip code, and optionally country for the address.
    """
    def __init__(self, street=None, city=None, state=None, zip_code=None,
            country='US'):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return '<Address {0.street}, {0.city}, {0.state} {0.zip_code}>' \
            .format(self)
