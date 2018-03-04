from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool


class TupleWidget(OWWidget):
    name = "Tuple Set"
    category = "Tarantool"
    description = "Set of tuples."
    icon = "icons/tuple.svg"
    want_main_area = False
    priority = 2

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

    def _build_table(self):
        self.Warning.warning("")
        if len(self._data) > 0:
            # print(self._data)

            minTuple = len(self._data[0])
            for oneTuple in self._data:
                if len(oneTuple) < minTuple:
                    minTuple = len(oneTuple)

            _cleanData = []
            for oneTuple in self._data:
                _cleanData.append(oneTuple[0:minTuple])

            rawDomain = []
            i = 0
            for variable in self._domain.variables:
                if i < minTuple:
                    rawDomain.append(variable)
                    i = i + 1
                else:
                    break
            if i < minTuple:
                self.Warning.warning("Schema is not full.")
            while i < minTuple:
                rawDomain.append(ContinuousVariable("field_%d" % i))
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
            if len(response.data) > 0:
                self._data = response.data[0]
            else:
                self._data = []
        else:
            self._data = []
        self._build_table()
