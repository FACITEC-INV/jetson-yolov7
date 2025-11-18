import os
import psutil
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuración
PROCESS_NAME = "mapycam_process"  # Tu proceso
CAM_DEVICE = "/dev/video0"       # Dispositivo de la cámara
HOST = "0.0.0.0"
PORT = 8000

# Función para verificar proceso
def is_process_running(name):
    for p in psutil.process_iter(['name', 'cmdline']):
        cmdline = p.info['cmdline']
        if p.info['name'] == name or (cmdline and name in " ".join(cmdline)):
            return True
    return False

# Función para verificar cámara
def is_camera_connected():
    return os.path.exists(CAM_DEVICE)

# Micro-API HTTP
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            status = {
                "process_running": is_process_running(PROCESS_NAME),
                "camera_connected": is_camera_connected()
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    # Desactivar logs en consola
    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    print(f"🚀 API ligera corriendo en http://{HOST}:{PORT}/status")
    server = HTTPServer((HOST, PORT), RequestHandler)
    server.serve_forever()
