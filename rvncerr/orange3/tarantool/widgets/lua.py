from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool

LUA_KEYWORDS = ['do', 'end', 'for', 'while',
                'if', 'then', 'else', 'elseif',
                'repeat', 'until', 'function', 'local',
                'return', 'in', 'break', 'not',
                'nil', 'and', 'or', 'true']

def text_format(foreground=Qt.black, weight=QFont.Normal):
    fmt = QTextCharFormat()
    fmt.setForeground(QBrush(foreground))
    fmt.setFontWeight(weight)
    return fmt

class LuaSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        self.rules = []

        self.constantFormat = text_format(Qt.darkGreen)
        self.classFormat = text_format(Qt.darkMagenta)
        self.functionFormat = text_format(Qt.blue)
        self.keywordFormat = text_format(Qt.darkBlue, QFont.Bold)
        self.quotationFormat = text_format(Qt.darkGreen)
        self.singleLineCommentFormat = text_format(Qt.gray)
        self.singleLineCommentFormat.setFontItalic(True)

        self.rules.append((QRegExp("[-+]?(?:(?:\\d+\\.\\d+)|(?:\\.\\d+)|(?:\\d+\\.?))"), self.constantFormat))
        self.rules.append((QRegExp("\\b[A-Za-z][A-Za-z0-9_]*\\b"), self.classFormat))
        self.rules.append((QRegExp("\\b[A-Za-z0-9_]+ *(?=\\()"), self.functionFormat))
        for kwd in LUA_KEYWORDS:
            self.rules.append((QRegExp(r"\b%s\b" % kwd), self.keywordFormat))
        self.rules.append((QRegExp("\"[^\"]*\""), self.quotationFormat))
        self.rules.append((QRegExp("'[^']*'"), self.quotationFormat))
        self.rules.append((QRegExp("--[^\n]*"), self.singleLineCommentFormat))

        super().__init__(parent)

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            exp = QRegExp(pattern)
            index = exp.indexIn(text)
            while index >= 0:
                length = exp.matchedLength()
                if exp.captureCount() > 0:
                    self.setFormat(exp.pos(1), len(str(exp.cap(1))), format)
                else:
                    self.setFormat(exp.pos(0), len(str(exp.cap(0))), format)
                index = exp.indexIn(text, index + length)

class LuaEditor(QPlainTextEdit):
    INDENT = 4

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def lastLine(self):
        text = str(self.toPlainText())
        pos = self.textCursor().position()
        index = text.rfind("\n", 0, pos)
        text = text[index: pos].lstrip("\n")
        return text

    def keyPressEvent(self, event):
        #self.widget.enable_execute()
        if event.key() == Qt.Key_Return:
            if event.modifiers() & (
                    Qt.ShiftModifier | Qt.ControlModifier | Qt.MetaModifier):
                self.widget.unconditional_commit()
                return
            text = self.lastLine()
            indent = len(text) - len(text.lstrip())
            if text.strip() == "pass" or text.strip().startswith("return "):
                indent = max(0, indent - self.INDENT)
            elif text.strip().endswith(":"):
                indent += self.INDENT
            super().keyPressEvent(event)
            self.insertPlainText(" " * indent)
        elif event.key() == Qt.Key_Tab:
            self.insertPlainText(" " * self.INDENT)
        elif event.key() == Qt.Key_Backspace:
            text = self.lastLine()
            if text and not text.strip():
                cursor = self.textCursor()
                for _ in range(min(self.INDENT, len(text))):
                    cursor.deletePreviousChar()
            else:
                super().keyPressEvent(event)

        else:
            super().keyPressEvent(event)

class LuaWidget(OWWidget):
    name = "Lua"
    category = "Tarantool"
    description = "Execute Lua code in Tarantool database."
    icon = "icons/lua.svg"
    want_main_area = False
    priority = 1

    _connection = None

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Inputs:
        connection = Input('Connection', tarantool.Connection)

    class Outputs:
        data = Output('Data', Table)

    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)

        #self.controlArea = QWidget(self.controlArea)
        #self.layout().addWidget(self.controlArea)
        #layout = QGridLayout()
        #layout.setContentsMargins(4, 4, 4, 4)
        #self.controlArea.setLayout(layout)

        self.controlBox = gui.vBox(self, 'Info')
        layout.addWidget(self.controlBox, 0, 0, 0, 1)

        #self.splitCanvas = QSplitter(Qt.Vertical, self.controlArea)
        #self.controlArea.layout().addWidget(self.splitCanvas, 0, 2, 0, 2)

        self.text = LuaEditor(self.controlArea)
        layout.addWidget(self.text, 0, 2, 0, 4)
        self.text.setTabStopWidth(4)
        self.text.setFont(QFont('Courier New', 10))
        self.highlighter = LuaSyntaxHighlighter(self.text.document())

        self.runButton = gui.button(self.controlBox, self, 'Run', callback=self.run, autoDefault=False)

    def run(self):
        try:
            if self._connection is not None:
                result = self._connection.eval(self.text.toPlainText())
                self.tuples = np.array(result)
                if len(self.tuples.shape) == 2:
                    self.domain = Domain([ContinuousVariable('field_%d' % i) for i in range(self.tuples.shape[1])])
                    self.table = Table.from_numpy(self.domain, self.tuples)
                    self.Outputs.data.send(self.table)
                else:
                    self.Outputs.data.send(None)
            self.Error.error.clear()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Error.error(e)

    @Inputs.connection
    def signal_connection(self, connection):
        try:
            self._connection = connection
            self.run()
        except (tarantool.error.DatabaseError, tarantool.error.InterfaceError) as e:
            self.Error.error(e)
