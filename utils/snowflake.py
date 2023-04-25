"""
@file snowflake.py
@author Antony Chiossi

inspired by https://gist.github.com/wakingyeung/c4615dacd5b7789873d9be498af92acc
"""
import time

DATACENTER_ID_BITS = 6
NODE_ID_BITS = 4
TIMESTAMP_BITS = 41
SEQUENCE_BITS = 12

EPOCH = 1609459200000  # 2021-01-01T00:00:00Z in milliseconds
MAX_DATACENTER_ID = 2**DATACENTER_ID_BITS - 1
MAX_NODE_ID = 2**NODE_ID_BITS - 1
MAX_SEQUENCE = 2**SEQUENCE_BITS - 1

TIMESTAMP_LEFT_SHIFT = NODE_ID_BITS + SEQUENCE_BITS + DATACENTER_ID_BITS
DATACENTER_ID_LEFT_SHIFT = NODE_ID_BITS + SEQUENCE_BITS
NODE_ID_LEFT_SHIFT = SEQUENCE_BITS


class Snowflake:
    def __init__(self, datacenter_id: int, node_id: int, sequence=0):
        self._datacenter_id = datacenter_id
        self._node_id = node_id
        self._sequence = sequence

        # Set the initial timestamp
        self.last_timestamp = int(time.time() * 1000) - EPOCH
        print("Snowflake: {}".format(self))

    def generate_snowflake_id(self):
        # Get current timestamp in milliseconds
        timestamp = self.__get_timestamp()

        # If we've moved to the next millisecond, reset the sequence number
        if self.last_timestamp is not None and timestamp < self.last_timestamp:
            self._sequence = 0

        # If we're still in the same millisecond, increment the sequence number
        elif timestamp == self.last_timestamp:
            self._sequence = (self._sequence + 1) & MAX_SEQUENCE

            # If we've exceeded the maximum sequence number, wait until the next millisecond
            if self._sequence == 0:
                timestamp = self.__wait_for_next_millisecond()

        # If we've moved to a new millisecond, reset the sequence number
        else:
            self._sequence = 0

        # Update the last timestamp
        self.last_timestamp = timestamp

        # Combine the timestamp, datacenter ID, node ID, and sequence number to create the Snowflake ID
        snowflake_id = (
            (timestamp << TIMESTAMP_LEFT_SHIFT)
            | (self._datacenter_id << DATACENTER_ID_LEFT_SHIFT)
            | (self._node_id << NODE_ID_LEFT_SHIFT)
            | self._sequence
        )

        return snowflake_id

    def __get_timestamp(self) -> int:
        return int(time.time() * 1000) - EPOCH

    def __wait_for_next_millisecond(self):
        timestamp = self.__get_timestamp()
        while timestamp <= self.last_timestamp:
            time.sleep(0.001)
            timestamp = self.__get_timestamp()
        return timestamp
