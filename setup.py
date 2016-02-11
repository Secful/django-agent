from setuptools import setup

setup(name='secfuldjangoplugin',
      version='1.0',
      description='Django plugin for SECful',
      url='https://github.com/SECful/django-agent.git',
      author='Michael Vilensky',
      packages=['secfuldjangoplugin'],
      install_requires=[
                'websocket-client',
                      ],
      zip_safe=False)
