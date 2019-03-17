"""
Python 2.7 script that parses given list of subreddits for new submissions and comments and submits
them into a database
"""

import argparse
import backoff
import logging
import praw
import pymongo
from pymongo import errors as pymongo_errors
from requests import exceptions as requests_exceptions
import time
import yaml

DEFAULT = 'DEFAULT'
TEST = 'TEST'
DEV = 'DEV'

# logger to be used throughout the script
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Submission:
    """
    Submission object structure with:
        - own unique id (Reddit's), which will replace the DB's one
        - created field on which second index will be genereated
    """
    def __init__(self, id, title, created, subreddit):
        self._id = id
        self.title = title
        self.created = created
        self.subreddit = subreddit


class Comment:
    """
    Comment object structure with:
        - own unique id (Reddit's), which will replace the DB's one
        - created field on which second index will be genereated
    """
    def __init__(self, id, title, created, subreddit):
        self._id = id
        self.text = title
        self.created = created
        self.subreddit = subreddit


class RedditConnectionError(Exception):
    """Exception to wrap Reddit client connection error"""
    pass

class DBConnectionError(Exception):
    """Exception to wrap MongoDB connection error exception or any other DBs"""
    pass


class Singleton(type):
    """Singleton metaclass to be used as a class for all the singleton classes"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(object):
    """Config that reads the configuration from given yaml and section"""
    __metaclass__ = Singleton

    def __init__(self, config_file, section=DEFAULT):
        self.__config_file = config_file
        self.__section = section
        self.__config = self.__read_config()
        self.__add_attrs()

    def __read_config(self):
        logger.info(
            "Read configuration from file: {0} using section: {1}".format(
                self.__config_file,
                self.__section
            )
        )
        with open(self.__config_file, 'r') as yamlfile:
            content = yaml.load(yamlfile)
            if content:
                return content
        return {}

    def __add_attrs(self):
        """Not exactly the perfect suit because the IDE won't see the attributes, but fast"""
        section = self.__config.get(self.__section, {})
        for key, value in section.items():
            setattr(self, key, value)


class SubredditSubmissionsManager(object):
    """A manager to get objects from reddit and push them into the database"""

    def __init__(self, reddit_client, objects_dbwriter, submissions_collection,
                 comments_collection, subreddits_list):
        self.__reddit_client = reddit_client
        self.__objects_dbwriter = objects_dbwriter
        self.__subreddits_list = subreddits_list
        self.__submissions_collection = submissions_collection
        self.__comments_collection = comments_collection

    def grab_submissions(self):
        """
        Grabs submissions together with their comments from reddit and pushes them into the
        database
        """
        for submissions, comments in self.__pull_items_from_reddi(self.__subreddits_list):
            self.__push_to_db(self.__submissions_collection, submissions)
            self.__push_to_db(self.__comments_collection, comments)

    def __pull_items_from_reddi(self, subreddits_list):
        """
        Submissions and comments could be grabbed separately or together.
        Grabbing them together for performance now...
        """
        for subreddit in subreddits_list:
            try:
                logger.info(
                    "Grab reddit submissions and comments for subreddit: {0}".format(subreddit)
                )
                submissions, comments = self.__reddit_client\
                    .get_last_submissions_and_comments(subreddit)
                yield submissions, comments
            except RedditConnectionError:
                yield [], []

    def __push_to_db(self, collection, submissions_list):
        logger.info(
            "Push items into: {0} collection".format(collection)
        )
        self.__objects_dbwriter.bulk_write(collection, submissions_list)


class RedditClient(object):
    """Reddit client wrapper, singleton because best practices say so"""
    __metaclass__ = Singleton

    def __init__(self, user, password, app_id, app_secret, user_agent, query_limit=20):
        self.__praw_reddit = praw.Reddit(
                                client_id=app_id,
                                client_secret=app_secret,
                                username=user,
                                password=password,
                                user_agent=user_agent
                            )
        self.__query_limit = query_limit

    @backoff.on_exception(backoff.expo, RedditConnectionError, max_time=10)
    def get_last_submissions_and_comments(self, subreddit):
        """
        Scrapes given subreddit of new submissions and comments
        :param subreddit: str, an actual subreddit
        :return tuple, (list of submissions, list of comments)
        :raises  RedditConnectionError
        """
        last_submissions = []
        last_comments = []
        try:
            logger.info(
                "Retrieve subreddit: {0} newest {1} submissions".format(
                    subreddit, self.__query_limit
                )
            )
            new_submissions = self.__praw_reddit.subreddit(subreddit).new(limit=self.__query_limit)
        except requests_exceptions.ConnectionError as e:
            logger.error("Cannot connect to reddit. Error: {0}".format(e))
            raise RedditConnectionError
        for submission in new_submissions:
            # this is reddit unique id for submission objects
            submission_uniq_id = submission.fullname
            last_submissions.append(
                Submission(submission_uniq_id, submission.title, submission.created, subreddit)
            )
            for comment in submission.comments:
                # this is reddit unique id for comment objects
                comment_uniq_id = comment.fullname
                last_comments.append(
                    Comment(comment_uniq_id, comment.body, comment.created, subreddit)
                )
        return last_submissions, last_comments


class ObjectsDBWriter(object):
    """Handles given objects that need to be written in the database by serializing them"""
    __metaclass__ = Singleton

    def __init__(self, db_client):
        self.__db_client = db_client

    def bulk_write(self, collection, objects_list, serialized=False):
        """
        Writes a list of objects to the data base
        :param collection: str, the collection in the db in which the objects are to be written
        :param objects_list: list of submissions to write to db
        :param serialized: if the list contains named tuples or they are serialized already
        """
        if not serialized:
            objects_list = self.__serialize_objects(objects_list)
        if objects_list:
            try:
                self.__db_client.bulk_write(collection, objects_list)
            except DBConnectionError:
                pass

    def __serialize_objects(self, objects_list):
        serialized_objects = []
        for item in objects_list:
            serialized_objects.append(vars(item))
        return serialized_objects


class DBClient(object):
    __metaclass__ = Singleton

    def __init__(self, host, port, db):
        self.__db_client = pymongo.MongoClient(host, port)
        self.__db = self.__db_client[db]

    @backoff.on_exception(backoff.expo, DBConnectionError, max_time=10)
    def bulk_write(self, collection, json_list):
        """
        Bulk writes a list of serialized objects into a given collection
        :param collection: str, a collection in the database
        :param json_list: list of serialized objects
        :raises DBConnectionError
        """
        try:
            self.__db[collection].insert_many(json_list, ordered=False)
        except pymongo_errors.DuplicateKeyError:
            logger.info("Duplicate Key when wanting to insert object with existing ids")
        except pymongo_errors.BulkWriteError as e:
            logger.info("BulkWriteError encountered. See: {0}".format(e))
        except pymongo_errors.ServerSelectionTimeoutError as e:
            logger.error("Cannot connect to database. Error: {0}".format(e))
            raise DBConnectionError

    @backoff.on_exception(backoff.expo, DBConnectionError, max_time=10)
    def create_secondary_index(self, collection, key, reverse=True):
        """
        Creates secondary index on collection on given key
        :param collection: str, a collection
        :param key: str, an object's key or field
        :param reverse: bool, default True
        :return:
        """
        if reverse:
            order = pymongo.DESCENDING
        else:
            order = pymongo.ASCENDING
        try:
            self.__db[collection].ensure_index([(key, order)])
        except pymongo_errors.ServerSelectionTimeoutError as e:
            logger.error("Cannot connect do database. Error: {0}".format(e))
            raise DBConnectionError

    def create_collection(self, name):
        """
        Creates a collection with given name
        :param name: str, collection name
        """
        self.__db[name]


def initialize_database(db_client, collections, field):
    """
    Initializes the database
    :param db_client: a database client
    :param collections: the list of collections to create
    :param field: the field on which we want a secondary index
    """
    for collection in collections:
        logger.info("Create collection: {0}".format(collection))
        db_client.create_collection(collection)
        logger.info("Create secondary index for: {0} on field: {1}".format(collection, field))
        db_client.create_secondary_index(collection, field)


def particularize_argument_parser():
    """
    Provide all needed arguments for an argument parser
    :return: an argument parser with all needed arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config_section',
        type=str,
        dest='config_section',
        required=False,
        help='Config section to use. If none is provide, the default one will be used.',
    )
    return parser


def main():

    args = particularize_argument_parser().parse_args()

    if args.config_section:
        config = Config('config.yaml', section=args.config_section)
    else:
        config = Config('config.yaml')

    reddit_client = RedditClient(
        config.REDDIT["USER"],
        config.REDDIT["PASSWORD"],
        config.REDDIT["APP_ID"],
        config.REDDIT["APP_SECRET"],
        config.REDDIT["USER_AGENT"],
        config.REDDIT['QUERY_LIMIT']
    )

    db_client = DBClient(config.DB['HOST'], config.DB['PORT'], config.DB['NAME'])

    initialize_database(db_client, config.DB['COLLECTIONS'], 'created')

    object_dbwriter = ObjectsDBWriter(db_client)

    subreddits = config.REDDIT['SUBREDDITS']

    submissions_collection, comments_collection = config.DB['COLLECTIONS']

    manager = SubredditSubmissionsManager(
        reddit_client,
        object_dbwriter,
        submissions_collection,
        comments_collection,
        subreddits
    )

    while True:
        manager.grab_submissions()
        time.sleep(int(config.PARSER["RUN_FREQUENCY"]))

if __name__ == "__main__":
    main()
