from Orange.data import Domain, Table, ContinuousVariable, StringVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool

def o3t_list_depth(l):
    if type(l) != list:
        return 0
    if len(l) == 0:
        return 1
    depth = 0
    for sl in l:
        sl_depth = o3t_list_depth(sl)
        if sl_depth > depth:
            depth = sl_depth
    return 1 + depth

class CorrelationWidget(OWWidget):
    name = "Correlation"
    category = "Tarantool"
    description = "Select from Tarantool space."
    icon = "icons/correlation.svg"
    want_main_area = False
    priority = 100

    part = Setting(10)

    _connection = None
    _space = None
    raw_tuples = []

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        space = Input('Space', tarantool.space.Space)

    class Outputs:
        data = Output('Data', Table)

    def __init__(self):
        super().__init__()

        # filter_edit = gui.lineEdit(self.controlArea, self, 'filterexpr', 'Filter')
        select_button = gui.button(self.controlArea, self, 'Calculate', callback=self.run_select, autoDefault=False)

    def _run_select_if_possible(self):
        if self._space is not None:
            self.run_select()
        else:
            self.Outputs.data.send(None)

    @Inputs.space
    def signal_space(self, space):
        self._space = space
        self._run_select_if_possible()

    def run_select(self):
        try:
            _raw_tuples = self._space.connection.call("orange_correlation", (self._space.space_no)).data
            while o3t_list_depth(_raw_tuples) > 2:
                _raw_tuples = _raw_tuples[0]
            while o3t_list_depth(_raw_tuples) < 2:
                _raw_tuples = [_raw_tuples]
            _schema = self._space.connection.schema.get_space(self._space.space_no).format
            _raw_domain = []
            i = 0
            while True:
                if i in _schema.keys():
                    _raw_domain.append(ContinuousVariable(_schema[i]['name']))
                else:
                    break
                i = i + 1
            i = 0
            for _raw_tuple in _raw_tuples:
                _raw_tuple.append(_schema[i]['name'])
                i = i + 1
            print(_raw_tuples)
            _raw_domain_metas = [StringVariable('field_name')]
            table = Table(Domain(_raw_domain, metas=_raw_domain_metas), _raw_tuples)
            self.Outputs.data.send(table)
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Outputs.data.send(None)
            self.Error.error(e)
