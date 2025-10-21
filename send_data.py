from apscheduler.schedulers.background import BackgroundScheduler
from db import Detection
import httpx
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

ID_CAMARA = os.getenv("ID_CAMARA", "m01")

endpoints = [
    {"id": "1", "url": "https://appmapy.facitec.edu.py/api/"},
    {"id": "2", "url": "http://192.168.1.245:3300/api/"},
]

def send():
    now = datetime.now()
    nowStr = now.strftime('%Y-%m-%d %H:%M:%S')
    nowParsed = datetime.strptime(f"{nowStr}:000000", '%Y-%m-%d %H:%M:%S:%f')

    for endpoint in endpoints:
        eid = endpoint["id"]
        url = endpoint["url"]

        try:
            # Obtener la última transacción de este endpoints
            response = httpx.post(f'{url}detections/getLastTransaction', timeout=10.0)
            if response.status_code != httpx.codes.OK:
                print(f"Fallo al obtener última transacción de {url}")
                first(endpoint)
                continue

            print(f"Última transacción desde {url}: {response.json()['fecha']}")
            lastTransaction = datetime.strptime(f"{response.json()['fecha']}:000000", '%Y-%m-%d %H:%M:%S:%f')

            # Seleccionar los registros en el rango de tiempo, que no fueron enviados a este endpoint
            query = Detection.select().where(
                #(Detection.fecha >= (lastTransaction - timedelta(minutes=1))) &
                (Detection.fecha < nowParsed) &
                ~(Detection.enviado_a.contains(eid))
            ).order_by(Detection.fecha).limit(3000)

            if not query.exists():
                continue

            data = {
                "detections": [{
                    "id_zona": det.zona,
                    "clase": det.clase.lower(),
                    "fecha": det.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                    "id_camara": ID_CAMARA,
                } for det in query]
            }

            response = httpx.post(f'{url}detections/add', json=data, timeout=10.0)
            print(f"Respuesta de {url}: {response.status_code}")

            if response.status_code == httpx.codes.OK:
                for det in query:
                    ya_enviados = det.enviado_a.split(",") if det.enviado_a else []
                    if eid not in ya_enviados:
                        ya_enviados.append(eid)
                        det.enviado_a = ",".join(ya_enviados)
                    det.save()
            else:
                print(f"Error al enviar a {url}: {response.status_code}")

        except Exception as e:
            print(f"Error en el procesamiento del endpoint {url}: {e}")

    cleanup_old_detections()
    
    
def first(endpoint):
    url = endpoint["url"]
    eid = endpoint["id"]
    nowStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.strptime(f"{nowStr}:000000", '%Y-%m-%d %H:%M:%S:%f')
    query = Detection.select().where(
        Detection.fecha < now
    ).order_by(Detection.fecha).limit(3000)
    data = {
        "detections": [{
            "id_zona": det.zona,
            "clase": det.clase.lower(),
            "fecha": det.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            "id_camara": ID_CAMARA,
        } for det in query]
    }
    response = httpx.post(f'{url}detections/add', json=data, timeout=10.0)
    print(f"first() response from {url}: {response.status_code}, {response.json() if response.status_code == 200 else ''}")
    if response.status_code == httpx.codes.OK:
        for det in query:
            ya_enviados = det.enviado_a.split(",") if det.enviado_a else []
            if eid not in ya_enviados:
                ya_enviados.append(eid)
                det.enviado_a = ",".join(ya_enviados)
            det.save()

def cleanup_old_detections():
    limite = datetime.now() - timedelta(days=30)
    delete_query = Detection.delete().where(Detection.fecha < limite)

    # Agregar un filtro .contains() por cada endpoint directamente en el WHERE del DELETE
    for ep in endpoints:
        delete_query = delete_query.where(Detection.enviado_a.contains(ep["id"]))
    
    print(delete_query.sql())
    deleted_count = delete_query.execute()
    print(f"Se eliminaron {deleted_count} registros enviados con más de 30 días.")
    

def start(min):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send, 'interval', minutes=min)
    scheduler.start()