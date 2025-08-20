try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._reader import napari_get_reader

# from ._sample_data import make_sample_data
from ._sample_data import (
    airyscan_zstack_data,
    celldivision_data,
    he_stain_data,
    wellplate_data,
    zstack_data,
)
from ._widget import (
    CziReaderWidget,
)

__all__ = (
    "napari_get_reader",
    "celldivision_data",
    "wellplate_data",
    "zstack_data",
    "airyscan_zstack_data",
    "he_stain_data",
    "CziReaderWidget",
)
