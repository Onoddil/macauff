# Licensed under a 3-clause BSD style license - see LICENSE
'''
Tests for the "matching" module.
'''

import pytest
import os
from numpy.testing import assert_almost_equal
import numpy as np

from ..matching import CrossMatch


def test_crossmatch_run_input():
    with pytest.raises(FileNotFoundError):
        cm = CrossMatch('./file.txt')

    cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata.txt'))
    assert cm.run_auf is False
    assert cm.run_group is False
    assert cm.run_cf is True
    assert cm.run_star is True

    # List of simple one line config file replacements for error message checking
    f = open(os.path.join(os.path.dirname(__file__), 'data/metadata.txt')).readlines()
    for old_line, new_line, match_text in zip(['run_cf = yes', 'run_auf = no', 'run_auf = no'],
                                              ['', 'run_auf = aye\n', 'run_auf = yes\n'],
                                              ['Missing key', 'Boolean flag key not set',
                                               'Inconsistency between run/no run']):
        idx = np.where([old_line in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata.txt'),
                                 idx, new_line, out_file=os.path.join(os.path.dirname(__file__),
                                                                      'data/metadata_.txt'))

        with pytest.raises(ValueError, match=match_text):
            cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_.txt'))


def test_crossmatch_auf_cf_input():
    cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata.txt'))
    assert cm.auf_region_frame == 'equatorial'
    assert_almost_equal(cm.auf_region_points,
                        np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                  [131, 0], [132, 0], [133, 0], [134, 0],
                                  [131, 1], [132, 1], [133, 1], [134, 1]]))

    assert cm.cf_region_frame == 'equatorial'
    assert_almost_equal(cm.cf_region_points,
                        np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                  [131, 0], [132, 0], [133, 0], [134, 0],
                                  [131, 1], [132, 1], [133, 1], [134, 1]]))

    f = open(os.path.join(os.path.dirname(__file__), 'data/metadata.txt')).readlines()
    for kind in ['auf_region_', 'cf_region_']:
        # List of simple one line config file replacements for error message checking
        for old_line, new_line, match_text in zip(
            ['{}type = rectangle'.format(kind), '{}type = rectangle'.format(kind),
             '{}points = 131 134 4 -1 1 3'.format(kind),
             '{}points = 131 134 4 -1 1 3'.format(kind),
             '{}frame = equatorial'.format(kind), '{}points = 131 134 4 -1 1 3'.format(kind)],
            ['', '{}type = triangle\n'.format(kind), '{}points = 131 134 4 -1 1 a\n'.format(kind),
             '{}points = 131 134 4 -1 1\n'.format(kind), '{}frame = ecliptic\n'.format(kind),
             '{}points = 131 134 4 -1 1 3.4\n'.format(kind)],
            ['Missing key {}type'.format(kind),
             "{}type should either be 'rectangle' or".format(kind),
             '{}points should be 6 numbers'.format(kind),
             '{}points should be 6 numbers'.format(kind),
             "{}frame should either be 'equatorial' or".format(kind),
             'start and stop values for {}points'.format(kind)]):
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/metadata.txt'), idx, new_line, out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/metadata_.txt'))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_.txt'))

        # Check correct and incorrect *_region_points when *_region_type is 'points'
        idx = np.where(['{}type = rectangle'.format(kind) in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata.txt'),
                                 idx, '{}type = points\n'.format(kind),
                                 out_file=os.path.join(os.path.dirname(__file__),
                                                       'data/metadata_.txt'))

        idx = np.where(['{}points = 131 134 4 -1 1 3'.format(kind) in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata_.txt'),
                                 idx, '{}points = (131, 0), (133, 0), (132, -1)\n'.format(kind),
                                 out_file=os.path.join(os.path.dirname(__file__),
                                                       'data/metadata_2.txt'))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_2.txt'))
        assert_almost_equal(getattr(cm, '{}points'.format(kind)),
                            np.array([[131, 0], [133, 0], [132, -1]]))

        old_line = '{}points = 131 134 4 -1 1 3'.format(kind)
        for new_line in ['{}points = (131, 0), (131, )\n'.format(kind),
                         '{}points = (131, 0), (131, 1, 2)\n'.format(kind),
                         '{}points = (131, 0), (131, a)\n'.format(kind)]:
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/metadata_.txt'), idx, new_line, out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/metadata_2.txt'))

            with pytest.raises(ValueError):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_2.txt'))

        # Check galactic run is also fine
        idx = np.where(['{}frame = equatorial'.format(kind) in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata.txt'),
                                 idx, '{}frame = galactic\n'.format(kind),
                                 out_file=os.path.join(os.path.dirname(__file__),
                                                       'data/metadata_.txt'))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_.txt'))

        assert getattr(cm, '{}frame'.format(kind)) == 'galactic'
        assert_almost_equal(getattr(cm, '{}points'.format(kind)),
                            np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                      [131, 0], [132, 0], [133, 0], [134, 0],
                                      [131, 1], [132, 1], [133, 1], [134, 1]]))

        # Check single-length point grids are fine
        idx = np.where(['{}points = 131 134 4 -1 1 3'.format(kind) in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata.txt'),
                                 idx, '{}points = 131 131 1 0 0 1\n'.format(kind),
                                 out_file=os.path.join(os.path.dirname(__file__),
                                                       'data/metadata_.txt'))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_.txt'))

        assert_almost_equal(getattr(cm, '{}points'.format(kind)), np.array([[131, 0]]))

        idx = np.where(['{}type = rectangle'.format(kind) in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata.txt'),
                                 idx, '{}type = points\n'.format(kind),
                                 out_file=os.path.join(os.path.dirname(__file__),
                                                       'data/metadata_.txt'))

        idx = np.where(['{}points = 131 134 4 -1 1 3'.format(kind) in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__), 'data/metadata_.txt'),
                                 idx, '{}points = (131, 0)\n'.format(kind),
                                 out_file=os.path.join(os.path.dirname(__file__),
                                                       'data/metadata_2.txt'))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/metadata_2.txt'))
        assert_almost_equal(getattr(cm, '{}points'.format(kind)), np.array([[131, 0]]))
