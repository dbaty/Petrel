from unittest import TestCase


class TestDocument(TestCase):

    def _make_one(self):
        from petrel.content.document import Document
        return Document()

    def test_init(self):
        site = self._make_one()
        self.assertEqual(site.title, u'')
        self.assertEqual(site.body, u'')
