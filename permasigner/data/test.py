import importlib.resources

f = importlib.resources.files('permasigner')
print(type(f))

with importlib.resources.path('permasigner', '__init__.py') as r:
    res = r.parent
print(type(res))
