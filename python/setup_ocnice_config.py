#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
'''
Creates a config file for ACME ice-ocean analysis given a number of environment
variables set in one of the run_<machine>.csh scripts and the default config
file from MPAS-Analysis

Authors
-------
Xylar Asay-Davis

Modified
--------
2017/12/03
'''

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import os
import six
from six.moves.configparser import RawConfigParser


def add_config_option(config, section, option, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)


def check_env(envVarName):
    return os.environ[envVarName].lower() in ['1', 't', 'true']


inFileName = 'python/MPAS-Analysis/mpas_analysis/config.default'
outFileName = os.environ['config_file']

config = RawConfigParser()
config.read(inFileName)

# Turn off generation of MPAS-Analysis html page by default
add_config_option(config, 'html', 'generate', 'False')

add_config_option(config, 'runs', 'mainRunName',
                  os.environ['test_casename'])
add_config_option(config, 'runs', 'preprocessedReferenceRunName',
                  os.environ['ref_case_v0'])

baseDir = '{}/{}'.format(os.environ['test_archive_dir'],
                         os.environ['test_casename'])

scratchDir = os.environ['test_scratch_dir']

add_config_option(config, 'input', 'baseDirectory', baseDir)
add_config_option(config, 'input', 'runSubdirectory', 'run')
add_config_option(config, 'input', 'oceanNamelistFileName', 'run/mpas-o_in')
add_config_option(config, 'input', 'oceanStreamsFileName', 'run/streams.ocean')
add_config_option(config, 'input', 'seaIceNamelistFileName', 'run/mpas-cice_in')
add_config_option(config, 'input', 'seaIceStreamsFileName', 'run/streams.cice')
if check_env('test_short_term_archive'):
    add_config_option(config, 'input', 'oceanHistorySubdirectory', 'archive/ocn/hist')
    add_config_option(config, 'input', 'seaIceHistorySubdirectory', 'archive/ice/hist')
else:
    add_config_option(config, 'input', 'oceanHistorySubdirectory', 'run')
    add_config_option(config, 'input', 'seaIceHistorySubdirectory', 'run')
add_config_option(config, 'input', 'mpasMeshName',
                  os.environ['test_mpas_mesh_name'])
add_config_option(config, 'input', 'autocloseFileLimitFraction',
                  os.environ['mpasAutocloseFileLimitFraction'])

add_config_option(config, 'output', 'baseDirectory',
                  os.environ['output_base_dir'])
add_config_option(config, 'output', 'scratchSubdirectory',
                  os.environ['test_scratch_dir'])
add_config_option(config, 'output', 'plotsSubdirectory',
                  os.environ['plots_dir'])
add_config_option(config, 'output', 'logsSubdirectory',
                  os.environ['log_dir'])
add_config_option(config, 'output', 'mappingSubdirectory',
                  '{}/mapping'.format(scratchDir))
add_config_option(config, 'output', 'mpasClimatologySubdirectory',
                  '{}/clim/mpas/'.format(scratchDir))
add_config_option(config, 'output', 'mpasRegriddedClimSubdirectory',
                  '{}/clim/mpas/regridded'.format(scratchDir))
add_config_option(config, 'output', 'timeSeriesSubdirectory',
                  '{}/timeSeries/'.format(scratchDir))

generate = []
if check_env('generate_ohc_trends'):
    generate.append('timeSeriesOHC')
if check_env('generate_sst_trends'):
    generate.append('timeSeriesSST')
if check_env('generate_nino34'):
    generate.append('indexNino34')
if check_env('generate_mht'):
    generate.append('meridionalHeatTransport')
if check_env('generate_moc'):
    generate.append('streamfunctionMOC')

for field in ['sst', 'sss', 'mld']:
    if check_env('generate_{}_climo'.format(field)):
        generate.append('climatologyMap{}'.format(field.upper()))

if check_env('generate_seaice_trends'):
    generate.append('timeSeriesSeaIceAreaVol')
if check_env('generate_seaice_climo'):
    generate.append('climatologyMapSeaIceConcNH')
    generate.append('climatologyMapSeaIceConcSH')
    generate.append('climatologyMapSeaIceThickNH')
    generate.append('climatologyMapSeaIceThickSH')

generateString = ', '.join(["'{}'".format(element)
                            for element in generate])

add_config_option(config, 'output', 'generate',
                  '[{}]'.format(generateString))

add_config_option(config, 'climatology', 'startYear',
                  os.environ['test_begin_yr_climo'])
add_config_option(config, 'climatology', 'endYear',
                  os.environ['test_end_yr_climo'])
add_config_option(config, 'climatology', 'mpasMappingFile',
                  os.environ['mpas_remapfile'])

add_config_option(config, 'timeSeries', 'startYear',
                  os.environ['test_begin_yr_ts'])
add_config_option(config, 'timeSeries', 'endYear',
                  os.environ['test_end_yr_ts'])

add_config_option(config, 'index', 'startYear',
                  os.environ['test_begin_yr_climateIndex_ts'])
add_config_option(config, 'index', 'endYear',
                  os.environ['test_end_yr_climateIndex_ts'])

add_config_option(config, 'oceanObservations', 'baseDirectory',
                  os.environ['obs_ocndir'])
for field in ['sst', 'sss', 'mld', 'mht', 'nino']:
    add_config_option(config, 'oceanObservations',
                      '{}Subdirectory'.format(field),
                      os.environ['obs_{}dir'.format(field)])
add_config_option(config, 'oceanObservations', 'climatologySubdirectory',
                  '{}/clim/obs/'.format(scratchDir))
add_config_option(config, 'oceanObservations', 'regriddedClimSubdirectory',
                  '{}/clim/obs/regridded'.format(scratchDir))

add_config_option(config, 'oceanPreprocessedReference', 'baseDirectory',
                  os.environ['ref_archive_v0_ocndir'])

add_config_option(config, 'seaIceObservations', 'baseDirectory',
                  os.environ['obs_seaicedir'])
add_config_option(config, 'seaIceObservations', 'climatologySubdirectory',
                  '{}/clim/obs/'.format(scratchDir))
add_config_option(config, 'seaIceObservations', 'regriddedClimSubdirectory',
                  '{}/clim/obs/regridded'.format(scratchDir))

add_config_option(config, 'seaIcePreprocessedReference', 'baseDirectory',
                  os.environ['ref_archive_v0_seaicedir'])

add_config_option(config, 'streamfunctionMOC', 'regionMaskFiles',
                  os.environ['mpaso_regions_file'])

if check_env('run_batch_script'):
    add_config_option(config, 'execute', 'parallelTaskCount',
                      os.environ['mpas_analysis_tasks'])
    add_config_option(config, 'execute', 'commandPrefix',
                      os.environ['command_prefix'])
add_config_option(config, 'execute', 'ncclimoParallelMode',
                  os.environ['ncclimoParallelMode'])

filePointer = open(outFileName, 'w')
config.write(filePointer)
filePointer.close()
