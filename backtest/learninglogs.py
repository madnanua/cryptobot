import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(asctime)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler('test.log')
file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def div(x,y):
   try:
      result=x/yz
      logger.debug(result)
      # if x>y:
      #    raise Exception
   except FileNotFoundError as e:
      logger.exception(e)
   except Exception as e:
      logger.exception(e)
   else:
      return result

div(4,1)