from __future__ import absolute_import, unicode_literals

import io
import os

import responses

import testtools

import resources.lib.classes as classes
import resources.lib.comm as comm
import resources.lib.config as config


class CommTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/CONFIG.json'), 'rb') as f:
            self.CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MATCHES_FIXTURE.json'),
                  'rb') as f:
            self.MATCHES_FIXTURE_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MATCHES_SUMMARY.json'),
                  'rb') as f:
            self.MATCHES_SUMMARY_JSON = io.BytesIO(f.read()).read()

    @responses.activate
    def test_fetch_url(self):
        responses.add(responses.GET, 'http://foo.bar/',
                      body=u'Hello World', status=200)
        observed = comm.fetch_url('http://foo.bar/').decode('utf-8')
        self.assertEqual(observed, 'Hello World')

    @responses.activate
    def test_list_comps(self):
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.CONFIG_JSON, status=200)
        listing = comm.list_comps({})
        self.assertEqual(8, len(listing))
        self.assertEqual('Hyundai A-League', listing[0].title)

    @responses.activate
    def test_list_rounds(self):
        responses.add(responses.GET,
                      config.MATCHES_URL.format('c214/s2019/summary'),
                      body=self.MATCHES_SUMMARY_JSON, status=200)
        observed = comm.list_rounds({'id': '214', 'active_season': '2019'})
        expected = classes.Category()
        expected.title = 'Round 16'
        expected.rnd = '16'
        expected.id = '214'
        expected.active_season = '2019'
        for attrib in vars(observed[0]):
            self.assertEqual(getattr(expected, attrib),
                             getattr(observed[0], attrib))

    @responses.activate
    def test_list_matches_non_team(self):
        responses.add(responses.GET,
                      config.MATCHES_URL.format('c214/s2019/r9/fixture'),
                      body=self.MATCHES_FIXTURE_JSON, status=200)
        observed = comm.list_matches({'id': '214', 'active_season': '2019',
                                      'rnd': '9'})
        self.assertEqual(5, len(observed))
        self.assertEqual(6114100255001, observed[4].video_id)
