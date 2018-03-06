from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool


class PartialSelectWidget(OWWidget):
    name = "Partial Select"
    category = "Tarantool"
    description = "Select from Tarantool space."
    icon = "icons/partial.svg"
    want_main_area = False
    priority = 2

    index = Setting(0)
    filterexpr = Setting(0)
    limit = Setting(0)

    _connection = None
    _space = None
    raw_tuples = []

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        space = Input('Space', tarantool.space.Space)

    class Outputs:
        #data = Output('Data', Table)
        tuples = Output('Response', tarantool.response.Response)

    def __init__(self):
        super().__init__()

        index_spin = gui.spin(self.controlArea, self, 'index', 0, 127, label='Index')
        filter_edit = gui.lineEdit(self.controlArea, self, 'filterexpr', 'Filter')
        limit_spin = gui.spin(self.controlArea, self, 'limit', 0, 1e6, label='Limit')
        select_button = gui.button(self.controlArea, self, "Select", callback=self.run_select, autoDefault=False)

    def _run_select_if_possible(self):
        pass

    @Inputs.space
    def signal_space(self, space):
        self._space = space
        if space is not None:
            self._schema = space.connection.schema.get_space(space.space_no).format
        else:
            self._schema = dict()

    def run_select(self):
        try:
            if self.filterexpr == '':
                self.raw_tuples = self._space.select(index=self.index)
            else:
                self.raw_tuples = self._space.select(int(self.filterexpr), index=self.index)
            if len(self.raw_tuples) != 0:
                self.Outputs.tuples.send(self.raw_tuples)
            else:
                self.Outputs.tuples.send(None)
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Outputs.tuples.send(None)
            self.Error.error(e)