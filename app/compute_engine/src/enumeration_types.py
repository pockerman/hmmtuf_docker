from enum import Enum

from compute_engine.src.constants import DEFAULT_ERROR_EXPLANATION

class JobResultEnum(Enum):
    """
    Job result enumeration
    """
    PENDING = 0
    FAILURE = 1
    SUCCESS = 2
    CREATED = 4

class JobType(Enum):
    """
    Job type enumeration
    """
    VITERBI = 0
    EXTRACT_REGION = 1
    GROUP_VITERBI = 3
    VITERBI_SEQUENCE_COMPARE = 4
    VITERBI_GROUP_ALL = 5
    KMER = 6
    BED_COMPARISON = 7

class BackendType(Enum):
    """
    Backend type enumeration
    """
    SKLEARN = 0
    PYTORCH = 1

class ClassifierType(Enum):
    """
    Classifier type enumeration
    """
    SKLEARN_LOGISTIC_REGRESSOR = 0
    PYTORCH_LOGISTIC_REGRESSOR = 1


class FileReaderType(Enum):
    """
    Enumeration to distinguish various file readers
    """
    TUF_BED = 0
    TDT_BED = 1
    NUCL_OUT = 3
    GQUADS = 4
    DELETION_BED = 5
    DUPLICATION_BED = 6
    GAP_BED = 7
    NORMAL_BED = 8
    VITERBI_BED_GRAPH = 9
    QUAD_BED = 10
    REP_BED = 11
    REPEATS_INFO_BED = 12
    VITERBI_PATH = 13
    NUCL_OUT_MISSING = 14


