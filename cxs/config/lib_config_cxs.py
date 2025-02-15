"""
Management of CXS configuration files.
"""

from __future__ import print_function
import os
if os.environ.get("is_legacy"):
    from const_config import *
else:
    from cxs.config.const_config_cxs import *

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
    

def get_configuration(file_log, config_file, v=0):
    """
    Read parameters from configuration file "configh.conf".
    
    Parameters
    ----------
     file_log : handler to file
         handler to log file.
     config_file : str
         path to CorrelX configuration file.
     timestamp_str : str
         suffix to be added to temporary data folder (hwere media will be split).
     v : int
         verbose if 1.
     
    Returns
    -------
     FFT_AT_MAPPER : bool
         Boolean, if 0 FFT is done at reducer (default).
     DATA_DIR : str
         Path with media input files.
     INI_FOLDER : str
         Folder with experiment .ini files.
     INI_STATIONS : str
         Stations ini file name.
     INI_SOURCES : str
         Sources ini file name.
     INI_DELAY_MODEL : str
         Delay model ini file name.
     INI_DELAYS : str
         Delay polynomials ini file name.
     INI_MEDIA : str
         Media ini file name.
     INI_CORRELATION : str
         Correlation ini file name.
     INTERNAL_LOG_MAPPER
         [remove] currently default 0.
     INTERNAL_LOG_REDUCER
         [remove] currenlty default 0.
     FFTS_PER_CHUNK
        [Remove] Number of DFT windows per mapper output, -1 by default (whole frame)
     ONE_BASELINE_PER_TASK : int
        0 by default (if 1, old implementation allowed scaling with one baseline per task in the reducers).
     MIN_MAPPER_CHUNK
        [Remove] Chunk constraints for mapper (-1).
     MAX_MAPPER_CHUNK
        [Remove] Chunk constraints for mapper (-1).
     TASK_SCALING_STATIONS: int
        0 by default (if 1, old implementation allowed linear scaling per task in the reducers).

    Notes
    -----
    |
    | **Configuration:**
    |
    |  All constants taken from const_config.py and const_hadoop.py.
    |
    |
    | **TO DO:**
    |
    |  OVER_SLURM: explain better, and check assumptions.
    |  Remove INTERNAL_LOG_MAPPER and INTERNAL_LOG_REDUCER.
    |  Remove FFTS_PER_CHUNK,MIN_MAPPER_CHUNK and MAX_MAPPER_CHUNK.
    |  Check that SINGLE_PRECISION is followed in mapper and reducer.
    """
    
   
    #config_file="configh.conf"
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_file)

    INTERNAL_LOG_MAPPER =    0                                                                # TO DO: remove
    INTERNAL_LOG_REDUCER =   0                                                                # TO DO: remove

    if v==1:
        print("\nReading configuration file...",file=file_log)    

    # Misc (Hadoop-other in legacy)
    # FFT at mapper:              no
    #FFT_AT_MAPPER =          config.getboolean( C_CONF_MISC, C_CONF_OTHER_FFT_MAP)
    FFT_AT_MAPPER = False

    #Task scaling stations: no
    #TASK_SCALING_STATIONS =  config.getboolean( C_CONF_MISC, C_CONF_OTHER_SCALING_STATIONS)
    TASK_SCALING_STATIONS = False

    #One baseline per task: no
    #ONE_BASELINE_PER_TASK =  config.getboolean( C_CONF_MISC, C_CONF_OTHER_ONE_BASELINE)
    ONE_BASELINE_PER_TASK = False

    SINGLE_PRECISION =       config.getboolean( C_CONF_MISC, C_CONF_OTHER_SINGLE_PRECISION, fallback=False)
    FFTS_PER_CHUNK =         -1                                                                # TO DO: remove
    MIN_MAPPER_CHUNK =       -1                                                                # TO DO: remove
    MAX_MAPPER_CHUNK =       -1                                                                # TO DO: remove
    
    
    
    # Experiment
    INI_FOLDER =                         config.get(   C_CONF_EXP, C_CONF_EXP_FOLDER)
    INI_STATIONS = INI_FOLDER + "/" +    config.get(   C_CONF_EXP, C_CONF_EXP_STATIONS, fallback="stations.ini")
    INI_SOURCES = INI_FOLDER + "/" +     config.get(   C_CONF_EXP, C_CONF_EXP_SOURCES, fallback="sources.ini")
    INI_DELAYS = INI_FOLDER + "/" +      config.get(   C_CONF_EXP, C_CONF_EXP_DELAYS, fallback="delays.ini")
    INI_DELAY_MODEL = INI_FOLDER + "/" + config.get(   C_CONF_EXP, C_CONF_EXP_DELAY_MODEL, fallback="delay_model.ini")
    INI_MEDIA = INI_FOLDER + "/" +       config.get(   C_CONF_EXP, C_CONF_EXP_MEDIA, fallback="media.ini")
    INI_CORRELATION = INI_FOLDER + "/" + config.get(   C_CONF_EXP, C_CONF_EXP_CORRELATION, fallback="correlation.ini")
    #DATA_DIR = INI_FOLDER + "/" +        config.get(   C_CONF_EXP, C_CONF_EXP_MEDIA_SUB) + "/"
    DATA_DIR =                           config.get(   C_CONF_EXP, C_CONF_EXP_MEDIA_SPARK)
    #DATA_DIR = None

    # Files
    SPARK_HOME_DIR =     config.get(       C_CONF_FILES, C_CONF_FILES_SPARK_HOME_DIR, fallback=None)
    OUTPUT_DIR =         config.get(       C_CONF_FILES, C_CONF_FILES_OUT_DIR)
    if OUTPUT_DIR[-1]!="/":
        OUTPUT_DIR+=("/")
    PREFIX_OUTPUT =      config.get(       C_CONF_FILES, C_CONF_FILES_PREFIX_OUTPUT, fallback="OUT")


    # Spark

    spark_config_pairs = None
    if C_CONF_SPARK in config.sections():
        spark_config_pairs = [list(j) for j in config.items(C_CONF_SPARK)]

    if not os.path.isdir(INI_FOLDER):
        raise Exception("Cannot find experiment folder: {}".format(INI_FOLDER))

    FILES = [
        INI_STATIONS,
        INI_SOURCES,
        #INI_DELAYS,
        INI_DELAY_MODEL,
        INI_MEDIA,
        INI_CORRELATION,
    ]

    for x in FILES:
        if not os.path.isfile(x):
            raise Exception("Cannot find experiment configuration file: {}".format(x))

    #if not os.path.isdir(DATA_DIR):
    #    raise Exception("Cannot find experiment data dir: {}".format(DATA_DIR))

    config = ConfigCXS(
        fft_at_mapper=FFT_AT_MAPPER,
        data_dir=DATA_DIR,
        ini_folder=INI_FOLDER,
        ini_stations=INI_STATIONS,
        ini_sources=INI_SOURCES,
        ini_delay_model=INI_DELAY_MODEL,
        ini_delays=INI_DELAYS,
        ini_media=INI_MEDIA,
        ini_correlation=INI_CORRELATION,
        internal_log_mapper=INTERNAL_LOG_MAPPER,
        internal_log_reducer=INTERNAL_LOG_REDUCER,
        ffts_per_chunk=FFTS_PER_CHUNK,
        one_baseline_per_task=ONE_BASELINE_PER_TASK,
        min_mapper_chunk=MIN_MAPPER_CHUNK,
        max_mapper_chunk=MAX_MAPPER_CHUNK,
        task_scaling_stations=TASK_SCALING_STATIONS,
        single_precision=SINGLE_PRECISION,
        out_dir=OUTPUT_DIR,
        out_prefix=PREFIX_OUTPUT,
        spark_config_pairs=spark_config_pairs,
        spark_home=SPARK_HOME_DIR
    )
    return config
