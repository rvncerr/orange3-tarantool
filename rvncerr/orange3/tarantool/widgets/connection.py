from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import widget, gui

import numpy as np
import tarantool


class ConnectionWidget(OWWidget):
    name = "Connection"
    category = "Tarantool"
    description = "Connection to Tarantool database."
    icon = "icons/connection.svg"
    want_main_area = False
    priority = 0

    host = Setting('localhost')
    port = Setting(3301)
    user = Setting('')
    passwd = Setting('')

    database = None

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Outputs:
        connection = Output('Connection', tarantool.Connection)

    def __init__(self):
        super().__init__()

        address_edit = gui.lineEdit(self.controlArea, self, 'host', 'Host')
        port_spin = gui.spin(self.controlArea, self, 'port', 0, 65535, label='Port')
        user_edit = gui.lineEdit(self.controlArea, self, 'user', 'User')
        passwd_edit = gui.lineEdit(self.controlArea, self, 'passwd', 'Password')
        self.connect_button = gui.button(self.controlArea, self, "Connect", callback=self.connect, autoDefault=False)
        self.disconnect_button = gui.button(self.controlArea, self, "Disconnect", callback=self.disconnect, autoDefault=False, enabled=False)

    def connect(self):
        try:
            if self.user == '':
                self.database = tarantool.connect(self.host, self.port)
            else:
                self.database = tarantool.connect(self.host, self.port, user=self.user, password=self.passwd)
            self.Outputs.connection.send(self.database)
            self.disconnect_button.setEnabled(True)
            self.connect_button.setEnabled(False)
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Error.error(e)

    def disconnect(self):
        self.database.close()
        self.Outputs.connection.send(None)
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
