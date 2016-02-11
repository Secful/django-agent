# django-agent
Secure Django server with SECful

Installation
------------

```
pip install git+https://github.com/SECful/django-agent.git@v1.0
```
In django settings.py:
* add the item 'secfuldjangoplugin.Secful' to MIDDLEWARE_CLASSES list.
* add "SECFUL_KEY = 'KEY'" to the settings (replace KEY with the key provided by SECful.)
* add "SECFUL_HOST = 'HOST'" to the settings (replace HOST with the host provided by SECful.)

For example (settings.py):
```
SECFUL_KEY = 'KEY' # replace KEY with the key provided by SECful.
SECFUL_HOST = 'HOST' # replace HOST with the host provided by SECful.
...
MIDDLEWARE_CLASSES = [
    ..., 
    ..., 
    ..., 
    'secfuldjangoplugin.Secful',
]

```
