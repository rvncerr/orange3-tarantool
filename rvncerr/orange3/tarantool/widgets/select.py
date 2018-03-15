from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool


class SelectWidget(OWWidget):
    name = "Select"
    category = "Tarantool"
    description = "Select from Tarantool space."
    icon = "icons/select.svg"
    want_main_area = False
    priority = 1000

    filterexpr = Setting(0)
    limit = Setting(0)

    _connection = None
    _space = None
    _index = 0
    raw_tuples = []

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        space = Input('Space', tarantool.space.Space)
        index = Input('Index', int)
        trigger = Input('Trigger', bool)

    class Outputs:
        tuples = Output('Response', tarantool.response.Response)

    def __init__(self):
        super().__init__()

        filter_edit = gui.lineEdit(self.controlArea, self, 'filterexpr', 'Filter')
        limit_spin = gui.spin(self.controlArea, self, 'limit', 0, 1e6, label='Limit')
        select_button = gui.button(self.controlArea, self, 'Select', callback=self.run_select, autoDefault=False)

    def _run_select_if_possible(self):
        if self._space is not None:
            self.run_select()
        else:
            self.Outputs.tuples.send(None)

    @Inputs.trigger
    def signal_trigger(self, trigger):
        if trigger is not None:
            self._run_select_if_possible()

    @Inputs.space
    def signal_space(self, space):
        self._space = space
        self._run_select_if_possible()

    @Inputs.index
    def signal_index(self, index):
        if index is None:
            self._index = 0
        else:
            self._index = index
        self._run_select_if_possible()

    def run_select(self):
        try:
            if self.filterexpr == '':
                self.raw_tuples = self._space.select(index=self._index)
            else:
                self.raw_tuples = self._space.select(int(self.filterexpr), index=self._index)
            if len(self.raw_tuples) != 0:
                self.Outputs.tuples.send(self.raw_tuples)
            else:
                self.Outputs.tuples.send(None)
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Outputs.tuples.send(None)
            self.Error.error(e)
