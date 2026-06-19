from dataclasses import asdict
from pprint import pformat

def fprint(data):
    print(pformat(asdict(data), sort_dicts=False, width=100))