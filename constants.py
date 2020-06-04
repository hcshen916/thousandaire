"""
Global constants shared by the whole package.
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONST_MAP = {
    ('currency_price', 'TW') : 'currency_price_tw'
}
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DATA_LIST_ALL = ['currency_price_tw', 'workdays']
TIMESTAMP_FILE_SUFFIX = '_timestamp_file.pkl'
