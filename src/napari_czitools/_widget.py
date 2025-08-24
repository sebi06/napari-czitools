"""
References:
- Widget specification: https://napari.org/stable/plugins/guides.html?#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/

Replace code below according to your needs.
"""

import contextlib
import os
from enum import Enum
from typing import TYPE_CHECKING

from czitools.metadata_tools import czi_metadata as czimd
from czitools.metadata_tools.czi_metadata import CziMetadata
from czitools.utils import logging_tools
from magicgui.types import FileDialogMode
from magicgui.widgets import ComboBox, FileEdit, PushButton
from qtpy.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ._doublerange_slider import LabeledDoubleRangeSliderWidget
from ._metadata_widget import MdTableWidget, MdTreeWidget, MetadataDisplayMode
from ._range_widget import RangeSliderWidget
from ._reader import reader_function_adv
from ._utilities import _convert_numpy_types

logger = logging_tools.set_logging()

if TYPE_CHECKING:
    import napari


class SliderType(Enum):
    TwoSliders = 1
    DoubleRangeSlider = 2


class CziReaderWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        sliders=SliderType.DoubleRangeSlider,
        show_type_column=True,
    ):
        super().__init__()
        # store the viewer instance for later use
        self.viewer = viewer
        self.show_type_column = show_type_column

        self.sliders = SliderType(sliders)

        # create a layout
        self.main_layout = QVBoxLayout()

        # 1. FileDialog Section
        file_layout = QHBoxLayout()
        file_label = QLabel("Select CZI Image:")
        file_layout.addWidget(file_label)

        # define filter based on file extension
        model_extension = "*.czi"
        self.filename_edit = FileEdit(mode=FileDialogMode.EXISTING_FILE, value="", filter=model_extension)
        file_layout.addWidget(self.filename_edit.native)
        self.filename_edit.line_edit.changed.connect(self._file_changed)

        # 2. ComboBox and Type Column Checkbox Section
        mdcombo_layout = QHBoxLayout()
        mdcombo_label = QLabel("Metadata Display:")

        self.mdata_widget = ComboBox(
            value="Table",
            choices=["Table", "Tree"],
            label="Metadata Display",
        )
        self.mdata_widget.changed.connect(self._mdwidget_changed)
        mdcombo_layout.addWidget(mdcombo_label)
        mdcombo_layout.addWidget(self.mdata_widget.native)

        # Add checkbox for type column visibility
        self.type_column_checkbox = QCheckBox("Show Type Column")
        self.type_column_checkbox.setChecked(self.show_type_column)
        self.type_column_checkbox.stateChanged.connect(self._type_column_changed)
        # Initially hide the checkbox since default display is Table
        self.type_column_checkbox.hide()
        mdcombo_layout.addWidget(self.type_column_checkbox)

        # 3. Slider Type Section - separate layout positioned under metadata display
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Slider Type:")

        self.slidertype_widget = ComboBox(
            value="DoubleRangeSlider",
            choices=["DoubleRangeSlider", "TwoSliders"],
            label="Slider Type",
        )
        self.slidertype_widget.changed.connect(self._slider_type_changed)
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.slidertype_widget.native)

        # Pushbutton to load pixel data
        self.load_pixeldata = PushButton(
            name="Load Pixel Data",
            visible=True,
            enabled=False,
        )
        # self.load_pixeldata.native.setStyleSheet("border: 1px solid blue;")
        self.load_pixeldata.native.clicked.connect(self._loadbutton_pressed)

        self.mdtable = MdTableWidget()
        # self.mdtable.setStyleSheet("border: 1px solid red;")
        self.mdtable.setMinimumHeight(400)  # Set minimum height for the table
        self.mdtable.update_metadata({})
        self.mdtable.update_style(font_bold=False, font_size=6)

        self.mdtree = MdTreeWidget(show_type_column=self.show_type_column)
        # self.mdtree.setStyleSheet("border: 1px solid red;")
        self.mdtree.setMinimumHeight(400)  # Set minimum height for the table

        self.current_md_widget = self.mdtable
        self.spacer_item = QSpacerItem(100, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Add all widgets to the main layout
        self.main_layout.addLayout(file_layout)  # Add FileDialog section
        self.main_layout.addLayout(mdcombo_layout)  # Add ComboBox
        self.main_layout.addLayout(slider_layout)  # Add Slider Type section

        self.main_layout.addWidget(self.mdtable)  # Add the native Qt widget of the table
        self.main_layout.addItem(self.spacer_item)
        self.main_layout.addWidget(self.load_pixeldata.native)

        # Define Dimension slider configurations
        slider_configs = [
            ("Scene", "scene_slider"),
            ("Time", "time_slider"),
            ("Channel", "channel_slider"),
            ("Z-Plane", "z_slider"),
        ]

        if self.sliders == SliderType.TwoSliders:
            # Create two sliders dynamically
            for label, attr_name in slider_configs:
                slider = RangeSliderWidget(
                    dimension_label=label,
                    min_value=0,
                    max_value=0,
                    readout=True,
                    visible=True,
                    enabled=False,
                )
                setattr(self, attr_name, slider)

            self.main_layout.addWidget(self.scene_slider.native)
            self.main_layout.addWidget(self.time_slider.native)
            self.main_layout.addWidget(self.channel_slider.native)
            self.main_layout.addWidget(self.z_slider.native)

        if self.sliders == SliderType.DoubleRangeSlider:
            # Create double-range sliders dynamically
            for label, attr_name in slider_configs:
                slider = LabeledDoubleRangeSliderWidget(
                    dimension_label=label,
                    min_value=0,
                    max_value=0,
                    readout=True,
                    visible=True,
                    enabled=False,
                )
                setattr(self, attr_name, slider)

            self.main_layout.addWidget(self.scene_slider)
            self.main_layout.addWidget(self.time_slider)
            self.main_layout.addWidget(self.channel_slider)
            self.main_layout.addWidget(self.z_slider)

        # set the layout
        self.setLayout(self.main_layout)

    def _file_changed(self):
        """Callback for when the file edit changes."""
        filepath = self.filename_edit.value
        logger.info("File changed to: %s", filepath)

        # Reset metadata widgets first - clear any previous data
        self._reset_metadata_widgets()

        # Reset range sliders to default state
        self._reset_range_sliders()

        # Disable the load pixel data button until new metadata is loaded
        self.load_pixeldata.enabled = False

        # If filepath is empty, just leave the widgets reset
        if not filepath:
            return

        # Create metadata from the selected file
        try:
            self.metadata = CziMetadata(filepath)
        except (FileNotFoundError, ValueError, OSError) as e:
            logger.error("Failed to load metadata from file %s: %s", filepath, str(e))
            return

        # create a nested dictionary for the tree and a reduced dictionary for the table
        md_dict_tree = czimd.create_md_dict_nested(self.metadata, sort=True, remove_none=True)
        # drop certain entries
        md_dict_tree.pop("bbox", None)
        self.mdtree.setData(md_dict_tree, expandlevel=0, hideRoot=True)

        md_dict_table = czimd.create_md_dict_red(self.metadata, sort=True, remove_none=True)

        # Convert all numpy values to native Python types for better display
        with contextlib.suppress(Exception):  # Catch any conversion errors
            md_dict_table = _convert_numpy_types(md_dict_table)

        self.mdtable.update_metadata(md_dict_table)

        # Update sliders based on metadata
        slider_mapping = {
            "SizeS": self.scene_slider,
            "SizeT": self.time_slider,
            "SizeC": self.channel_slider,
            "SizeZ": self.z_slider,
        }

        if self.sliders == SliderType.TwoSliders:

            for size_attr, slider in slider_mapping.items():
                size_value = getattr(self.metadata.image, size_attr, None)
                # logger.info("Size attribute %s has value: %s", size_attr, size_value)
                if size_value is not None and size_value > 1:
                    # Update the range for both sliders first
                    slider.min_slider.min = 0
                    slider.min_slider.max = size_value - 1
                    slider.max_slider.min = 0
                    slider.max_slider.max = size_value - 1

                    # Set the values
                    slider.min_slider.value = 0
                    slider.max_slider.value = size_value - 1

                    # Enable the slider after setting up the range
                    slider.enabled = True
                else:
                    # Reset slider if size_value is None
                    slider.enabled = False
                    slider.min_slider.min = 0
                    slider.min_slider.max = 0
                    slider.max_slider.min = 0
                    slider.max_slider.max = 0
                    slider.min_slider.value = 0
                    slider.max_slider.value = 0

            # Enable the load pixel data button
            self.load_pixeldata.enabled = True

            # Ensure layout updates dynamically
            self.main_layout.update()

        elif self.sliders == SliderType.DoubleRangeSlider:

            for size_attr, slider in slider_mapping.items():
                size_value = getattr(self.metadata.image, size_attr, None)
                if size_value is not None and size_value > 1:
                    # Update the range limits first
                    slider.setMinimum(0)
                    slider.setMaximum(size_value - 1)

                    # Set the actual slider positions to span the full range
                    slider.setLow(0)
                    slider.setHigh(size_value - 1)

                    # Enable the slider after setting up the range
                    slider.setEnabled(True)
                else:
                    # Reset slider if size_value is None
                    slider.setEnabled(False)
                    slider.setVisible(False)
                    slider.setMinimum(0)
                    slider.setMaximum(0)
                    slider.setLow(0)
                    slider.setHigh(0)

            # Enable the load pixel data button
            self.load_pixeldata.enabled = True

            # Ensure layout updates dynamically
            self.main_layout.update()

    def _mdwidget_changed(self):
        # Remove the current widget
        self.main_layout.removeWidget(self.current_md_widget)
        self.current_md_widget.hide()

        # Toggle to the other widget
        if self.current_md_widget == self.mdtable:
            self.current_md_widget = self.mdtree
            # Show the type column checkbox when tree is selected
            self.type_column_checkbox.show()
        else:
            self.current_md_widget = self.mdtable
            # Hide the type column checkbox when table is selected
            self.type_column_checkbox.hide()

        # Add the new widget to the layout
        self.main_layout.insertWidget(2, self.current_md_widget)
        self.current_md_widget.show()

    def _reset_metadata_widgets(self):
        """Reset both metadata table and tree widgets to clear previous data."""
        # Clear the tree widget using the convenience method
        self.mdtree.clear()

        # Clear the table widget using the convenience method
        self.mdtable.setRowCount(0)

    def _reset_range_sliders(self):
        """Reset all range sliders to default state when file changes."""
        slider_list = [self.scene_slider, self.time_slider, self.channel_slider, self.z_slider]

        if self.sliders == SliderType.TwoSliders:
            for slider in slider_list:
                # Disable the slider first
                slider.enabled = False

                # Reset both min and max sliders to default values
                slider.min_slider.min = 0
                slider.min_slider.max = 0
                slider.max_slider.min = 0
                slider.max_slider.max = 0
                slider.min_slider.value = 0
                slider.max_slider.value = 0

        elif self.sliders == SliderType.DoubleRangeSlider:
            for slider in slider_list:
                # Disable the slider first
                slider.setEnabled(False)

                # Reset the double range slider to default values
                slider.setMinimum(0)
                slider.setMaximum(0)
                slider.setLow(0)
                slider.setHigh(0)
                slider.setVisible(True)  # Ensure visibility is reset

    def _type_column_changed(self):
        """Callback for when the type column checkbox changes."""
        show_type = self.type_column_checkbox.isChecked()
        self.show_type_column = show_type
        # Update the tree widget's type column visibility
        self.mdtree.set_type_column_visibility(visible=show_type, column_id=2)

    def _loadbutton_pressed(self):

        if self.sliders == SliderType.TwoSliders:
            # get the require values to read the pixel data and show the layers
            planes = {
                "S": (
                    self.scene_slider.min_slider.value,
                    self.scene_slider.max_slider.value,
                ),
                "T": (
                    self.time_slider.min_slider.value,
                    self.time_slider.max_slider.value,
                ),
                "C": (
                    self.channel_slider.min_slider.value,
                    self.channel_slider.max_slider.value,
                ),
                "Z": (
                    self.z_slider.min_slider.value,
                    self.z_slider.max_slider.value,
                ),
            }
        elif self.sliders == SliderType.DoubleRangeSlider:
            # get the require values to read the pixel data and show the layers
            planes = {
                "S": (self.scene_slider.low(), self.scene_slider.high()),
                "T": (self.time_slider.low(), self.time_slider.high()),
                "C": (self.channel_slider.low(), self.channel_slider.high()),
                "Z": (self.z_slider.low(), self.z_slider.high()),
            }

        logger.info(
            "Read Pixel data for file: %s - Planes: %s",
            os.path.basename(self.filename_edit.value),
            planes,
        )
        reader_function_adv(
            self.filename_edit.value,
            zoom=1.0,
            planes=planes,
            show_metadata=MetadataDisplayMode.NONE,
        )

    def _slider_type_changed(self, value):
        """Callback for when the slider type combo box changes."""
        if value == "DoubleRangeSlider":
            new_slider_type = SliderType.DoubleRangeSlider
        elif value == "TwoSliders":
            new_slider_type = SliderType.TwoSliders
        else:
            return  # Invalid value, do nothing

        # Only proceed if the slider type actually changed
        if new_slider_type == self.sliders:
            return

        # Remove existing sliders from layout and delete them
        self._remove_existing_sliders()

        # Update the slider type
        self.sliders = new_slider_type

        # Create new sliders with the new type
        self._create_sliders()

        # If we have metadata loaded, update the new sliders
        if hasattr(self, "metadata") and self.metadata is not None:
            self._update_sliders_from_metadata()

    def _remove_existing_sliders(self):
        """Remove existing sliders from layout and delete them."""
        slider_names = ["scene_slider", "time_slider", "channel_slider", "z_slider"]

        for slider_name in slider_names:
            if hasattr(self, slider_name):
                slider = getattr(self, slider_name)
                # Remove from layout
                if hasattr(slider, "native"):
                    # TwoSliders type has .native attribute
                    self.main_layout.removeWidget(slider.native)
                    slider.native.setParent(None)
                else:
                    # DoubleRangeSlider type is added directly
                    self.main_layout.removeWidget(slider)
                    slider.setParent(None)
                # Delete the attribute
                delattr(self, slider_name)

    def _create_sliders(self):
        """Create sliders based on current slider type."""
        slider_configs = [
            ("Scene", "scene_slider"),
            ("Time", "time_slider"),
            ("Channel", "channel_slider"),
            ("Z-Plane", "z_slider"),
        ]

        if self.sliders == SliderType.TwoSliders:
            # Create two sliders dynamically
            for label, attr_name in slider_configs:
                slider = RangeSliderWidget(
                    dimension_label=label,
                    min_value=0,
                    max_value=0,
                    readout=True,
                    visible=True,
                    enabled=False,
                )
                setattr(self, attr_name, slider)
                self.main_layout.addWidget(slider.native)

        elif self.sliders == SliderType.DoubleRangeSlider:
            # Create double-range sliders dynamically
            for label, attr_name in slider_configs:
                slider = LabeledDoubleRangeSliderWidget(
                    dimension_label=label,
                    min_value=0,
                    max_value=0,
                    readout=True,
                    visible=True,
                    enabled=False,
                )
                setattr(self, attr_name, slider)
                self.main_layout.addWidget(slider)

    def _update_sliders_from_metadata(self):
        """Update sliders based on current metadata (called after slider type change)."""
        if not hasattr(self, "metadata") or self.metadata is None:
            return

        slider_mapping = {
            "SizeS": self.scene_slider,
            "SizeT": self.time_slider,
            "SizeC": self.channel_slider,
            "SizeZ": self.z_slider,
        }

        if self.sliders == SliderType.TwoSliders:
            for size_attr, slider in slider_mapping.items():
                size_value = getattr(self.metadata.image, size_attr, None)
                if size_value is not None and size_value > 1:
                    slider.min_slider.min = 0
                    slider.min_slider.max = size_value - 1
                    slider.max_slider.min = 0
                    slider.max_slider.max = size_value - 1
                    slider.min_slider.value = 0
                    slider.max_slider.value = size_value - 1
                    slider.enabled = True
                else:
                    slider.enabled = False

        elif self.sliders == SliderType.DoubleRangeSlider:
            for size_attr, slider in slider_mapping.items():
                size_value = getattr(self.metadata.image, size_attr, None)
                if size_value is not None and size_value > 1:
                    slider.setMinimum(0)
                    slider.setMaximum(size_value - 1)
                    slider.setLow(0)
                    slider.setHigh(size_value - 1)
                    slider.setEnabled(True)
                else:
                    slider.setEnabled(False)
                    slider.setVisible(False)
