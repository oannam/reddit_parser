import unittest
from mock import mock
# from unittest.mock import patch
from parser import Config, SubredditSubmissionsManager


class TestParser(unittest.TestCase):

    def setUp(self):
        self.manager_result_in_db = []
        self.mock_reddit_client = mock.Mock()
        last_items = {
            "stories": ([1, 2], [3, 4]),
            "jokes": ([5, 6], [7, 8])
        }
        self.mock_reddit_client.get_last_submissions_and_comments = lambda x: last_items[x]

        self.mock_object_dbwriter = mock.Mock()
        self.mock_object_dbwriter.bulk_write = lambda x, y: self.manager_result_in_db.append((x, y))

    def test_config(self):
        conf = Config('test/unit/test_config.yaml', section='DEFAULT')
        self.assertEqual(conf.REDDIT['USER'], '<user>')

    def test_subreddit_submission_manager(self):
        submissions_collection = "submissions"
        comments_collection = "comments"
        subreddits = ['stories', 'jokes']

        manager = SubredditSubmissionsManager(
            self.mock_reddit_client,
            self.mock_object_dbwriter,
            submissions_collection,
            comments_collection,
            subreddits
        )

        manager.grab_submissions()

        self.assertEqual(
            self.manager_result_in_db,
            [
                ('submissions', [1, 2]),
                ('comments', [3, 4]),
                ('submissions', [5, 6]),
                ('comments', [7, 8])
            ]
        )
