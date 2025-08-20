from czitools.utils import logging_tools

from napari_czitools._reader import reader_function
from napari_czitools._utilities import check_filepath

logger = logging_tools.set_logging()


def celldivision_data():
    """Opens 5D CZI image dataset"""

    filepath = check_filepath("CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi")

    if filepath is None:
        logger.error("Could not find celldivision sample data file")
        raise FileNotFoundError("Sample data file not found - this is normal in CI/CD environments")

    return return_result(filepath)


def wellplate_data():
    """Opens 6D CZI image dataset"""

    filepath = check_filepath("testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi")

    if filepath is None:
        logger.error("Could not find wellplate sample data file")
        raise FileNotFoundError("Sample data file not found - this is normal in CI/CD environments")

    return return_result(filepath)


def zstack_data():
    """Opens 3D CZI image dataset"""

    filepath = check_filepath("RatBrain_Z79_ZSTD.czi")

    if filepath is None:
        logger.error("Could not find zstack sample data file")
        raise FileNotFoundError("Sample data file not found - this is normal in CI/CD environments")

    return return_result(filepath)


def airyscan_zstack_data():
    """Opens 3D CZI image dataset"""

    filepath = check_filepath("20X_SR-Airyscan_JDCV.czi")

    if filepath is None:
        logger.error("Could not find airyscan sample data file")
        raise FileNotFoundError("Sample data file not found - this is normal in CI/CD environments")

    return return_result(filepath)


def he_stain_data():
    """Opens HE stain CZI image dataset"""

    filepath = check_filepath("Tumor_HE_Orig_small.czi")

    if filepath is None:
        logger.error("Could not find HE Stain sample data file")
        raise FileNotFoundError("Sample data file not found - this is normal in CI/CD environments")

    return return_result(filepath)


def return_result(filepath):

    try:
        result = reader_function(filepath)
        if result is None or len(result) == 0:
            logger.error("Reader function returned empty data")
            raise ValueError("Sample data reader returned empty data - this is normal in CI/CD environments")
        return result
    except (FileNotFoundError, OSError, ValueError, AttributeError) as e:
        logger.error("Failed to read sample data: %s", str(e))
        # In headless environments or when reading from URLs fails, this is expected
        logger.info("Sample data unavailable - this is normal in CI/CD environments")
        raise FileNotFoundError("Sample data unavailable in headless/CI environment") from e


if __name__ == "__main__":

    import os

    path = check_filepath("CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi")
    print(f"Sample data filepath: {path}")
    if os.path.exists(path):
        print(f"File exists: {path}")

    celldivision_data()

    wellplate_data()

    zstack_data()

    airyscan_zstack_data()
