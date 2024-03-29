from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

import testtools

import resources.lib.classes as classes
from resources.tests.fakes import fakes

try:
    import mock
except ImportError:
    import unittest.mock as mock


class ClassesTests(testtools.TestCase):

    @mock.patch('aussieaddonscommon.utils.get_addon_version')
    def test_make_kodi_url(self, mock_version):
        mock_version.return_value = '1.0.0'
        video = classes.Video()
        attrs = OrderedDict(
            sorted(fakes.FAKE_VIDEO_ATTRS.items(), key=lambda x: x[0]))
        for k, v in attrs.items():
            setattr(video, k, v)
        self.assertEqual(fakes.FAKE_VIDEO_URL, video.make_kodi_url())

    @mock.patch('aussieaddonscommon.utils.get_addon_version')
    def test_parse_kodi_url(self, mock_version):
        mock_version.return_value = '1.0.0'
        video = classes.Video()
        video.parse_kodi_url(fakes.FAKE_VIDEO_URL)
        observed = video.make_kodi_url()
        self.assertEqual(fakes.FAKE_VIDEO_URL, observed)

    @mock.patch.object(classes.Video, 'get_tz_delta', lambda x: 11)
    def test_get_airtime(self):
        video = classes.Video()
        video.parse_kodi_url(fakes.FAKE_VIDEO_URL)
        expected = 'Saturday 25 Jan @ 10:30 AM'
        self.assertEqual(expected, video.get_airtime())
