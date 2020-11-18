from setuptools import find_packages
from numpy.distutils.core import Extension, setup

names = ['perturbation_auf_fortran', 'group_sources_fortran', 'misc_functions_fortran']
f90_args = ["-Wall", "-Wextra", "-Werror", "-pedantic", "-fbacktrace", "-O0", "-g", "-fcheck=all",
            "-fopenmp"]

extension = [Extension(name='macauff.{}'.format(name), sources=['macauff/{}.f90'.format(name)],
                       language='f90', extra_link_args=["-lgomp"],
                       extra_f90_compile_args=f90_args, libraries=['shared_library'])
             for name in names]

extension.extend([Extension(name='macauff.tests.test_misc_functions_fortran',
                            sources=['macauff/tests/test_misc_functions_fortran.f90'],
                            language='f90', extra_link_args=["-lgomp"],
                            libraries=['shared_library'], extra_f90_compile_args=f90_args)])

setup(name="macauff", packages=find_packages(), package_data={'macauff': ['tests/data/*']},
      ext_modules=extension, libraries=[('shared_library',
                                        dict(sources=['macauff/shared_library.f90'],
                                         extra_f90_compile_args=f90_args,
                                         extra_link_args=["-lgomp"], language="f90"))])
