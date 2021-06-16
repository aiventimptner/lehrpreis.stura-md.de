# Studierendenrat

This repository contains the source code for some parts of the homepage of [Studierendenrat](https://stura-md.de) 
(StuRa). StuRa is the student council and representative for all students at the 
[Otto-von-Guericke-University Magdeburg](https://www.ovgu.de).

The website makes use of [Django](https://www.djangoproject.com/) and is styled with [Bulma](https://bulma.io/).

## Installation

Set up a dedicated virtual environment for you python runtime and install all 
required packages. It's recommended to use Python version 3.9 but everything 
above version 3.5 should also be sufficient.

```shell
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

In a production environment you should set the following environment variables. You 
should note, that it is required to separate multiple domain names (including 
subdomains) via comma and no whitespaces for `ALLOWED_HOSTS`. All email configuration 
require a TLS enabled connection.

```ini
SECRET_KEY=secret-key
DJANGO_SETTINGS_MODULE=stura.settings.production
ALLOWED_HOSTS=example.com,example.org
DB_NAME=stura
DB_USER=stura
DB_PASSWORD=secret-password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST = localhost
EMAIL_PORT = 587
EMAIL_USER = no-reply
EMAIL_PASSWORD = secret-password
DEFAULT_EMAIL = no-reply@stura-md.de
```

You can generate a new secret key:

```python
from django.core.management import utils
utils.get_random_secret_key()
```

Last but not least you can migrate all database models and start your webserver.

```shell
python manage.py migrate
python manage.py runserver
```

## Translation

To find all translations strings and update the `.po` file run the following command from project root.

```shell
django-admin makemessages -l de --ignore=django
```

To generate the corresponding binary `.mo` file run:

```shell
django-admin compilemessages --ignore=django
```

## License

[MIT](https://github.com/aiventimptner/stura/blob/main/LICENSE)
