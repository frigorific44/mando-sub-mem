import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
dependencies = data["project"]["dependencies"]
try:
    ignore = data["tool"]["vendors"]["ignore"]
except KeyError:
    ignore = []
vendor = [p for p in dependencies if all([ig not in p for ig in ignore])]
print(" ".join(vendor))
