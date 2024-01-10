from apscheduler.schedulers.background import BackgroundScheduler
from db import Detection
import requests
from datetime import datetime, timedelta

urlBase = "#"

def send():
    query = Detection.select()
    response = requests.post(f'{urlBase}detections/getLastTransaction')
    if response.ok:
        lastTransaction = datetime.strptime(f"{response.json()['fecha']}:999999", '%Y-%m-%d %H:%M:%S:%f')
        nowStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(f"{nowStr}:000000", '%Y-%m-%d %H:%M:%S:%f')
        query = Detection.select().where(
            (Detection.fecha > lastTransaction) 
            & (Detection.fecha < now)
        )
        data = { 
            "detections": [{
                "id_zona": det.zona,
                "clase": det.clase.lower(),
                "fecha": det.fecha.strftime('%Y-%m-%d %H:%M:%S')
            } for det in query] 
        }
        response = requests.post(f'{urlBase}detections/add', json=data) 
    
def start(min):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send, 'interval', minutes=min)
    scheduler.start()
