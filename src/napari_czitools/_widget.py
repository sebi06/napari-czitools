"""
References:
- Widget specification: https://napari.org/stable/plugins/guides.html?#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/

Replace code below according to your needs.
"""

from typing import TYPE_CHECKING, Iterable, Literal

from czitools.metadata_tools import czi_metadata as czimd
from czitools.metadata_tools.czi_metadata import CziMetadata
from magicgui.types import FileDialogMode
from magicgui.widgets import ComboBox, Container, FileEdit, Label, PushButton, RangeSlider, Table
from qtpy.QtWidgets import QHBoxLayout, QLabel, QPushButton, QRangeSlider, QVBoxLayout, QWidget

from ._metadata_widget import MdTableWidget, MdTreeWidget

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
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
        mdcombo_layout.addWidget(mdcombo_label)
        mdcombo_layout.addWidget(self.mdata_widget.native)

        # Pushbutton to load pixel data
        self.load_pixeldata = PushButton(
            name="Load Pixel Data",
            visible=True,
            enabled=False,
        )

        # scene slider
        self.scene_slider = RangeSlider(
            value=(0, 0), min=0, max=0, step=1, label="Scene", readout=True, visible=True, enabled=False
        )

        # time slider
        self.time_slider = RangeSlider(
            value=(0, 0), min=0, max=0, step=1, label="Time", readout=True, visible=True, enabled=False
        )

        # channel slider
        self.channel_slider = RangeSlider(
            value=(0, 0), min=0, max=0, step=1, label="Channel", readout=True, visible=True, enabled=False
        )

        # z slider
        self.z_slider = RangeSlider(
            value=(0, 0), min=0, max=0, step=1, label="Z-Plane", readout=True, visible=True, enabled=False
        )
        # self.z_slider = QRangeSlider()
        # self.z_slider.setMinimum(0)
        # self.z_slider.setMaximum(0)
        # self.z_slider.setValue((0, 0))
        # self.z_slider.setSingleStep(1)
        # self.z_slider.enabled = False
        # self.z_slider.visible = True
        # z_slider_layout = QHBoxLayout()  # Create a layout for the slider and its label
        # z_slider_label = QLabel("Z-Plane:")  # Create a QLabel for the slider
        # z_slider_layout.addWidget(z_slider_label)  # Add the label to the layout

        # self.z_slider = RangeSlider(value=(0, 1), min=0, max=1, step=1, readout=True, visible=True, enabled=False)
        # z_slider_layout.addWidget(self.z_slider.native)  # Add the slider to the layout

        # Add all widgets to the main layout
        self.main_layout.addLayout(file_layout)  # Add FileDialog section
        self.main_layout.addLayout(mdcombo_layout)  # Add ComboBox
        self.placeholder = QWidget()
        self.main_layout.addWidget(self.placeholder)  # Add QWidget as a placeholder
        self.main_layout.addWidget(self.load_pixeldata.native)
        self.main_layout.addWidget(self.scene_slider.native)
        self.main_layout.addWidget(self.time_slider.native)
        self.main_layout.addWidget(self.channel_slider.native)

        self.main_layout.addWidget(self.z_slider.native)
        # self.main_layout.addLayout(z_slider_layout)  # Add the slider layout to the main layout

        self.setLayout(self.main_layout)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

    def _file_changed(self):
        """Callback for when the file edit changes."""
        filepath = self.filename_edit.value
        print(f"File changed to: {filepath}")
        # Here you can add logic to handle the file change, e.g., load data

        # read the metadata from the file
        self.metadata = CziMetadata(filepath)

        print(f"SizeS: {self.metadata.image.SizeS}")
        print(f"SizeT: {self.metadata.image.SizeT}")
        print(f"SizeC: {self.metadata.image.SizeC}")
        print(f"SizeZ: {self.metadata.image.SizeZ}")

        if self.mdata_widget.value == "Tree":
            md_dict = czimd.create_md_dict_nested(self.metadata, sort=True, remove_none=True)
            self.mdtree = MdTreeWidget(data=md_dict, expandlevel=0)
            self.viewer.window.add_dock_widget(self.mdtree, name="MetadataTree", area="right")

        if self.mdata_widget.value == "Table":

            self.main_layout.removeWidget(self.placeholder)
            self.placeholder.deleteLater()

            md_dict = czimd.create_md_dict_red(self.metadata, sort=True, remove_none=True)
            self.mdtable = MdTableWidget()
            self.mdtable.update_metadata(md_dict)
            self.mdtable.update_style()
            self.main_layout.insertWidget(2, self.mdtable)

        # update sliders based on metadata
        if self.metadata.image.SizeS is not None:
            self.scene_slider.enabled = True
            self.scene_slider.max = self.metadata.image.SizeS - 1
            self.scene_slider.value = (0, self.metadata.image.SizeS - 1)

        if self.metadata.image.SizeT is not None:
            self.time_slider.enabled = True
            self.time_slider.max = self.metadata.image.SizeT - 1
            self.time_slider.value = (0, self.metadata.image.SizeT - 1)

        if self.metadata.image.SizeC is not None:
            self.channel_slider.enabled = True
            self.channel_slider.max = self.metadata.image.SizeC - 1
            self.channel_slider.value = (0, self.metadata.image.SizeC - 1)

        if self.metadata.image.SizeZ is not None:
            self.z_slider.enabled = True
            self.z_slider.max = self.metadata.image.SizeZ - 1
            self.z_slider.value = (0, self.metadata.image.SizeZ - 1)


# @magic_factory
# def example_magic_widget(img_layer: "napari.layers.Image"):
#     print(f"you have selected {img_layer}")
