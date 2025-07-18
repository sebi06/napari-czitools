"""
References:
- Widget specification: https://napari.org/stable/plugins/guides.html?#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/

Replace code below according to your needs.
"""

from typing import TYPE_CHECKING

from czitools.metadata_tools import czi_metadata as czimd
from czitools.metadata_tools.czi_metadata import CziMetadata
from magicgui.types import FileDialogMode
from magicgui.widgets import ComboBox, FileEdit, PushButton
from qtpy.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from ._metadata_widget import MdTableWidget, MdTreeWidget
from ._range_widget import RangeSliderWidget

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

        # # scene slider
        # self.scene_slider = RangeSliderWidget(
        #     dimension_label="Scene", min_value=0, max_value=0, readout=True, visible=True, enabled=False
        # )

        # # time slider
        # self.time_slider = RangeSliderWidget(
        #     dimension_label="Time", min_value=0, max_value=0, readout=True, visible=True, enabled=False
        # )

        # # channel slider
        # self.channel_slider = RangeSliderWidget(
        #     dimension_label="Channel", min_value=0, max_value=0, readout=True, visible=True, enabled=False
        # )

        # # z slider
        # self.z_slider = RangeSliderWidget(
        #     dimension_label="Z-Plane", min_value=0, max_value=0, readout=True, visible=True, enabled=False
        # )

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
        self.mdtable.update_metadata({})
        self.mdtable.update_style(font_bold=False, font_size=6)

        # self.mdtable.setStyleSheet("border: 1px solid red;")
        # self.mdtable.setMinimumHeight(300)  # Set minimum height for the table

        self.mdtree = MdTreeWidget()
        # self.mdtree.setStyleSheet("border: 1px solid red;")
        # self.mdtree.setMinimumHeight(300)  # Set minimum height for the table
        # self.mdtree.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.mdtable.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.mdtree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.mdtable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        print(f"File changed to: {filepath}")
        # Here you can add logic to handle the file change, e.g., load data

        # read the metadata from the file
        self.metadata = CziMetadata(filepath)

        md_dict = czimd.create_md_dict_nested(self.metadata, sort=True, remove_none=True)
        self.mdtree.setData(md_dict, expandlevel=0, hideRoot=True)

        self.mdtable.update_metadata(md_dict)
        # self.mdtable.update_style(font_bold=False, font_size=6)

        # update sliders based on metadata
        if self.metadata.image.SizeS is not None:
            self.scene_slider.enabled = True
            self.scene_slider.min_slider.enabled = True
            self.scene_slider.max_slider.enabled = True
            self.scene_slider.min_slider.min = 0
            self.scene_slider.max_slider.max = self.metadata.image.SizeS - 1
            self.scene_slider.min_slider.value = 0
            self.scene_slider.max_slider.value = self.metadata.image.SizeS - 1

        if self.metadata.image.SizeT is not None:
            self.time_slider.enabled = True
            self.time_slider.min_slider.enabled = True
            self.time_slider.max_slider.enabled = True
            self.time_slider.min_slider.min = 0
            self.time_slider.min_slider.max = self.metadata.image.SizeT - 1
            self.time_slider.max_slider.min = 0
            self.time_slider.max_slider.max = self.metadata.image.SizeT - 1
            self.time_slider.min_slider.value = 0
            self.time_slider.max_slider.value = self.metadata.image.SizeT - 1

        if self.metadata.image.SizeC is not None:
            self.channel_slider.enabled = True
            self.channel_slider.max_slider.enabled = True
            self.channel_slider.min_slider.enabled = True
            self.channel_slider.min_slider.min = 0
            self.channel_slider.max_slider.max = self.metadata.image.SizeC - 1
            self.channel_slider.min_slider.value = 0
            self.channel_slider.max_slider.value = self.metadata.image.SizeC - 1

        if self.metadata.image.SizeZ is not None:
            self.z_slider.enabled = True
            self.z_slider.max_slider.enabled = True
            self.z_slider.min_slider.enabled = True
            self.z_slider.min_slider.min = 0
            self.z_slider.max_slider.max = self.metadata.image.SizeZ - 1
            self.z_slider.min_slider.value = 0
            self.z_slider.max_slider.value = self.metadata.image.SizeZ - 1

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
