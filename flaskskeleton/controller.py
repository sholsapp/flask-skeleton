import argparse
import sys
import os
import pathlib

from configobj import ConfigObj

from flaskskeleton import init_webapp


def start_webapp(config):
    """Entry point to start web application.

    Call this function from a wrapper to initialize and start the web
    application.

    Configure the application using the process environment. Configurable
    attributes include:

        - HOST
        - PORT

    """
    app = init_webapp(config)
    app.run(
        host=os.environ.get('HOST', config['webapp']['host']),
        port=os.environ.get('PORT', config['webapp']['port']),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c" ,
        "--config",
        help="The configuration file.",
        default=str(pathlib.Path('./config/dev.config')),
        required=False,
    )
    args = parser.parse_args()
    try:
        config = ConfigObj(args.config, configspec=f'{args.config}spec')
    except OSError:
        print("Failed to load the configuration file at {args.config}.")
        sys.exit(1)
    start_webapp(config)
