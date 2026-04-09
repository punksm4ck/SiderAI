import sys
import os
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class AIWorker(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        # Bulletproof Key Retrieval
        key_path = os.path.expanduser("~/.groq_api_key")
        api_key = None

        if os.path.exists(key_path):
            with open(key_path, 'r') as f:
                api_key = f.read().strip()

        if not api_key:
            self.response_ready.emit("⚠️ ERROR: GROQ API Key not found in ~/.groq_api_key")
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": self.prompt}]
        }

        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            self.response_ready.emit(reply)
        except Exception as e:
            self.response_ready.emit(f"⚠️ API ERROR: {e}")

class SiderAI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSIRIS Sider AI Desktop")
        self.setFixedWidth(400)
        self.setMinimumHeight(700)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Sider AI...")
        self.input_field.returnPressed.connect(self.dispatch_message)

        self.btn_send = QPushButton("DISPATCH")
        self.btn_send.clicked.connect(self.dispatch_message)

        layout.addWidget(self.chat_area)
        layout.addWidget(self.input_field)
        layout.addWidget(self.btn_send)

    def apply_theme(self):
        self.setStyleSheet("""
             QMainWindow { background-color: #0b1120; border-left: 2px solid #3b82f6; }
             QWidget { background-color: #0b1120; color: #e2e8f0; font-family: 'Inter'; }
             QTextEdit { background-color: #0f172a; border: none; padding: 10px; font-size: 13px; }
             QLineEdit { background-color: #1e293b; border: 1px solid #3b82f6; padding: 8px; border-radius: 4px; }
             QPushButton { background-color: #3b82f6; color: #0b1120; font-weight: bold; border-radius: 4px; padding: 8px; }
             QPushButton:disabled { background-color: #1e3a5f; color: #475569; }
        """)

    def dispatch_message(self):
        text = self.input_field.text().strip()
        if not text: return

        self.chat_area.append(f"<b><font color='#3b82f6'>YOU:</font></b> {text}<br>")
        self.input_field.clear()

        self.btn_send.setEnabled(False)
        self.btn_send.setText("PROCESSING...")
        self.input_field.setEnabled(False)

        self.worker = AIWorker(text)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, reply):
        formatted_reply = reply.replace('\n', '<br>')
        self.chat_area.append(f"<b><font color='#10b981'>SIDER AI:</font></b> {formatted_reply}<br><br>")

        self.btn_send.setEnabled(True)
        self.btn_send.setText("DISPATCH")
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SiderAI()
    w.show()
    sys.exit(app.exec())
