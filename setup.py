from setuptools import setup

version=0.1

setup(name='djangoui', 
      version=str(version), 
      description='Very simple quick way to deploy Django Application',
      url='https://github.com/django-ui/djangoui.git',
      author='Wan Bae, Seattle University',
      author_email='baew@seattleu.edu',
      license='Apache License 2.0',
      packages = ['djangoui'],
      include_package_data=True,
      package_data={'djangoui':['djangoui/*', 'djangoui/**/*' ]},
      zip_safe=False,
      install_requires=['django'],
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',
            
          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          #'Topic :: Jupyter Prettification :: Utilities ',
      
          # Pick your license as you wish (should match "license" above)
           'License :: OSI Approved :: Apache Software License',
      
          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
)
