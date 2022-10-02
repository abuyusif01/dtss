import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/test.log"),  # the one that write to the file
        logging.StreamHandler(),
    ],
)
logging.info("anything given here")  # this will be written to the file and to the console
