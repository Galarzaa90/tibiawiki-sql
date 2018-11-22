import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(BASE_PATH, "resources/")


def load_resource(resource):
    with open(os.path.join(RESOURCES_PATH, resource)) as f:
        return f.read()
