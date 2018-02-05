from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import widget, gui

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

    class Error(OWWidget.Error):
        tarantool = widget.Msg("Tarantool: {}")

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

    def load_data(self):
        try:
            database = tarantool.connect(self.host, self.port)
            space = database.space(self.space)
            if self.select == '':
                raw_tuples = space.select(index=self.index)
            else:
                raw_tuples = space.select(int(self.select), index=self.index)
            tuples = np.array(raw_tuples)
            domain = Domain([ContinuousVariable('var[%d]' % i) for i in range(tuples.shape[1])])
            table = Table.from_numpy(domain, tuples)
            self.Outputs.data.send(table)
        except tarantool.NetworkError as e:
            self.Error.tarantool(e)
        except tarantool.DatabaseError as e:
            self.Error.tarantool(e)
