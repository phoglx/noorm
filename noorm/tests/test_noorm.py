import unittest

from noorm.noorm import NoORM

class TestNoORM(unittest.TestCase):
    @staticmethod
    def compare_results(res1, res2):
        def normalize(res):
            if isinstance(res, dict):
                return res
            elif isinstance(res, list):
                return {i['id']: i for i in res}

        def compare_dicts(d1, d2):
            assert len(d1) == len(d2)
            for key in d1:
                if isinstance(d1[key], dict):
                    assert isinstance(d2[key], dict)
                    compare_dicts(d1[key], d2[key])
                elif isinstance(d1[key], list):
                    assert isinstance(d2[key], list)
                    compare_dicts(normalize(d1[key]), normalize(d2[key]))
                elif isinstance(d1[key], (int, long, str, unicode)):
                    assert isinstance(d2[key], type(d1[key]))
                    assert d1[key] == d2[key]
                else:
                    assert False, "unexpected data: {}, {}".format(type(d1[key]), type(d2[key]))

        compare_dicts(normalize(res1), normalize(res2))

    def test_compare_results(self):
        testdata1 = {
            u'foo': [{'stuff': u'things', 'bar': u'baz', 'id': 1}, {'stuff': u'yay', 'bar': u'wooot', 'id': 2}],
            u'bar': [{'stuff': u'yoo!', 'bar': u'foo', 'id': 1}, {'stuff': u'...', 'bar': u':-(', 'id': 2}]}
        same_as_testdata1_but_2nd_list_has_different_order = {
            u'foo': [{'stuff': u'things', 'bar': u'baz', 'id': 1}, {'stuff': u'yay', 'bar': u'wooot', 'id': 2}],
            u'bar': [{'stuff': u'...', 'bar': u':-(', 'id': 2}, {'stuff': u'yoo!', 'bar': u'foo', 'id': 1}]}
        slightly_different_dict = {
            u'foo': [{'bar': u'baz', 'id': 1}, {'stuff': u'yay', 'bar': u'wooot', 'id': 2}],
            u'bar': [{'stuff': u'yoo!', 'bar': u'foo', 'id': 1}, {'stuff': u'...', 'bar': u':-(', 'id': 2}]}
        self.compare_results(testdata1, same_as_testdata1_but_2nd_list_has_different_order)
        success = False
        try:
            self.compare_results(testdata1, slightly_different_dict)
        except AssertionError:
            success = True
        if not success:
            raise AssertionError('comparation succeeded falsely for testdata1, slightly_different_dict')
        success = False
        try:
            self.compare_results(same_as_testdata1_but_2nd_list_has_different_order, slightly_different_dict)
        except AssertionError:
            success = True
        if not success:
            raise AssertionError('comparation succeeded falsely for same_as_testdata1, slightly_different_dict')
        self.compare_results({}, {})

    def test_insert(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})

    def test_update(self):
        with NoORM(':memory:') as ssql:
            ssql['foo'].insert({'bar': 'baz', 'stuff': 'things'})
            data = ssql['foo'][1]
            data['bar'] = 'updated'
            ssql['foo'].update(data)
            self.compare_results(ssql.dump(), {u'foo': [{'stuff': u'things', 'bar': u'updated', 'id': 1}]})

    def test_faulty_insert_with_id(self):
        with NoORM(':memory:') as ssql:
            try:
                ssql['foo'].insert({'stuff': u'things', 'bar': u'updated', 'id': 1})
            except Exception as ex:
                if ex.message != "'id' may not be in the dictionary. Did you want to use update(...)":
                    raise

    def test_id_query(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            result = tbl[1]
            assert isinstance(result, dict)
            expected_result = {'id': 1, 'bar': u'baz', 'stuff': u'things'}
            assert len(result) == len(expected_result)
            assert all(result[key] == expected_result[key] for key in expected_result)

    def test_slice_query(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            result = tbl[2:10:2]
            assert len(result) == 1
            result = result[0]
            assert result['stuff'] == u'yay'
            assert result['bar'] == u'wooot'
            assert result['id'] == 2

    def test_get_all(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            result = tbl['*']
            expected_result = [{'stuff': u'things', 'bar': u'baz', 'id': 1},
                               {'stuff': u'yay', 'bar': u'wooot', 'id': 2}]
            self.compare_results(result, expected_result)

    def test_get_str_err(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            try:
                tbl['whatever']
            except TypeError as te:
                if te.message != "<type 'str'> is not supported: whatever":
                    raise

    def test_dump(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            tbl = ssql['bar']
            tbl.insert({'bar': 'foo', 'stuff': 'yoo!'})
            tbl.insert({'bar': ':-(', 'stuff': '...'})
            result = ssql.dump()
            expected_result = {
                u'foo': [{'stuff': u'things', 'bar': u'baz', 'id': 1}, {'stuff': u'yay', 'bar': u'wooot', 'id': 2}],
                u'bar': [{'stuff': u'yoo!', 'bar': u'foo', 'id': 1}, {'stuff': u'...', 'bar': u':-(', 'id': 2}]}
            self.compare_results(result, expected_result)

    def test_dict_query(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            tbl = ssql['bar']
            tbl.insert({'bar': 'foo', 'stuff': 'yoo!'})
            tbl.insert({'bar': ':-(', 'stuff': '...'})
            result = ssql['bar'][{'bar': 'foo'}]
            expected_result = [{'stuff': u'yoo!', 'bar': u'foo', 'id': 1}]
            self.compare_results(result, expected_result)

    def test_raname_table(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            ssql.rename_table('foo', 'bar')
            result = ssql['bar'][{'bar': 'baz'}]
            expected_result = [{'stuff': u'things', 'bar': u'baz', 'id': 1}]
            self.compare_results(result, expected_result)

    def test_drop_table(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            tbl.insert({'bar': 'wooot', 'stuff': 'yay'})
            assert 'foo' in ssql.dump()
            ssql.drop_table('foo')
            assert 'foo' not in ssql.dump()

    def test_wrong_query(self):
        with NoORM(':memory:') as ssql:
            tbl = ssql['foo']
            tbl.insert({'bar': 'baz', 'stuff': 'things'})
            try:
                tbl[('tuple', 'of', 'strings')]
            except TypeError as te:
                if te.message != "<type 'tuple'> is not supported: ('tuple', 'of', 'strings')":
                    raise

    def test_table_info(self):
        with NoORM(':memory:') as ssql:
            ssql['foo'].insert({'bar': 'baz', 'stuff': 'things'})
            ssql['bar']
            tbl_info = ssql.get_table_info()
            assert len(tbl_info) == 1
            assert len(tbl_info[u'foo']) == 3
            assert tbl_info[u'foo'][u'id'] == 0
            assert tbl_info[u'foo'][u'stuff'] == 1
            assert tbl_info[u'foo'][u'bar'] == 2
