import argparse
from app import app
from config import config


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
        conf = config.Config('config.yaml', section=args.config_section)
    else:
        conf = config.Config('config.yaml')

    app.run(conf.WEBSERVER['HOST'], conf.WEBSERVER['PORT'], conf.WEBSERVER['DEBUG'])


if __name__ == '__main__':
    main()
