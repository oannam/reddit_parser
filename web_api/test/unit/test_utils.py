import unittest
from app import utils


class TestUtilsModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_merge_timestamp_sorted_dict_lists(self):
        list1 = [{'created': x} for x in range(8, 6, -1)]
        list2 = [{'created': x} for x in range(6, 0, -1)]
        merged_list = utils.merge_timestamp_sorted_dict_lists(list1, list2)
        wanted_merged_list = [{'created': x} for x in range(8, 0, -1)]
        self.assertEqual(merged_list, wanted_merged_list)

    def test_create_query_condition(self):
        subreddit = 'stories'
        from_date = 1
        to_date = 2
        query = utils.create_query_condition(
            subreddit, from_date, to_date
        )
        wanted_query = {'subreddit': 'stories', 'created': {'$lte': 2.0, '$gte': 1.0}}
        self.assertEqual(query, wanted_query)

    def test_create_query_condition_with_keyword(self):
        subreddit = 'stories'
        from_date = 1
        to_date = 2
        keyword = 'some_word'
        in_field = 'some_field'
        query = utils.create_query_condition(
            subreddit, from_date, to_date, keyword, in_field
        )
        wanted_query = {
            'subreddit': 'stories',
            'some_field': {'$regex': '.*some_word.*'},
            'created': {'$lte': 2.0, '$gte': 1.0}
        }
        self.assertEqual(query, wanted_query)
