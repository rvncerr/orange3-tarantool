from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool

class IndexWidget(OWWidget):
    name = "Index"
    category = "Tarantool"
    description = "Index of Tarantool space."
    icon = "icons/index.svg"
    want_main_area = False
    priority = 12

    _space = None
    _indexes = []
    _index_id = 0

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        space = Input('Space', tarantool.space.Space)

    class Outputs:
        index = Output('Index', int)

    def __init__(self):
        super().__init__()
        self.index_listbox = gui.listBox(self.controlArea, self)
        select_button = gui.button(self.controlArea, self, 'Select', callback=self._select_index, autoDefault=False)

    def _draw_indexes(self):
        self.index_listbox.clear()
        for index in self._indexes:
            item = QListWidgetItem()
            item.setText("{}".format(index))
            item.setIcon(QIcon('rvncerr/orange3/tarantool/widgets/icons/index.svg'))
            self.index_listbox.addItem(item)

    def _select_index(self):
        i = self.index_listbox.currentRow()
        self._index_id = self._indexes[i][1]
        if self._index_id != 0 and len(self._indexes) != 0:
            self.Outputs.index.send(self._index_id)
        else:
            self.Outputs.index.send(None)

    @Inputs.space
    def signal_space(self, space):
        self._space = space
        if space is not None:
            self._indexes = self._space.connection.schema.fetch_index_from(self._space.space_no, None).data
        else:
            self._indexes = []
        self._draw_indexes()
        if self._index_id != 0 and len(self._indexes) != 0:
            self.Outputs.index.send(self._index_id)
        else:
            self.Outputs.index.send(None)
