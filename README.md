# django-agent
Catch traffic on django middleware and send it out in different threads.

Installation
------------

    Install python websocket-client
    "pip install websocket-client"

    Put secful.py in the correct folder

    To activate secful middleware component, add it to the MIDDLEWARE_CLASSES list in your Django settings.
    For example:
    MIDDLEWARE_CLASSES = [

        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'djangoplugin.secful.Secful',
   ]
