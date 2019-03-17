"""Utils functions"""


def create_query_condition(subreddit, from_date, to_date, keyword=None, in_field=None):
    """
    Creates a mongo db query condition.
    :param subreddit: str, a subreddit name
    :param from_date: float, unix timestamp
    :param to_date: float, unix timestamp
    :param keyword: str, optional keyword
    :param in_field: str, optional, only used with keyword
    :return: a condition as a dict
    """
    if keyword and in_field:
        condition = {
            'created': {
                '$gte': float(from_date),
                '$lte': float(to_date)
            },
            'subreddit': subreddit,
            in_field: {'$regex': '.*{0}.*'.format(keyword)}
        }
    else:
        condition = {
            'created': {
                '$gte': float(from_date),
                '$lte': float(to_date)
            },
            'subreddit': subreddit
        }
    return condition


def merge_timestamp_sorted_dict_lists(d_list1, d_list2):
    """
    Merges 2 lists of sorted dictionaries on key "created".
    :param d_list1: list of sorted dictionaries
    :param d_list2: list of sorted dictionaries
    :return: merged list of sorted dictionaries
    """
    # Need to replace this implementation with an actual merge for optimization.
    return sorted(d_list1 + d_list2, key=lambda k: k['created'], reverse=True)