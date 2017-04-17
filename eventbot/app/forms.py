# from flask_wtf import FlaskForm
# from wtforms import Form, StringField

import logging
import pprint

log = logging.getLogger(__name__)

pp = pprint.PrettyPrinter(indent=4)

# ImmutableMultiDict([
# ('Field17', u''),
# ('Field14', u'Other site'),
# ('Field12', u'My interests'),
# ('HandshakeKey', u''),
# ('Field11', u'Myself'),
# ('Field27', u'Dafydd referral'),
# ('Field17-url', u''),
# ('Field3', u'Dafydd name'),
# ('DateCreated', u'2017-01-14 05:04:00'),
# ('Field5', u'dafydd@afterpandora.com'),
# ('Field6', u'DuffX'),
# ('EntryId', u'924'),
# ('IP', u'86.155.134.187'),
# ('CreatedBy', u'public'),
# ('Field8', u'Fetlife')])


class ApplicationForm:
    name = None
    email = None
    bio = None
    interests = None
    imageUrl = None

    def __init__(self, data):
        self.name = data['Field3']
        self.email = data['Field5']
        self.bio = data['Field11']
        self.interests = data['Field12']
        self.imageUrl = data['Field17-url']

    def values(self):
        """ Return all values as a dict, with more user-friendly names.
        """
        return {
            'name': self.name,
            'email': self.email,
            'bio': self.bio,
            'interests': self.interests,
            'imageUrl': self.imageUrl,
        }
