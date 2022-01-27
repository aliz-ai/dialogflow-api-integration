import logging
import sys

import click
import yaml

from chatbot.app import ChatbotApp


class LessThanFilter(logging.Filter):
    """ Class for implementing a logging filter that omits messages above a certain level """

    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        return 1 if record.levelno < self.max_level else 0


def setup_logging(level=logging.INFO, path=None):
    """ Set up streamed logging and optionally file logging """
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")

    logging_handler_stdout = logging.StreamHandler(sys.stdout)
    logging_handler_stdout.setLevel(level)
    logging_handler_stdout.addFilter(LessThanFilter(logging.WARNING))
    logging_handler_stdout.setFormatter(formatter)
    logger.addHandler(logging_handler_stdout)

    logging_handler_stderr = logging.StreamHandler(sys.stderr)
    logging_handler_stderr.setLevel(logging.WARNING)
    logging_handler_stderr.setFormatter(formatter)
    logger.addHandler(logging_handler_stderr)

    if path:
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def _load_config(ctx, param, value):
    """ Validate and load specified configuration file """
    try:
        with open(value, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        raise click.BadParameter("failed to load configuraion - {}: {}".format(value, e))


@click.command()
@click.version_option()
@click.option("-c", "--config", default="config.yaml", show_default=True, type=click.Path(exists=True),
              callback=_load_config, help="Set the application configuration")
@click.option("-h", "--host", default="127.0.0.1", show_default=True,
              help="Set the application host")
@click.option("-p", "--port", default=8080, show_default=True,
              help="Set the application port")
@click.option("--debug",  default=False, show_default=True, is_flag=True,
              help="Run application in debug mode")
@click.option("-v", "--log-level", default="INFO", show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help="Set the verbosity of logging")
@click.option("-l", "--log-file", default=None, show_default=True,
              help="Set the log file location")
def cli(config, host, port, debug, log_level, log_file):
    """ A PoC for validating Dialogflow - Userlike integration """
    setup_logging(log_level, log_file)
    logger = logging.getLogger(__name__)
    logger.info("Launching app on {}:{}".format(host, port))
    chatbot = ChatbotApp(config)
    chatbot.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    cli()
