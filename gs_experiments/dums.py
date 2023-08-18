import random, os, sys
cwd = os.getcwd()
sys.path.append(cwd)
from enum import Enum

import json
import git
from datetime import datetime
from utils import args

""" repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha
print(sha)

 
# Data to be written
dictionary = {
    "name": "sathiyajith",
    "rollno": 56,
    "cgpa": 8.6,
    "phonenumber": "9976770500"
}
 
dictionary = dict()
dictionary["commit_id"] = sha

with open("sample.json", "w") as outfile:
    json.dump(dictionary, outfile, indent=4, sort_keys=True, default=lambda x: x.__name__)

"""

a = args.Args()
a.colour = "blue"
print(a.colour)
for v in vars(a):
    print(v)
    print(getattr(a, v))