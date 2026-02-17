"""
Python 3.14 compatibility fix for Django 5.0
This patches the BaseContext.__copy__ method to work with Python 3.14
"""
from django.template import context
import copy

def patched_context_copy(self):
    """
    Fixed __copy__ method that works with Python 3.14
    """
    # Use __new__ to create instance without __init__
    duplicate = self.__class__.__new__(self.__class__)
    # Copy all attributes (efficient shallow copy)
    duplicate.__dict__ = self.__dict__.copy()
    # Ensure dicts list is copied (sliced)
    duplicate.dicts = self.dicts[:]
    return duplicate

# Apply the patch to BaseContext
context.BaseContext.__copy__ = patched_context_copy
