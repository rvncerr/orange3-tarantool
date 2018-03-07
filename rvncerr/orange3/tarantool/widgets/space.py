from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool


class SpaceWidget(OWWidget):
    name = "Space"
    category = "Tarantool"
    description = "Space in Tarantool database."
    icon = "icons/space.svg"
    want_main_area = False
    priority = 10

    _space = None
    _connection = None
    _space_list = None

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        connection = Input('Connection', tarantool.Connection)

    class Outputs:
        space = Output('Space', tarantool.space.Space)

    def __init__(self):
        super().__init__()

        refresh_button = gui.button(self.controlArea, self, 'Refresh', callback=self.update_list, autoDefault=False)
        self.space_listbox = gui.listBox(self.controlArea, self)
        connect_button = gui.button(self.controlArea, self, 'Load', callback=self.get_space, autoDefault=False)

    def update_list(self):
        if self._connection is not None:
            self._space_list = self._connection.schema.fetch_space_from(None).data
            self.space_listbox.clear()
            for space in self._space_list:
                if space[2][0] != '_':
                    item = QListWidgetItem()
                    item.setText(space[2])
                    item.setIcon(QIcon('rvncerr/orange3/tarantool/widgets/icons/space.svg'))
                    self.space_listbox.addItem(item)

    def update_output(self):
        if self._connection is not None:
            if self._space is not None:
                space = self._connection.space(self._space)
                self.Outputs.space.send(space)
            else:
                self.Outputs.space.send(None)
        else:
            self.Outputs.space.send(None)

    @Inputs.connection
    def signal_connection(self, connection):
        try:
            self._connection = connection
            self.update_list()
            self.update_output()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Error.error(e)

    def get_space(self):
        try:
            self._space = self.space_listbox.currentItem().text()
            self.update_output()
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Error.error(e)
