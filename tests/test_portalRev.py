from unittest import TestCase
from check_portal_rev import PortalRev
from naglib.nagiosplugin import NAG_RESP_CLASSES, NAG_OK, NAG_WARNING, NAG_CRITICAL

__author__ = 'jaclu'


K_HOST = 'host'
K_BRANCH = 'branch'
K_BUILD = 'build'
K_REV = 'rev'
K_VERS = 'vers'

class PortalRevTestBase(TestCase):
    def setUp(self):
        self._reference_values = {K_HOST:'http://www.europeana.eu'}

        code,self._entire_response = PortalRev([self._reference_values['host']]).run()
        self.assertEquals(code, NAG_OK, 'Failed to find example params!')
        self.assertEqual(self._entire_response.split(':')[0], 'OK', 'Test did not result with OK!')
        for part in self._entire_response.split():
            parts2 = part.split(':')
            key = parts2[0]
            if key == 'OK':
                continue  # special case don't store this one
            self.assertIn(key, (K_HOST, K_BRANCH, K_BUILD, K_REV, K_VERS),'Invalid key field: %s' % key)
            value = ':'.join(parts2[1:])
            self._reference_values[key] = value



class TestPortalRevTestCase(PortalRevTestBase):

    def test_two_params(self):
        self.test_rev_good()
        self.test_rev_bad()
        self.test_version_good()
        self.test_version_wrong()




    def test_rev_good(self):
        code, msg = PortalRev([self._reference_values[K_HOST], '-r', self._reference_values[K_REV]]).run()
        self.assertEqual(code, NAG_OK,'correct revision should not fail')
        self.assertEqual(msg.split(':')[0], 'OK','correct revision should be labeled OK')

    def test_rev_bad(self):
        code, msg = PortalRev([self._reference_values[K_HOST], '-r', 'NOWAY']).run()
        self.assertEqual(code, NAG_CRITICAL,'revision NOWAY should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], 'ERROR','revision NOWAY should be labeled ERROR')

    def test_version_good(self):
        code, msg = PortalRev([self._reference_values[K_HOST], '-V', self._reference_values[K_VERS]]).run()
        self.assertEqual(code, NAG_OK,'correct revision should not fail')
        self.assertEqual(msg.split(':')[0], 'OK','correct revision should be labeled OK')


    def test_version_wrong(self):
        code, msg = PortalRev([self._reference_values[K_HOST],'-V','NOWAY']).run()
        self.assertEqual(code, NAG_CRITICAL,'version NOWAY should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], 'ERROR','version NOWAY should be labeled ERROR')



