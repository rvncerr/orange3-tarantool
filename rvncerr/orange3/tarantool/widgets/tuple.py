from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool
from pathlib import Path

def depth(l):
    if type(l) != list:
        return 0
    if len(l) == 0:
        return 1
    s = 0
    for ll in l:
        dll = depth(ll)
        if dll > s:
            s = dll
    return 1 + s

class TupleWidget(OWWidget):
    name = "Tuple Set"
    category = "Tarantool"
    description = "Set of tuples."
    icon = "icons/tuple.svg"
    want_main_area = False
    priority = 13

    _domain = Domain([])
    _data = []

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Warning(OWWidget.Warning):
        warning = widget.Msg("{}")

    class Inputs:
        domain = Input('Domain', Domain)
        response = Input('Response', tarantool.response.Response)

    class Outputs:
        data = Output('Data', Table)

    def __init__(self):
        super().__init__()

        self.tuple_listbox = gui.listBox(self.controlArea, self)

    def _clean_table(self):
        while depth(self._data) > 2:
            self._data = self._data[0]
        while depth(self._data) < 2:
            self._data = [self._data]

    def _build_table(self):
        self.Warning.warning("")
        self.tuple_listbox.clear()
        self._clean_table()

        if len(self._data) > 0:
            dataCount = 0
            for dataTuple in self._data:
                if dataCount < 100:
                    item = QListWidgetItem()
                    item.setText("{}".format(dataTuple))
                    item.setIcon(QIcon(str(Path(__file__).parents[0]) + '/icons/tuple.svg'))
                    self.tuple_listbox.addItem(item)
                else:
                    item = QListWidgetItem()
                    item.setText('(--- 100 tuples ---)')
                    item.setIcon(QIcon(str(Path(__file__).parents[0]) + '/icons/tuple.svg'))
                    self.tuple_listbox.addItem(item)
                    break
                dataCount = dataCount + 1

            minTuple = len(self._data[0])
            for oneTuple in self._data:
                if len(oneTuple) < minTuple:
                    minTuple = len(oneTuple)

            _cleanData = []
            for oneTuple in self._data:
                _cleanData.append(oneTuple[0:minTuple])

            rawDomain = []
            i = 0
            if self._domain is not None:
                for variable in self._domain.variables:
                    if i < minTuple:
                        rawDomain.append(variable)
                        i = i + 1
                    else:
                        break
            if i < minTuple:
                self.Warning.warning("Schema is not full.")
            while i < minTuple:
                rawDomain.append(ContinuousVariable("field_%d" % (i + 1)))
                i = i + 1

            table = Table(Domain(rawDomain), _cleanData)
            self.Outputs.data.send(table)
        else:
            self.Outputs.data.send(None)

    @Inputs.domain
    def signal_domain(self, domain):
        self._domain = domain
        self._build_table()

    @Inputs.response
    def signal_response(self, response):
        if response is not None:
            self._data = response.data
        else:
            self._data = []
        self._build_table()
