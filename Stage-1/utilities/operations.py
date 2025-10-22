from collections import Counter 
from datetime import datetime, timezone
import hashlib

def length(item: str):
    '''
    Returns number of characters in string
    '''
    return len(item)

def is_palindrome(item: str):
    """
    Return true if words is reads backwards as same as forward (case sensitive)
    """
    normalized_item = item.lower()
    return normalized_item == normalized_item[::-1]

def unique_characters(item: str):
    '''
    Return count of unique characters in string
    '''
    return len(set(item))

def word_count(item: str):
    '''
    Return number of words in item seperated by whitespace
    '''
    return len(item.split())

def sha256_hash(item: str):
    '''
    Returns SHA-256 hash of item for unique identification
    '''

    input_bytes = item.encode("utf-8")
    sha256_hash_object = hashlib.sha256(input_bytes)
    hex_digest = sha256_hash_object.hexdigest()

    return hex_digest

def character_frequency_map(item: str):
    """
    Returns dictionary of each character as key and count as value
    """
    return dict(Counter(item))

def get_current_time():
    return datetime.now(timezone.utc)