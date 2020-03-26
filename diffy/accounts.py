"""
.. module: diffy.accounts
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from rapidfuzz import process

from honeybee.extensions import swag
from honeybee.exceptions import ResolveException

log = logging.getLogger(__name__)


def get_fuzzy_accounts(identifier, accounts):
    """Attempts to fuzz identifier and provides suggestions.

    :param identifier: identifier to fuzz
    :param accounts: list of accounts to compare
    :return: tuple. Possible accounts that could match.
    """
    # collect all possibilities
    choices = []
    for a in accounts:
        choices.append(a["name"])
        choices += a["aliases"]

    return process.extract(identifier, choices, limit=3)


def valid_account(identifier):
    """Validates account identifier.

    :param identifier: identifier to validate
    :return: bool. ``True``
    """
    account = get_account_id(identifier)
    if account:
        return True


def get_account_name(identifier):
    """Fetches account name from SWAG.

    :param identifier: identifier to fetch
    """
    log.debug(f"Fetching account information. Name: {identifier}")
    account_data = swag.get(f"[?id=='{identifier}']")

    if not account_data:
        raise ResolveException(
            f"Unable to find any account information. Identifier: {identifier}"
        )

    return account_data["name"]


def get_account_id(identifier):
    """Fetches account id from SWAG.

    :param identifier: identifier to fetch
    """
    log.debug(f"Fetching account information. Identifier: {identifier}")
    account_data = swag.get(f"[?id=='{identifier}']")

    if not account_data:
        account_data = swag.get_by_name(identifier, alias=True)

        if not account_data:
            raise ResolveException(
                f"Unable to find any account information. Identifier: {identifier}"
            )

        if len(account_data) > 1:
            raise ResolveException(
                f"Unable to resolve to a single account. Accounts: {len(account_data)} Identifier: {identifier}"
            )

        return account_data[0]["id"]
    return account_data["id"]
