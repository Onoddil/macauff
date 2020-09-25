# Licensed under a 3-clause BSD style license - see LICENSE
'''
Tests for the "matching" module.
'''

import pytest
import os
from configparser import ConfigParser
from numpy.testing import assert_almost_equal
import numpy as np

from ..matching import CrossMatch


class TestInputs:
    def setup_class(self):
        joint_config = ConfigParser()
        with open(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt')) as f:
            joint_config.read_string('[config]\n' + f.read())
        joint_config = joint_config['config']
        cat_a_config = ConfigParser()
        with open(os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt')) as f:
            cat_a_config.read_string('[config]\n' + f.read())
        cat_a_config = cat_a_config['config']
        cat_b_config = ConfigParser()
        with open(os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt')) as f:
            cat_b_config.read_string('[config]\n' + f.read())
        cat_b_config = cat_b_config['config']
        self.a_cat_folder_path = os.path.abspath(cat_a_config['cat_folder_path'])
        self.b_cat_folder_path = os.path.abspath(cat_b_config['cat_folder_path'])

        os.makedirs(self.a_cat_folder_path, exist_ok=True)
        os.makedirs(self.b_cat_folder_path, exist_ok=True)

        np.save('{}/con_cat_astro.npy'.format(self.a_cat_folder_path), np.zeros((2, 3), float))
        np.save('{}/con_cat_photo.npy'.format(self.a_cat_folder_path), np.zeros((2, 3), float))
        np.save('{}/magref.npy'.format(self.a_cat_folder_path), np.zeros(2, float))

        np.save('{}/con_cat_astro.npy'.format(self.b_cat_folder_path), np.zeros((2, 3), float))
        np.save('{}/con_cat_photo.npy'.format(self.b_cat_folder_path), np.zeros((2, 4), float))
        np.save('{}/magref.npy'.format(self.b_cat_folder_path), np.zeros(2, float))

    def test_crossmatch_run_input(self):
        with pytest.raises(FileNotFoundError):
            cm = CrossMatch('./file.txt', './file2.txt', './file3.txt')
        with pytest.raises(FileNotFoundError):
            cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                            './file2.txt', './file3.txt')
        with pytest.raises(FileNotFoundError):
            cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                            './file3.txt')

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.run_auf is False
        assert cm.run_group is False
        assert cm.run_cf is True
        assert cm.run_star is True

        # List of simple one line config file replacements for error message checking
        f = open(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt')).readlines()
        for old_line, new_line, match_text in zip(['run_cf = yes', 'run_auf = no', 'run_auf = no'],
                                                  ['', 'run_auf = aye\n', 'run_auf = yes\n'],
                                                  ['Missing key', 'Boolean flag key not set',
                                                   'Inconsistency between run/no run']):
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                                      'data/crossmatch_params.txt'),
                                     idx, new_line,
                                     out_file=os.path.join(os.path.dirname(__file__),
                                     'data/crossmatch_params_.txt'))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params_.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))

    def test_crossmatch_auf_cf_input(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.cf_region_frame == 'equatorial'
        assert_almost_equal(cm.cf_region_points,
                            np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                      [131, 0], [132, 0], [133, 0], [134, 0],
                                      [131, 1], [132, 1], [133, 1], [134, 1]]))

        f = open(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt')).readlines()
        old_line = 'include_perturb_auf = no'
        new_line = 'include_perturb_auf = yes\n'
        idx = np.where([old_line in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                 'data/crossmatch_params.txt'), idx, new_line,
                                 out_file=os.path.join(
                                 os.path.dirname(__file__), 'data/crossmatch_params_.txt'))
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params_.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.a_auf_region_frame == 'equatorial'
        assert_almost_equal(cm.a_auf_region_points,
                            np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                      [131, 0], [132, 0], [133, 0], [134, 0],
                                      [131, 1], [132, 1], [133, 1], [134, 1]]))
        assert_almost_equal(cm.b_auf_region_points,
                            np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                      [131, -1/3], [132, -1/3], [133, -1/3], [134, -1/3],
                                      [131, 1/3], [132, 1/3], [133, 1/3], [134, 1/3],
                                      [131, 1], [132, 1], [133, 1], [134, 1]]))

        for kind in ['auf_region_', 'cf_region_']:
            in_file = 'crossmatch_params' if 'cf' in kind else 'cat_a_params'
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/{}.txt'.format(in_file))).readlines()
            # List of simple one line config file replacements for error message checking
            for old_line, new_line, match_text in zip(
                ['{}type = rectangle'.format(kind), '{}type = rectangle'.format(kind),
                 '{}points = 131 134 4 -1 1 3'.format(kind),
                 '{}points = 131 134 4 -1 1 3'.format(kind),
                 '{}frame = equatorial'.format(kind), '{}points = 131 134 4 -1 1 3'.format(kind)],
                ['', '{}type = triangle\n'.format(kind),
                 '{}points = 131 134 4 -1 1 a\n'.format(kind),
                 '{}points = 131 134 4 -1 1\n'.format(kind), '{}frame = ecliptic\n'.format(kind),
                 '{}points = 131 134 4 -1 1 3.4\n'.format(kind)],
                ['Missing key {}type'.format(kind),
                 "{}{}type should either be 'rectangle' or".format('' if 'cf' in kind
                                                                   else 'a_', kind),
                 '{}{}points should be 6 numbers'.format('' if 'cf' in kind else 'a_', kind),
                 '{}{}points should be 6 numbers'.format('' if 'cf' in kind else 'a_', kind),
                 "{}{}frame should either be 'equatorial' or".format(
                    '' if 'cf' in kind else 'a_', kind),
                 'start and stop values for {}{}points'.format('' if 'cf' in kind
                                                               else 'a_', kind)]):
                idx = np.where([old_line in line for line in f])[0][0]
                CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                         'data/{}.txt'.format(in_file)), idx, new_line,
                                         out_file=os.path.join(os.path.dirname(__file__),
                                                               'data/{}_.txt'.format(in_file)))

                with pytest.raises(ValueError, match=match_text):
                    cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                                 'data/crossmatch_params{}.txt'.format(
                                                 '_' if 'cf' in kind else '')),
                                    os.path.join(os.path.dirname(__file__),
                                                 'data/cat_a_params{}.txt'.format(
                                                 '_' if 'cf' not in kind else '')),
                                    os.path.join(os.path.dirname(__file__),
                                                 'data/cat_b_params.txt'))

            # Check correct and incorrect *_region_points when *_region_type is 'points'
            idx = np.where(['{}type = rectangle'.format(kind) in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                                      'data/{}.txt'.format(in_file)),
                                     idx, '{}type = points\n'.format(kind),
                                     out_file=os.path.join(os.path.dirname(__file__),
                                                           'data/{}_.txt'.format(in_file)))

            idx = np.where(['{}points = 131 134 4 -1 1 3'.format(kind) in line for
                            line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}_.txt'.format(in_file)), idx,
                                     '{}points = (131, 0), (133, 0), (132, -1)\n'.format(kind),
                                     out_file=os.path.join(os.path.dirname(__file__),
                                                           'data/{}_2.txt'.format(in_file)))

            cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                            'data/crossmatch_params{}.txt'.format('_2' if 'cf' in kind else '')),
                            os.path.join(os.path.dirname(__file__),
                            'data/cat_a_params{}.txt'.format('_2' if 'cf' not in kind else '')),
                            os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
            assert_almost_equal(getattr(cm, '{}{}points'.format('' if 'cf' in kind
                                else 'a_', kind)), np.array([[131, 0], [133, 0], [132, -1]]))

            old_line = '{}points = 131 134 4 -1 1 3'.format(kind)
            for new_line in ['{}points = (131, 0), (131, )\n'.format(kind),
                             '{}points = (131, 0), (131, 1, 2)\n'.format(kind),
                             '{}points = (131, 0), (131, a)\n'.format(kind)]:
                idx = np.where([old_line in line for line in f])[0][0]
                CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                         'data/{}_.txt'.format(in_file)), idx, new_line,
                                         out_file=os.path.join(
                                         os.path.dirname(__file__),
                                         'data/{}_2.txt'.format(in_file)))

                with pytest.raises(ValueError):
                    cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                                 'data/crossmatch_params{}.txt'.format(
                                                 '_2' if 'cf' in kind else '')),
                                    os.path.join(os.path.dirname(__file__),
                                                 'data/cat_a_params{}.txt'.format(
                                                 '_2' if 'cf' not in kind else '')),
                                    os.path.join(os.path.dirname(__file__),
                                                 'data/cat_b_params.txt'))

            # Check single-length point grids are fine
            idx = np.where(['{}points = 131 134 4 -1 1 3'.format(kind) in line
                            for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)),
                                     idx, '{}points = 131 131 1 0 0 1\n'.format(kind),
                                     out_file=os.path.join(os.path.dirname(__file__),
                                                           'data/{}_.txt'.format(in_file)))

            cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                            'data/crossmatch_params{}.txt'.format('_' if 'cf' in kind else '')),
                            os.path.join(os.path.dirname(__file__),
                            'data/cat_a_params{}.txt'.format('_' if 'cf' not in kind else '')),
                            os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
            assert_almost_equal(getattr(cm, '{}{}points'.format('' if 'cf' in kind
                                else 'a_', kind)), np.array([[131, 0]]))

            idx = np.where(['{}type = rectangle'.format(kind) in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)),
                                     idx, '{}type = points\n'.format(kind),
                                     out_file=os.path.join(os.path.dirname(__file__),
                                                           'data/{}_.txt'.format(in_file)))

            idx = np.where(['{}points = 131 134 4 -1 1 3'.format(kind) in
                            line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}_.txt'.format(in_file)),
                                     idx, '{}points = (131, 0)\n'.format(kind),
                                     out_file=os.path.join(os.path.dirname(__file__),
                                                           'data/{}_2.txt'.format(in_file)))

            cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                            'data/crossmatch_params{}.txt'.format('_2' if 'cf' in kind else '')),
                            os.path.join(os.path.dirname(__file__),
                            'data/cat_a_params{}.txt'.format('_2' if 'cf' not in kind else '')),
                            os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
            assert_almost_equal(getattr(cm, '{}{}points'.format('' if 'cf' in kind
                                else 'a_', kind)), np.array([[131, 0]]))

        # Check galactic run is also fine -- here we have to replace all 3 parameter
        # options with "galactic", however.
        for in_file in ['crossmatch_params', 'cat_a_params', 'cat_b_params']:
            kind = 'cf_region_' if 'h_p' in in_file else 'auf_region_'
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/{}.txt'.format(in_file))).readlines()
            idx = np.where(['{}frame = equatorial'.format(kind) in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)),
                                     idx, '{}frame = galactic\n'.format(kind),
                                     out_file=os.path.join(os.path.dirname(__file__),
                                                           'data/{}_.txt'.format(in_file)))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params_.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params_.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params_.txt'))
        for kind in ['auf_region_', 'cf_region_']:
            assert getattr(cm, '{}{}frame'.format('' if 'cf' in kind
                                                  else 'a_', kind)) == 'galactic'
            assert_almost_equal(getattr(cm, '{}{}points'.format('' if 'cf' in kind
                                                                else 'a_', kind)),
                                np.array([[131, -1], [132, -1], [133, -1], [134, -1],
                                          [131, 0], [132, 0], [133, 0], [134, 0],
                                          [131, 1], [132, 1], [133, 1], [134, 1]]))

    def test_crossmatch_folder_path_inputs(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.joint_folder_path == os.path.join(os.getcwd(), 'test_path')
        assert os.path.isdir(os.path.join(os.getcwd(), 'test_path'))
        assert cm.a_auf_folder_path == os.path.join(os.getcwd(), 'gaia_auf_folder')
        assert cm.b_auf_folder_path == os.path.join(os.getcwd(), 'wise_auf_folder')

        # List of simple one line config file replacements for error message checking
        for old_line, new_line, match_text, error, in_file in zip(
                ['joint_folder_path = test_path', 'joint_folder_path = test_path',
                 'auf_folder_path = gaia_auf_folder', 'auf_folder_path = wise_auf_folder'],
                ['', 'joint_folder_path = /User/test/some/path/\n', '',
                 'auf_folder_path = /User/test/some/path\n'],
                ['Missing key', 'Error when trying to create temporary',
                 'Missing key auf_folder_path from catalogue "a"',
                 'folder for catalogue "b" AUF outputs. Please ensure that b_auf_folder_path'],
                [ValueError, OSError, ValueError, OSError],
                ['crossmatch_params', 'crossmatch_params', 'cat_a_params', 'cat_b_params']):
            f = open(os.path.join(os.path.dirname(__file__),
                     'data/{}.txt'.format(in_file))).readlines()
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(error, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params{}.txt'.format(
                                '_' if 'h_p' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_crossmatch_tri_inputs(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert not hasattr(cm, 'a_tri_set_name')

        f = open(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt')).readlines()
        old_line = 'include_perturb_auf = no'
        new_line = 'include_perturb_auf = yes\n'
        idx = np.where([old_line in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                 'data/crossmatch_params.txt'), idx, new_line,
                                 out_file=os.path.join(
                                 os.path.dirname(__file__), 'data/crossmatch_params_.txt'))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params_.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.a_tri_set_name == 'gaiadr2'
        assert np.all(cm.b_tri_filt_names == np.array(['W1', 'W2', 'W3', 'W4']))
        assert cm.a_tri_filt_num == 1
        assert not cm.b_download_tri

        # List of simple one line config file replacements for error message checking
        for old_line, new_line, match_text, in_file in zip(
                ['tri_set_name = gaiadr2', 'tri_filt_num = 11', 'tri_filt_num = 11',
                 'download_tri = no', 'download_tri = no'],
                ['', 'tri_filt_num = a\n', 'tri_filt_num = 3.4\n', 'download_tri = aye\n',
                 'download_tri = yes\n'],
                ['Missing key tri_set_name from catalogue "a"',
                 'tri_filt_num should be a single integer number in catalogue "b"',
                 'tri_filt_num should be a single integer number in catalogue "b"',
                 'Boolean flag key not set', 'a_download_tri is True and run_auf is False'],
                ['cat_a_params', 'cat_b_params', 'cat_b_params', 'cat_a_params', 'cat_a_params']):
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/{}.txt'.format(in_file))).readlines()
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params_.txt'),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_crossmatch_psf_param_inputs(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert not hasattr(cm, 'a_norm_scale_laws')
        assert np.all(cm.b_filt_names == np.array(['W1', 'W2', 'W3', 'W4']))

        f = open(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt')).readlines()
        old_line = 'include_perturb_auf = no'
        new_line = 'include_perturb_auf = yes\n'
        idx = np.where([old_line in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                 'data/crossmatch_params.txt'), idx, new_line,
                                 out_file=os.path.join(
                                 os.path.dirname(__file__), 'data/crossmatch_params_.txt'))

        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params_.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert np.all(cm.a_psf_fwhms == np.array([0.12, 0.12, 0.12]))
        assert np.all(cm.b_norm_scale_laws == np.array([2, 2, 2, 2]))

        # List of simple one line config file replacements for error message checking
        for old_line, new_line, match_text, in_file in zip(
                ['filt_names = G G_BP G_RP', 'filt_names = G G_BP G_RP', 'norm_scale_laws = 2 2 2',
                 'psf_fwhms = 6.08 6.84 7.36 11.99', 'psf_fwhms = 6.08 6.84 7.36 11.99'],
                ['', 'filt_names = G G_BP\n', 'norm_scale_laws = 2 2 a\n',
                 'psf_fwhms = 6.08 6.84 7.36\n', 'psf_fwhms = 6.08 6.84 7.36 word\n'],
                ['Missing key filt_names from catalogue "a"',
                 'a_tri_filt_names and a_filt_names should contain the same',
                 'norm_scale_laws should be a list of floats in catalogue "a"',
                 'b_psf_fwhms and b_filt_names should contain the same',
                 'psf_fwhms should be a list of floats in catalogue "b".'],
                ['cat_a_params', 'cat_a_params', 'cat_a_params', 'cat_b_params', 'cat_b_params']):
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/{}.txt'.format(in_file))).readlines()
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params_.txt'),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_crossmatch_cat_name_inputs(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.b_cat_name == 'WISE'
        assert os.path.exists('{}/test_path/WISE'.format(os.getcwd()))

        f = open(os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt')).readlines()
        old_line = 'cat_name = Gaia'
        new_line = ''
        idx = np.where([old_line in line for line in f])[0][0]
        CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                 'data/cat_a_params.txt'), idx, new_line, out_file=os.path.join(
                                 os.path.dirname(__file__), 'data/cat_a_params_.txt'))

        match_text = 'Missing key cat_name from catalogue "a"'
        with pytest.raises(ValueError, match=match_text):
            cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_a_params_.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))

    def test_crossmatch_search_inputs(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.pos_corr_dist == 11
        assert cm.b_dens_dist == 900

        # List of simple one line config file replacements for error message checking
        for old_line, new_line, match_text, in_file in zip(
                ['pos_corr_dist = 11', 'pos_corr_dist = 11', 'dens_dist = 900', 'dens_dist = 900'],
                ['', 'pos_corr_dist = word\n', '', 'dens_dist = word\n'],
                ['Missing key pos_corr_dist', 'pos_corr_dist must be a float',
                 'Missing key dens_dist from catalogue "b"', 'dens_dist in catalogue "a" must'],
                ['crossmatch_params', 'crossmatch_params', 'cat_b_params', 'cat_a_params']):
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/{}.txt'.format(in_file))).readlines()
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params{}.txt'.format(
                                '_' if 'h_p' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_crossmatch_fourier_inputs(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.real_hankel_points == 10000
        assert cm.four_hankel_points == 10000
        assert cm.four_max_rho == 100

        # List of simple one line config file replacements for error message checking
        for old_line, new_line, match_text in zip(
                ['real_hankel_points = 10000', 'four_hankel_points = 10000', 'four_max_rho = 100'],
                ['', 'four_hankel_points = 10000.1\n', 'four_max_rho = word\n'],
                ['Missing key real_hankel_points', 'four_hankel_points should be an integer.',
                 'four_max_rho should be an integer.']):
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/crossmatch_params.txt')).readlines()
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/crossmatch_params.txt'), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/crossmatch_params_.txt'))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params_.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))

    def test_crossmatch_frame_equality(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert cm.a_auf_region_frame == 'equatorial'
        assert cm.b_auf_region_frame == 'equatorial'
        assert cm.cf_region_frame == 'equatorial'

        # List of simple one line config file replacements for error message checking
        match_text = 'Region frames for c/f and AUF creation must all be the same.'
        for old_line, new_line, in_file in zip(
                ['cf_region_frame = equatorial', 'auf_region_frame = equatorial',
                 'auf_region_frame = equatorial'],
                ['cf_region_frame = galactic\n', 'auf_region_frame = galactic\n',
                 'auf_region_frame = galactic\n'],
                ['crossmatch_params', 'cat_a_params', 'cat_b_params']):
            f = open(os.path.join(os.path.dirname(__file__),
                                  'data/{}.txt'.format(in_file))).readlines()
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params{}.txt'.format(
                                '_' if 'h_p' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_cross_match_extent(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert np.all(cm.cross_match_extent == np.array([131, 138, -3, 3]))

        # List of simple one line config file replacements for error message checking
        in_file = 'crossmatch_params'
        f = open(os.path.join(os.path.dirname(__file__),
                              'data/{}.txt'.format(in_file))).readlines()
        old_line = 'cross_match_extent = 131 138 -3 3'
        for new_line, match_text in zip(
                ['', 'cross_match_extent = 131 138 -3 word\n', 'cross_match_extent = 131 138 -3\n',
                 'cross_match_extent = 131 138 -3 3 1'],
                ['Missing key cross_match_extent', 'All elements of cross_match_extent should be',
                 'cross_match_extent should contain.', 'cross_match_extent should contain']):
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params{}.txt'.format(
                                '_' if 'h_p' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_crossmatch_chunk_num(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert np.all(cm.mem_chunk_num == 10)

        # List of simple one line config file replacements for error message checking
        in_file = 'crossmatch_params'
        f = open(os.path.join(os.path.dirname(__file__),
                              'data/{}.txt'.format(in_file))).readlines()
        old_line = 'mem_chunk_num = 10'
        for new_line, match_text in zip(
                ['', 'mem_chunk_num = word\n', 'mem_chunk_num = 10.1\n'],
                ['Missing key mem_chunk_num', 'mem_chunk_num should be a single integer',
                 'mem_chunk_num should be a single integer']):
            idx = np.where([old_line in line for line in f])[0][0]
            CrossMatch._replace_line(cm, os.path.join(os.path.dirname(__file__),
                                     'data/{}.txt'.format(in_file)), idx, new_line,
                                     out_file=os.path.join(
                                     os.path.dirname(__file__), 'data/{}_.txt'.format(in_file)))

            with pytest.raises(ValueError, match=match_text):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params{}.txt'.format(
                                '_' if 'h_p' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_a_params{}.txt'.format('_' if '_a_' in in_file else '')),
                                os.path.join(os.path.dirname(__file__),
                                'data/cat_b_params{}.txt'.format('_' if '_b_' in in_file else '')))

    def test_crossmatch_shared_data(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert np.all(cm.r == np.linspace(0, 1.185 * 11.99, 10000))
        assert_almost_equal(cm.dr, np.ones(9999, float) * 1.185*11.99/9999)
        assert np.all(cm.rho == np.linspace(0, 100, 10000))
        assert_almost_equal(cm.drho, np.ones(9999, float) * 100/9999)

    def test_cat_folder_path(self):
        cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                        os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        assert os.path.exists(self.a_cat_folder_path)
        assert os.path.exists(self.b_cat_folder_path)
        assert cm.a_cat_folder_path == self.a_cat_folder_path
        assert np.all(np.load('{}/con_cat_astro.npy'.format(
                      self.a_cat_folder_path)).shape == (2, 3))
        assert np.all(np.load('{}/con_cat_photo.npy'.format(
                      self.b_cat_folder_path)).shape == (2, 4))
        assert np.all(np.load('{}/magref.npy'.format(
                      self.b_cat_folder_path)).shape == (2,))

        os.system('rm -rf {}'.format(self.a_cat_folder_path))
        with pytest.raises(OSError, match="a_cat_folder_path does not exist."):
            cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        self.setup_class()

        os.system('rm -rf {}'.format(self.b_cat_folder_path))
        with pytest.raises(OSError, match="b_cat_folder_path does not exist."):
            cm = CrossMatch(os.path.join(os.path.dirname(__file__), 'data/crossmatch_params.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                            os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
        self.setup_class()

        for catpath, file in zip([self.a_cat_folder_path, self.b_cat_folder_path],
                                 ['con_cat_astro', 'magref']):
            os.system('rm {}/{}.npy'.format(catpath, file))
            with pytest.raises(FileNotFoundError,
                               match='{} file not found in catalogue '.format(file)):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
            self.setup_class()

        for name, data, match in zip(['con_cat_astro', 'con_cat_photo', 'con_cat_astro',
                                      'con_cat_photo', 'magref', 'con_cat_astro', 'con_cat_photo',
                                      'magref'],
                                     [np.zeros((2, 2), float), np.zeros((2, 5), float),
                                      np.zeros((2, 3, 4), float), np.zeros(2, float),
                                      np.zeros((2, 2), float), np.zeros((1, 3), float),
                                      np.zeros((3, 4), float), np.zeros(3, float)],
                                     ["Second dimension of con_cat_astro",
                                      "Second dimension of con_cat_photo in",
                                      "Incorrect number of dimensions",
                                      "Incorrect number of dimensions",
                                      "Incorrect number of dimensions",
                                      'Consolidated catalogue arrays for catalogue "b"',
                                      'Consolidated catalogue arrays for catalogue "b"',
                                      'Consolidated catalogue arrays for catalogue "b"']):
            np.save('{}/{}.npy'.format(self.b_cat_folder_path, name), data)
            with pytest.raises(ValueError, match=match):
                cm = CrossMatch(os.path.join(os.path.dirname(__file__),
                                'data/crossmatch_params.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_a_params.txt'),
                                os.path.join(os.path.dirname(__file__), 'data/cat_b_params.txt'))
            self.setup_class()
