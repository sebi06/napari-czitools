from pylibCZIrw import czi as pyczi
from czitools.metadata_tools.czi_metadata import CziMetadata
from czitools.metadata_tools import czi_metadata as czimd
from czitools.utils import logging_tools, misc, pixels
from czitools.read_tools import read_tools


# czifile = r"F:\Github\digicontrast\combined_assembly_stack_pyramid.czi"
czifile = r"F:\Github\czitools\data\w96_A1+A2.czi"

# determine shape of combines stack
mdata = CziMetadata(czifile)

mdata_nested = czimd.create_md_dict_nested(mdata, sort=True, remove_none=True)
mdata_nested.pop("bbox", None)

# return an array with dimension order STCZYX(A)
array6d, metadata = read_tools.read_6darray(
    czifile,
    use_xarray=True,
    planes={},
)

print(f"Array shape: {array6d.shape}")
