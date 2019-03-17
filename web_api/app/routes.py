"""
Python 2.7 API to get Reddit sumbissions and comments
"""

from flask import request, jsonify
import json
from bson import BSON
from bson import json_util
from app import app, mongo
from app import utils
from logger import logger


log = logger.create_logger(__name__)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return "Hello, this is Murarasu's Reddit Sumission and Comments API"


@app.route('/items/', methods=['GET'])
def get_items():
    """
    Call this api method by passing the parameters: subreddit, from, and to
    ---
    tags:
      - Reddit submission and comments
    parameters:
      - name: subreddit
        in: query
        type: string
        required: true
        description: Subreddit name
      - name: from
        in: query
        type: number
        required: true
        description: from date in unix timestamp format
      - name: to
        in: query
        type: number
        required: true
        description: from date in unix timestamp format
      - name: keyword
        in: query
        type: string
        required: false
        description: keyword to filter submissions and comments by
    responses:
      500:
        description: Error!
      200:
        description: All the submissions and comments that match the query parameters
    """
    query_parameters = request.args

    subreddit = query_parameters.get('subreddit', None)
    from_date = query_parameters.get('from', None)
    to_date = query_parameters.get('to', None)
    keyword = query_parameters.get('keyword', None)

    if not (subreddit and from_date and to_date):
        return '{"Error": "subreddit, from_date and to_date are mandatory query parameters"}'

    submissions_condition = utils.create_query_condition(
            subreddit, from_date, to_date, keyword, 'title'
    )
    comments_condition = utils.create_query_condition(
            subreddit, from_date, to_date, keyword, 'text'
    )

    log.info('Query DB for submissions')
    cursor = mongo.db['submissions'].find(submissions_condition)
    submissions_objects_list = [item for item in cursor]

    log.info('Query DB for submissions')
    cursor = mongo.db['comments'].find(comments_condition)
    comments_objects_list = [item for item in cursor]

    merged_items = utils.merge_timestamp_sorted_dict_lists(
        submissions_objects_list,
        comments_objects_list
    )

    return json.dumps(
        {'items': merged_items},
        sort_keys=False,
        indent=4,
        default=json_util.default
    )

#print json.dumps(cursor.explain(), sort_keys=True, indent=4, default=json_util.default)