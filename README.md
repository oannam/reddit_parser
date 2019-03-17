# reddit_parser

This project is composed of:

## reddit_parser
This is a long running script that parses submissions and comments form a 
list of given subreddits and then submits them into a database

Checkout reddit_parser/config.yaml for configuration insights.

Run example: ``python parser.py --config_section TEST``

## web_api
This is a Web API that exposes methods of querying a database for reddit submissions
and comments. It provides filtering by subreddit, timestamps, and optionally a 
keyword.

Checkout web_api/config.yaml for configuration insights.

Run example: ``python app.py``

It runs on localhost:8080 by default. If you want to try the API you can run it and
then go to: ``http://localhost:8080/apidocs``

## mongo
This part consists of a dockerfile for a MongoDB instance.

## Build and run all containers
In order to build all the cotainers:
``docker-compose build``

In order to run all the containers:
``docker-compose up``