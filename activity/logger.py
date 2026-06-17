import logging
import os

LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

activity_logger = logging.getLogger('user_activity')
activity_logger.setLevel(logging.INFO)

handler = logging.FileHandler(os.path.join(LOG_DIR, 'activity.log'))
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(message)s'
))

activity_logger.addHandler(handler)