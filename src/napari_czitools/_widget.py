"""
References:
- Widget specification: https://napari.org/stable/plugins/guides.html?#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/

Replace code below according to your needs.
"""

from typing import TYPE_CHECKING

from czitools.metadata_tools import czi_metadata as czimd
from czitools.metadata_tools.czi_metadata import CziMetadata
from czitools.utils import logging_tools
from magicgui.types import FileDialogMode
from magicgui.widgets import ComboBox, FileEdit, PushButton
from qtpy.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from ._metadata_widget import MdTableWidget, MdTreeWidget, MetadataDisplayMode
from ._range_widget import RangeSliderWidget
from ._reader import reader_function_adv

logger = logging_tools.set_logging()

if TYPE_CHECKING:
    import napari


class CziReaderWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        # store the viewer instance for later use
        self.viewer = viewer

        # create a layout
        self.main_layout = QVBoxLayout()

        # 1. FileDialog Section
        file_layout = QHBoxLayout()
        file_label = QLabel("Select a CZI Image File:")
        file_layout.addWidget(file_label)

        # define filter based on file extension
        model_extension = "*.czi"
        self.filename_edit = FileEdit(mode=FileDialogMode.EXISTING_FILE, value="", filter=model_extension)
        file_layout.addWidget(self.filename_edit.native)
        self.filename_edit.line_edit.changed.connect(self._file_changed)

        # 2. ComboBox Section
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

        # Pushbutton to load pixel data
        self.load_pixeldata = PushButton(
            name="Load Pixel Data",
            visible=True,
            enabled=False,
        )
        self.load_pixeldata.native.setStyleSheet("border: 1px solid blue;")
        self.load_pixeldata.native.clicked.connect(self._loadbutton_pressed)

        # Define Dimension slider configurations
        slider_configs = [
            ("Scene", "scene_slider"),
            ("Time", "time_slider"),
            ("Channel", "channel_slider"),
            ("Z-Plane", "z_slider"),
        ]

        # Create sliders dynamically
        for label, attr_name in slider_configs:
            slider = RangeSliderWidget(
                dimension_label=label, min_value=0, max_value=0, readout=True, visible=True, enabled=False
            )
            setattr(self, attr_name, slider)

        # Add all widgets to the main layout
        self.main_layout.addLayout(file_layout)  # Add FileDialog section
        self.main_layout.addLayout(mdcombo_layout)  # Add ComboBox

        self.mdtable = MdTableWidget()
        self.mdtable.setStyleSheet("border: 1px solid red;")
        self.mdtable.setMinimumHeight(300)  # Set minimum height for the table
        self.mdtable.update_metadata({})
        self.mdtable.update_style(font_bold=False, font_size=6)

        self.mdtree = MdTreeWidget()
        self.mdtree.setStyleSheet("border: 1px solid red;")
        self.mdtree.setMinimumHeight(300)  # Set minimum height for the table

        self.current_md_widget = self.mdtable
        self.main_layout.addWidget(self.mdtable)  # Add the native Qt widget of the table

        self.spacer_item = QSpacerItem(100, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(self.spacer_item)

        self.main_layout.addWidget(self.load_pixeldata.native)
        self.main_layout.addWidget(self.scene_slider.native)
        self.main_layout.addWidget(self.time_slider.native)
        self.main_layout.addWidget(self.channel_slider.native)

        self.main_layout.addWidget(self.z_slider.native)
        # self.main_layout.addLayout(z_slider_layout)  # Add the slider layout to the main layout

        self.setLayout(self.main_layout)

    def _file_changed(self):
        """Callback for when the file edit changes."""
        filepath = self.filename_edit.value
        logger.info("File changed to: %(filepath)s", extra={"filepath": filepath})
        # Here you can add logic to handle the file change, e.g., load data

        # diable the load pixel button
        #self.load_pixeldata.enabled = False

        # read the metadata from the file
        self.metadata = CziMetadata(filepath)

        # create a nested dictionary for the tree and a reduced dictionary for the table
        md_dict_tree = czimd.create_md_dict_nested(self.metadata, sort=True, remove_none=True)
        # drop certain entries
        md_dict_tree.pop("bbox", None)
        self.mdtree.setData(md_dict_tree, expandlevel=0, hideRoot=True)

        md_dict_table = czimd.create_md_dict_red(self.metadata, sort=True, remove_none=True)
        self.mdtable.update_metadata(md_dict_table)

        # Update sliders based on metadata
        slider_mapping = {
            "SizeS": self.scene_slider,
            "SizeT": self.time_slider,
            "SizeC": self.channel_slider,
            "SizeZ": self.z_slider,
        }

        for size_attr, slider in slider_mapping.items():
            size_value = getattr(self.metadata.image, size_attr, None)
            logger.info(f"Size attribute {size_attr} has value: {size_value}")
            if size_value is not None:
                slider.enabled = True
                slider.min_slider.enabled = True
                slider.max_slider.enabled = True
                slider.min_slider.min = 0
                slider.max_slider.max = size_value - 1
                slider.min_slider.value = 0
                slider.max_slider.value = size_value - 1
            else:
                # Reset slider if size_value is None
                slider.enabled = False
                slider.min_slider.enabled = False
                slider.max_slider.enabled = False
                slider.min_slider.min = 0
                slider.max_slider.max = 0
                slider.min_slider.value = 0
                slider.max_slider.value = 0


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
        else:
            self.current_md_widget = self.mdtable

        # Add the new widget to the layout
        self.main_layout.insertWidget(2, self.current_md_widget)
        self.current_md_widget.show()

    def _loadbutton_pressed(self):

        # get the require values to read the pixel data and show the layers
        planes = {
            "S": (self.scene_slider.min_slider.value, self.scene_slider.max_slider.value),
            "T": (self.time_slider.min_slider.value, self.time_slider.max_slider.value),
            "C": (self.channel_slider.min_slider.value, self.channel_slider.max_slider.value),
            "Z": (self.z_slider.min_slider.value, self.z_slider.max_slider.value),
        }

        logger.info(
            "Read Pixel data for file: %(filepath)s - Planes: %(planes)s",
            extra={"filepath": self.filename_edit.value, "planes": planes},
        )
        reader_function_adv(self.filename_edit.value, zoom=1.0, planes=planes, show_metadata=MetadataDisplayMode.NONE)
