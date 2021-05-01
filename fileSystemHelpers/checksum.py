import os.path as path
import os
import platform
import time
from datetime import datetime
import sys


def check_sum(relative_path: str, complete_path: str, encoder: list):
    """
    Computes a check sum of a file including it's contents, filename, modification timestamp, and complete path
    Args:
        complete_path (str): Complete path to the file
        encoder (list): List of ints to encode a file
    Return:
        sum (int): some of the checksum
    """

    # Get name of file
    name_of_file = path.basename(complete_path)

    # Get timestamp as string
    timestamp = get_time_stamp(complete_path)

    # Open the file
    file = open(complete_path, "r")

    # Append timestamp, name_of_file, and complete path
    check_sum_contents = file.readlines()
    check_sum_contents.append(name_of_file)
    check_sum_contents.append(str(timestamp))
    check_sum_contents.append(relative_path)

    # Get the length of the encoder
    length_of_encoder = len(encoder)

    sum = 0

    # Go through each character and add it to the sum using encoder
    i = 0
    for line in check_sum_contents:
        for char in line:
            # Keeps index in range (0, len(encoder))
            encoder_index = i % length_of_encoder

            # Add the product of the unicode and encoder
            sum += ord(char) * encoder[encoder_index]
            i += 1

    return sum


def get_time_stamp(complete_path: str):
    """
    Gets the last modified timestamp of a file as a string
    Args:
        complete_path (str): Complete path to the file
    Return:
        sum (Datetime): Last time of modifiction a string
    """

    # If the OS of the machine is windows
    if platform.system() == "Windows":
        time_modified_since = path.getctime(complete_path)

    # If the OS of the machine is UNIX based
    else:
        stat = os.stat(complete_path)
        time_modified_since = stat.st_mtime

    # Convert to string
    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_modified_since))
    mod_time = datetime.strptime(mod_time, "%Y-%m-%d %H:%M:%S")

    return mod_time


if __name__ == "__main__":

    relative_path = sys.argv[1]

    default_encoder = [9, 4, 2, 5, 8]

    complete_path = path.abspath(relative_path)

    print(check_sum(complete_path, default_encoder))
