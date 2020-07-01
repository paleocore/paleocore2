paleocore
==================

Paleo Core Project

Installation
------------------
* Clone repository from GitHub and move into that directory
```
git clone https://github.com/paleocore/paleocore2.git
cd paleocore2
```

* Create virtual Python environment
```
virtualenv -p python3 venv
```

* Start the virtual environment and install the python libraries stipulated in the requirements file. Separate files stipulate a base set of libraries which are imported into dev and production requirement files.
```
source venv/bin/activate
pip install -r requirements/dev.txt
```

* Create the database. Assuming the database software is installed. The default database for this project uses postgreSQL. The simplest method of implementing the database is using postgres.app.
```
createdb paleocore2
```

* Update the following librarys manual:
```
cd venv/lib/python3.7/site-packages
```
..* djgeojson
...Edit __init__.py:
```
#: Module version, as defined in PEP-0396.
#from pkg_resources import DistributionNotFound

#pkg_resources = __import__('pkg_resources')
#try:
#    distribution = pkg_resources.get_distribution('django-geojson')
#    __version__ = distribution.version
#except (AttributeError, DistributionNotFound):
#    __version__ = 'unknown'
#    import warnings
#    warnings.warn('No distribution found.')

__version__ = '2.12.0'

GEOJSON_DEFAULT_SRID = 4326
```

..* fastkml
...Edit __init__.py:
```
# -*- coding: utf-8 -*-
# Copyright (C) 2012  Christian Ledermann
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""
Fastkml is a library to read, write and manipulate kml files. It aims to keep
it simple and fast (using lxml if available). Fast refers to the time you spend
to write and read KML files as well as the time you spend to get aquainted to
the library or to create KML objects. It provides a subset of KML and is aimed
at documents that can be read from multiple clients such as openlayers and
google maps rather than to give you all functionality that KML on google earth
provides.
"""

#from pkg_resources import get_distribution, DistributionNotFound

from .kml import KML, Document, Folder, Placemark
from .kml import TimeSpan, TimeStamp
from .kml import ExtendedData, Data
from .kml import Schema, SchemaData

from .styles import StyleUrl, Style, StyleMap
from .styles import IconStyle, LineStyle, PolyStyle
from .styles import LabelStyle, BalloonStyle

from .atom import Link, Author, Contributor

#try:
#    __version__ = get_distribution('fastkml').version
#except DistributionNotFound:
#    __version__ = 'dev'
__version__ = '0.10.dev'

__all__ = [
    'KML', 'Document', 'Folder', 'Placemark',
    'TimeSpan', 'TimeStamp',
    'ExtendedData', 'Data',
    'Schema', 'SchemaData',
    'StyleUrl', 'Style', 'StyleMap',
    'IconStyle', 'LineStyle', 'PolyStyle',
    'LabelStyle', 'BalloonStyle',
    'Link', 'Author', 'Contributor',
]
```

..* tablib
... Edit __init__.py:
```
""" Tablib. """
#from pkg_resources import DistributionNotFound, get_distribution
from tablib.core import (  # noqa: F401
    Databook,
    Dataset,
    InvalidDatasetType,
    InvalidDimensions,
    UnsupportedFormat,
    detect_format,
    import_book,
    import_set,
)

#try:
#    __version__ = get_distribution(__name__).version
#except DistributionNotFound:
#    # package is not installed
#    __version__ = None
__version__ = '2.0.2'
```

* Run migrations.
```
python manage.py migrate
```

Run Server
--------------------
* Start virtual environment.

* Create superuser.
```
python manage.py createsuperuser
```

* Run server on local host.
```
python manage.py runserver localhost:8000
```

* Open localhost:8000/django-admin in a web browswer.

