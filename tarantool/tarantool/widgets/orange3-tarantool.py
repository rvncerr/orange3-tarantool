from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool


class TarantoolWidget(OWWidget):
    name = "Tarantool"
    category = "Tarantool"
    icon = "icons/tarantool.svg"
    want_main_area = False

    host = Setting('localhost')
    port = Setting(3301)
    space = Setting('')
    index = Setting(0)
    select = Setting('')
    raw_tuples = []

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Outputs:
        data = Output('Data', Table)

    def __init__(self):
        super().__init__()

        connection_box = gui.widgetBox(self.controlArea, 'Connection')
        address_edit = gui.lineEdit(connection_box, self, 'host', 'Host')
        port_spin = gui.spin(connection_box, self, 'port', 0, 65535, label='Port')

        data_box = gui.widgetBox(self.controlArea, 'Data')
        space_edit = gui.lineEdit(data_box, self, 'space', 'Space')
        index_spin = gui.spin(data_box, self, 'index', 0, 32, label='Index')
        filter_edit = gui.lineEdit(data_box, self, 'select', 'Filter')

        load_button = gui.button(self.controlArea, self, "Load", callback=self.load_data, autoDefault=False)

        self.domain_editor = QTableWidget(0, 6, self)
        self.domain_editor.setHorizontalHeaderLabels(['Name', 'Type', 'Miss', 'Min', 'Max', 'Mean'])
        self.controlArea.layout().addWidget(self.domain_editor)

        apply_button = gui.button(self.controlArea, self, "Apply", callback=self.apply_data, autoDefault=False)

    def load_data(self):
        try:
            database = tarantool.connect(self.host, self.port)
            space = database.space(self.space)
            if self.select == '':
                self.raw_tuples = space.select(index=self.index)
            else:
                self.raw_tuples = space.select(int(self.select), index=self.index)
            self.tuples = np.array(self.raw_tuples)
            self.tuples_miss = np.sum(np.isnan(self.tuples), axis=0)/self.tuples.shape[0]*100
            self.tuples_min = np.nanmin(self.tuples, axis=0)
            self.tuples_max = np.nanmax(self.tuples, axis=0)
            self.tuples_mean = np.nanmean(self.tuples, axis=0)

            flags = Qt.ItemFlags()
            flags != Qt.ItemIsEnabled

            self.domain_editor.setRowCount(0)

            for i in range(self.tuples.shape[1]):
                self.domain_editor.insertRow(i)
                item = QTableWidgetItem('Feature %d' % (i + 1))
                self.domain_editor.setItem(i, 0, item)
                item = QTableWidgetItem('Numeric')
                item.setFlags(flags)
                self.domain_editor.setItem(i, 1, item)
                item = QTableWidgetItem("%d%%" % self.tuples_miss[i])
                if self.tuples_miss[i] < 1.0 and self.tuples_miss[i] > 0.0:
                    item = QTableWidgetItem("< 1%")
                item.setFlags(flags)
                self.domain_editor.setItem(i, 2, item)
                item = QTableWidgetItem("%.2e" % self.tuples_min[i])
                item.setFlags(flags)
                self.domain_editor.setItem(i, 3, item)
                item = QTableWidgetItem("%.2e" % self.tuples_max[i])
                item.setFlags(flags)
                self.domain_editor.setItem(i, 4, item)
                item = QTableWidgetItem("%.2e" % self.tuples_mean[i])
                item.setFlags(flags)
                self.domain_editor.setItem(i, 5, item)

            self.domain_editor.resizeColumnsToContents()
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Error.error(e)

    def apply_data(self):
        self.domain = Domain([ContinuousVariable(self.domain_editor.item(i, 0).data(Qt.DisplayRole)) for i in range(self.tuples.shape[1])])
        self.table = Table.from_numpy(self.domain, self.tuples)
        self.Outputs.data.send(self.table)
