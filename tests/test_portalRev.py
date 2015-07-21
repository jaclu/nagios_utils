from unittest import TestCase
from check_portal_rev import PortalRev

__author__ = 'jaclu'


class TestPortalRev(TestCase):
    def test_custom_options(self):
        self.fail()

    def test_two_params(self):
        pr = PortalRev
        self.ass assertRaises(Exception,pr.run,'http://www.europeana.eu')