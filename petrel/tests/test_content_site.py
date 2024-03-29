from unittest import TestCase


class TestSite(TestCase):

    def _make_one(self):
        from petrel.content.site import Site
        return Site()

    def test_init(self):
        site = self._make_one()
        self.assertEqual(site.title, u'Site')
        self.assertEqual(site.body, u'')
