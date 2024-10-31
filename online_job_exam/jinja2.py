
from django_jinja import library
from jinja2 import Environment

def environment(**options):
    env = Environment(**options)
    library.install_filters(env)
    return env
