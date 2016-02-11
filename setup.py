from setuptools import setup

setup(name='secfuldjangoplugin',
      version='1.0',
      #description='The funniest joke in the world',
      #url='http://github.com/storborg/funniest',
      author='Michael Vilensky',
      #author_email='flyingcircus@example.com',
      license='MIT',
      packages=['secfuldjangoplugin'],
      install_requires=[
                'websocket-client',
                      ],
      zip_safe=False)
