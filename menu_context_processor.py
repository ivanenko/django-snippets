import os
from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def app_delegate(request):
    app_name = resolve(request.path).app_name
    context = {}
    if app_name==None:
        return context

    dname = os.path.dirname(__import__(app_name).__file__)
    if os.path.isfile(os.path.join(dname, "menu.py")):
        try:
            # mod = import_module(os.path.join(dname, "menu.py"))
            mod = import_module('%s.%s' % (app_name, "menu"))
        except ImportError as e:
            raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (app_name, e))

        try:
            func = getattr(mod, "get_menu")
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (app_name, "get_menu"))

        context.update(func(request))

    return context




