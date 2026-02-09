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
    if hasattr(self, 'autoescape'):
        super(RequestContext, duplicate).__setattr__('autoescape', self.autoescape)
    else:
        # Add autoescape attribute if missing (default to True)
        super(RequestContext, duplicate).__setattr__('autoescape', True)
    if hasattr(self, 'use_tz'):
        super(RequestContext, duplicate).__setattr__('use_tz', self.use_tz)
    else:
        super(RequestContext, duplicate).__setattr__('use_tz', True)
    if hasattr(self, 'use_l10n'):
        super(RequestContext, duplicate).__setattr__('use_l10n', self.use_l10n)
    else:
        super(RequestContext, duplicate).__setattr__('use_l10n', True)
    return duplicate


def patch_request_context_autoescape():
    """Add missing attributes to RequestContext instances"""
    original_init = RequestContext.__init__
    
    def patched_init(self, request, dict_=None, processors=None, use_l10n=None, use_tz=None, autoescape=True):
        original_init(self, request, dict_, processors, use_l10n, use_tz)
        # Ensure essential attributes exist
        if not hasattr(self, 'autoescape'):
            super(RequestContext, self).__setattr__('autoescape', autoescape)
        if not hasattr(self, 'use_tz'):
            super(RequestContext, self).__setattr__('use_tz', use_tz if use_tz is not None else True)
        if not hasattr(self, 'use_l10n'):
            super(RequestContext, self).__setattr__('use_l10n', use_l10n if use_l10n is not None else True)
    
    RequestContext.__init__ = patched_init


# Apply the patches
BaseContext.__copy__ = patched_base_context_copy
Context.__copy__ = patched_context_copy
RequestContext.__copy__ = patched_request_context_copy
patch_request_context_autoescape()

print("Applied Python 3.14 compatibility patch for Django template context")
