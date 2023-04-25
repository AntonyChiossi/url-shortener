"""
@file test.py
@author Antony Chiossi
"""

from utils.commons import snowflake_to_base62
from utils.snowflake import Snowflake


sf = Snowflake(1, 1)
sf62 = snowflake_to_base62(sf.generate_snowflake_id())
print(sf62)
