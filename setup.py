from setuptools import setup
import os
import minidom_ext
setup(name = 'minidom_ext',
      version = minidom_ext.__version__,
      author = 'Emmanuel Desmontils',
      author_email = 'emmanuel.desmontils@univ-nantes.fr',
      maintainer = 'Emmanuel Desmontils',
      maintainer_email = ' emmanuel.desmontils@univ-nantes.fr',
      keywords = 'minidom XML DOM',
      classifiers = ['Topic :: Education',
                     'Topic :: Documentation'],
      url = 'https://github.com/edesmontils/Minidom_ext',
      packages = ['minidom_ext'],
      install_requires = ['lxml>=4.5.1'],
      description = 'Minidom extension',
      long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
      long_description_content_type="text/markdown",
      license = 'GPL V3',
      platforms = 'ALL',
     )