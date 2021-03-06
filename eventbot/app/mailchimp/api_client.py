#!/usr/bin/env python
import hashlib
import logging
import requests
import requests_cache

import eventbot.integrations.defaults

# http://developer.mailchimp.com/documentation/mailchimp/guides/get-started-with-mailchimp-api-3/
REGION = "us2"
BASE_URL = 'https://{}.api.mailchimp.com/3.0'.format(REGION)

log = logging.getLogger(__name__)


class TooManyFoundException(Exception):
    pass


class NotFoundException(Exception):
    pass


class MailChimpClient:

    api_key = ''
    list_name = ''
    use_cache = True

    def __init__(
            self,
            api_key,
            cache_timeout=eventbot.integrations.defaults.REQUESTS_CACHE_TIMEOUT,
            use_cache=True
    ):
        self.api_key = api_key
        self.use_cache = use_cache
        if self.use_cache is True:
            requests_cache.install_cache('mailchimp', expire_after=cache_timeout)

    def check_interest(self, email, list_name, interest_category_name, interest_name):
        """ Check whether the specified email address is in the list and has the interest.
        """
        search_result = self.search(email)
        members = search_result['exact_matches']['members']
        if len(members) > 1:
            raise TooManyFoundException("Number of exact matches should never be greater than 1!")
        if len(members) < 1:
            # alt_search_result = self.search(email, alldata=True)
            raise NotFoundException("email {} not found in the database".format(email))
        interest_id = self.lookup_interest_id(list_name, interest_category_name, interest_name)
        return members[0]['interests'].get(interest_id, False)

    def search(self, email, alldata=False):
        """ Search for a member by email.
        """
        if alldata:
            path = '/search-members?query=alldata:{}'.format(email)
        else:
            path = '/search-members?query={}'.format(email)
        o = self._get(path=path)
        return o

    def lookup_interest_id(self, list_name, interest_category_name, interest_name):
        list_id = self.lookup_list_id(list_name)
        interest_category_id = self.lookup_interest_category_id(list_name, interest_category_name)
        o = self.get_interests(list_id, interest_category_id)
        name_id_map = {l['name']: l['id'] for l in o['interests']}
        return name_id_map.get(interest_name, False)

    def lookup_interest_category_id(self, list_name, interest_category_name):
        list_id = self.lookup_list_id(list_name)
        o = self.get_interest_categories(list_id)
        name_id_map = {l['title']: l['id'] for l in o['categories']}
        return name_id_map.get(interest_category_name, False)

    def lookup_list_id(self, name):
        lists = self.get_lists()
        name_id_map = {l['name']: l['id'] for l in lists['lists']}
        return name_id_map.get(name, False)

    def get_interests(self, list_id, interest_category_id):
        path = '/lists/{}/interest-categories/{}/interests'.format(list_id, interest_category_id)
        interests = self._get(path)
        log.debug('{} interest/s returned for list_id={} interest_category_id={}'.format(
            len(interests['interests']),
            list_id,
            interest_category_id)
        )
        return interests

    def get_interest_categories(self, list_id):
        path = '/lists/{}/interest-categories'.format(list_id)
        interest_categories = self._get(path)
        log.debug('{} interest category/ies returned'.format(len(interest_categories['categories'])))
        return interest_categories

    def get_lists(self):
        path = '/lists'
        lists = self._get(path)
        log.debug('{} list/s returned'.format(len(lists['lists'])))
        return lists

    def get_member(self, subscriber_hash, list_id, use_cache=True):
        """ Get member by subscriber hash.
        """
        path = '/lists/{}/members/{}'.format(list_id, subscriber_hash)
        data = self._get(path, use_cache=use_cache)
        return data

    def get_members(self, list_id, params=None):
        """ Look up members by interest.
        """
        path = '/lists/{}/members'.format(list_id)
        data = self._get(path, params=params)
        return data

    def update_member(self, subscriber_hash, list_id, member):
        """ Patch member by subscriber hash.
        """
        path = '/lists/{}/members/{}'.format(list_id, subscriber_hash)
        data = self._patch(path, member)
        return data

    def _get(self, path, params=None, use_cache=True):
        url = '{}{}'.format(BASE_URL, path)
        log.debug(url)
        if use_cache:
            resp = requests.get(url, headers={'Authorization': 'Basic {}'.format(self.api_key)}, params=params)
        else:
            with requests_cache.disabled():
                resp = requests.get(url, headers={'Authorization': 'Basic {}'.format(self.api_key)}, params=params)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path, data):
        url = '{}{}'.format(BASE_URL, path)
        log.debug(url)
        resp = requests.patch(url, headers={'Authorization': 'Basic {}'.format(self.api_key)}, json=data)
        resp.raise_for_status()
        return resp.json()


class MailChimpInterestManager:

    """:type : MailChimpClient"""
    mc = None
    list_name = ''
    list_id = ''
    interest_category_name = ''
    interest_category_id = ''

    def __init__(
            self,
            mc,
            list_name,
            interest_category_name,
    ):
        """
        
        :param mc: MailChimpClient
        :param list_name: basestring
        :param interest_category_name: basestring 
        """
        self.mc = mc
        self.list_name = list_name
        self.list_id = mc.lookup_list_id(self.list_name)
        self.interest_category_name = interest_category_name
        self.interest_category_id = mc.lookup_interest_category_id(list_name, interest_category_name)

    def get_member(self, email_address, use_cache=False):
        """ Get member by subscriber hash.
        """
        subscriber_hash = calculate_subscriber_hash(email_address)
        data = self.mc.get_member(subscriber_hash, self.list_id, use_cache=use_cache)
        return data

    def lookup_interest_id(self, interest_name):
        o = self.mc.get_interests(self.list_id, self.interest_category_id)
        name_id_map = {l['name']: l['id'] for l in o['interests']}
        return name_id_map.get(interest_name, False)

    def lookup_members_by_interest(self, interest_name):
        """ Look up members by interest.
        """
        interest_id = self.lookup_interest_id(interest_name)
        params = {
            'interest_category_id': self.interest_category_id,
            'interest_ids': interest_id,
            'interest_match': 'any'
        }
        with requests_cache.disabled():
            members = self.mc.get_members(self.list_id, params=params)
        return members

    def add_interest(self, member_id, interest_name):
        """
        Add specified interest to member data.
        :param member_id: basestring 
        :param interest_name: basestring
        :return: 
        """
        return self._toggle_interest(member_id, interest_name, True)

    def remove_interest(self, member_id, interest_name):
        """
        Remove specified interest from member data.
        :param member_id: basestring 
        :param interest_name: basestring
        :return: 
        """
        return self._toggle_interest(member_id, interest_name, False)

    def _toggle_interest(self, member_id, interest_name, toggle):
        """
        Toggle specified interest from member data.
        :param member_id: basestring 
        :param interest_name: basestring
        :param toggle: boolean
        :return: 
        """
        interest_id = self.lookup_interest_id(interest_name)
        obj = {
            'interests': {
                interest_id: toggle
            }
        }
        self.mc.update_member(member_id, self.list_id, obj)
        with requests_cache.disabled():
            member = self.mc.get_member(member_id, self.list_id)
        try:
            assert member['interests'][interest_id] is toggle
        except KeyError as ke:
            log.error("KeyError: message={}, interest_id={}, member={}, toggle={}".format(
                ke.message,
                interest_id,
                member,
                toggle
            ))
            raise ke
        except AssertionError as ae:
            log.error("AssertionError: message={}, interest_id={}, member={}, toggle={}".format(
                ae.message,
                interest_id,
                member,
                toggle
            ))
            raise ae
        return member


def calculate_subscriber_hash(email_address):
    m = hashlib.md5()
    m.update(email_address.lower())
    subscriber_hash = m.hexdigest()
    return subscriber_hash


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import pprint
    import sys
    test_apikey = sys.argv[1]
    arg = sys.argv
    pp = pprint.PrettyPrinter(indent=4)
    # result = mc.check_interest(**sys.argv[2])
    # pp.pprint(result)
