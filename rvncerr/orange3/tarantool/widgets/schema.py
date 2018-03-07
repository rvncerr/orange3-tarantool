from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool


class SchemaWidget(OWWidget):
    name = "Schema"
    category = "Tarantool"
    description = "Schema of Tarantool space."
    icon = "icons/schema.svg"
    want_main_area = False
    priority = 3

    _connection = None
    _space = None
    _schema = dict()
    _domain = Domain([])

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        space = Input('Space', tarantool.space.Space)

    class Outputs:
        domain = Output('Domain', Domain)

    def __init__(self):
        super().__init__()

    @Inputs.space
    def signal_space(self, space):
        self._space = space
        if space is not None:
            _raw_domain = []

            self._schema = self._space.connection.schema.get_space(self._space.space_no).format
            i = 0
            while True:
                if i in self._schema.keys():
                    _raw_domain.append(ContinuousVariable(self._schema[i]['name']))
                else:
                    break
                i = i + 1

            if len(_raw_domain) > 0:
                self._domain = Domain(_raw_domain)
                self.Outputs.domain.send(self._domain)
            else:
                self._domain = Domain([])
                self.Outputs.domain.send(None)
        else:
            self._schema = dict()
            self._domain = Domain([])
            self.Outputs.domain.send(None)
