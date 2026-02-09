"""
Fix for Python 3.14 compatibility issue with Django template context
This patch fixes the 'super' object has no attribute 'dicts' error
"""

import copy
from django.template.context import BaseContext, Context, RequestContext


def patched_base_context_copy(self):
    """Patched __copy__ method for BaseContext to handle Python 3.14"""
    # Create a new instance without calling super()
    duplicate = self.__class__.__new__(self.__class__)
    # Use dict.__setitem__ to avoid super() issues
    super(BaseContext, duplicate).__setattr__('dicts', self.dicts[:])
    return duplicate


def patched_context_copy(self):
    """Patched __copy__ method for Context to handle Python 3.14"""
    # Create a new instance without calling super()
    duplicate = self.__class__.__new__(self.__class__)
    # Use dict.__setitem__ to avoid super() issues
    super(Context, duplicate).__setattr__('dicts', self.dicts[:])
    return duplicate


def patched_request_context_copy(self):
    """Patched __copy__ method for RequestContext to handle Python 3.14"""
    # Create a new instance without calling super()
    duplicate = self.__class__.__new__(self.__class__)
    # Use dict.__setitem__ to avoid super() issues
    super(RequestContext, duplicate).__setattr__('dicts', self.dicts[:])
    # Copy essential attributes
    if hasattr(self, 'request'):
        super(RequestContext, duplicate).__setattr__('request', self.request)
    if hasattr(self, '_processors_index'):
        super(RequestContext, duplicate).__setattr__('_processors_index', self._processors_index)
    if hasattr(self, 'template'):
        super(RequestContext, duplicate).__setattr__('template', self.template)
    if hasattr(self, 'render_context'):
        super(RequestContext, duplicate).__setattr__('render_context', self.render_context)
    return duplicate


# Apply the patches
BaseContext.__copy__ = patched_base_context_copy
Context.__copy__ = patched_context_copy
RequestContext.__copy__ = patched_request_context_copy

print("Applied Python 3.14 compatibility patch for Django template context")
