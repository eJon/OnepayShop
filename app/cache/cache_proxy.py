# -*- coding: utf-8 -*-
__author__ = 'wog'

import re

class CacheProxy():
    def __init__(self, mc):
        self.mc = mc
        self.routes = []

    def _set(self, key, value, timeout=30):
        if value == None:
            return
        self.mc.set(key, value, timeout)

    def _get(self, key, call_back, timeout=30, *args):
        key=str(key)
        if len(key) >= 250:
            return None
        value = self.mc.get(key)
        if value == None:
            value = call_back(*args)
            self._set( key, value, timeout)
        return value

    def get(self, name):
        value = self.mc.get(name)
        print "cache from memcached"
        if not value:
            print "can not cache from memcached"
            route_match = self.get_route_match(name)
            if route_match:
                kwargs, view_function, timeout = route_match
                value = view_function(**kwargs)
                self.mc.set(name, value, timeout)
            else:
                raise ValueError('Route "{}"" has not been registered'.format(name))
        return value

    def remove(self, name):
        return self.mc.delete(name)




    @staticmethod
    def build_route_pattern(route):
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{}$".format(route_regex))

    def register(self, route_str, timeout):
        def decorator(f):
            # Instead of inserting into a dictionary,
            # We'll append the tuple to our route list
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, f, timeout))
            return f
        return decorator


    def get_route_match(self, path):
        for route_pattern, view_function, timeout in self.routes:
            m = route_pattern.match(path)
            if m:
               return m.groupdict(), view_function, timeout
        return None