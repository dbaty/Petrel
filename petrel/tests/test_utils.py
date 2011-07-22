from unittest import TestCase


def _convert_nav_tree(tree):
    converted = []
    for i in tree:
        converted.append((i[0].title, _convert_nav_tree(i[1])))
    return converted


class TestUtils(TestCase):

    def setUp(self):
        from petrel.content.site import Site
        self.site = Site()

    def _make_folder(self, folder_id, parent=None):
        from petrel.content.folder import Folder
        folder = Folder()
        folder.title = folder_id
        if parent is None:
            parent = self.site
        parent.add(folder_id, folder)
        return folder

    def _make_doc(self, doc_id, parent=None):
        from petrel.content.document import Document
        doc = Document()
        doc.title = doc_id
        if parent is None:
            parent = self.site
        parent.add(doc_id, doc)
        return doc

    def _make_path(self, path):
        ids = path.split('/')
        parent = self.site
        for obj_id in ids[:-1]:
            if obj_id not in parent:
                self._makeFolder(obj_id, parent)
            parent = parent[obj_id]
        self._makeDoc(ids[-1], parent)

    def assert_trees_equal(self, expected, got):
        return self.assertEqual(expected, _convert_nav_tree(got))

    def test_convert_nav_tree(self):
        ## Test our own test function
        class Dummy:
            def __init__(self, title):
                self.title = title

        self.assertEqual([], _convert_nav_tree([]))
        tree = [(Dummy('foo'), []),
                (Dummy('bar'),
                 [(Dummy('baz'), []), (Dummy('quuz'), [])])]
        expected = [('foo', []), ('bar', [('baz', []), ('quuz', [])])]
        self.assertEqual(expected, _convert_nav_tree(tree))

    ## FIXME: reactivate later
    def _test_get_nav_tree_empty_site(self):
        from petrel.utils import get_nav_tree
        self.assertEqual(get_nav_tree(self.site), [])

    ## FIXME: reactivate later
    def _test_get_nav_tree_only_root_folders(self):
        from petrel.utils import get_nav_tree
        folder1 = self._makeFolder('folder1')
        expected = [('folder1', [])]
        self.assertTreesEqual(get_nav_tree(self.site), expected)
        self.assertTreesEqual(get_nav_tree(folder1), expected)

        folder2 = self._makeFolder('folder2')
        expected = [('folder1', []), ('folder2', [])]
        self.assertTreesEqual(get_nav_tree(self.site), expected)
        self.assertTreesEqual(get_nav_tree(folder1), expected)
        self.assertTreesEqual(get_nav_tree(folder2), expected)

    ## FIXME: reactivate later
    def _test_get_nav_tree_deep_document(self):
        from petrel.utils import get_nav_tree
        self._makePath('folder1/folder11/doc111')
        self._makePath('folder1/folder11/doc112')
        self._makePath('folder1/folder12/doc121')
        self._makePath('folder2/doc21')
        folder1 = self.site['folder1']
        folder11 = folder1['folder11']
        doc111 = folder11['doc111']
        doc112 = folder11['doc112']

        expected = [('folder1', []), ('folder2', [])]
        self.assertTreesEqual(get_nav_tree(self.site), expected)
        self.assertTreesEqual(get_nav_tree(folder1), expected)

        expected = [('folder1', []),
                    ('folder2',
                     [('folder11', [('doc111', []), ('doc112', [])])])]
        self.assertTreesEqual(get_nav_tree(folder11), expected)
        self.assertTreesEqual(get_nav_tree(doc111), expected)
        self.assertTreesEqual(get_nav_tree(doc112), expected)
