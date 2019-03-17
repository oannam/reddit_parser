# reddit_parser

This project is composed of:

## reddit_parser
This is a long running script that parses submissions and comments form a 
list of given subreddits and then submits them into a database

Checkout reddit_parser/config.yaml for configuration insights.

In order to run the parser, you need a MongoDB instance which you need to configure
in the parser config.yaml and reddit user, passord, application id and application
secret.

Run example: ``python parser.py --config_section TEST``

## web_api
This is a Web API that exposes methods of querying a database for reddit submissions
and comments. It provides filtering by subreddit, timestamps, and optionally a 
keyword.

Checkout web_api/config.yaml for configuration insights.


In order to run the web_api, you need a MongoDB instance which you need to configure
in the web_api config.yaml

Run example: ``python bootstrap.py --config_section TEST``

It runs on localhost:8080 by default. If you want to try the API you can run it and
then go to: ``http://localhost:8080/apidocs``

Or use: 

``curl -X GET "http://localhost:8080/items/?subreddit=stories&from=1546300800&to=1552748591" -H "accept: application/json"``

## mongo
This part consists of a dockerfile for a MongoDB instance.

## Build and run all containers
In order to build all the cotainers:
``docker-compose build``

In order to run all the containers:
``docker-compose up``

## Unit tests

In order to run unit tests, you need to:

```
pip install mock
cd reddit_parser/
python -m unittest discover -v
cd web_api/
python -m unittest discover -v
```