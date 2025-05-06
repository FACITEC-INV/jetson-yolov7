from apscheduler.schedulers.background import BackgroundScheduler
from db import Detection
import httpx
from datetime import datetime, timedelta

urlBase = "#"

def send():
    query = Detection.select()
    response = httpx.post(f'{urlBase}detections/getLastTransaction', timeout=10.0)
    if response.status_code == httpx.codes.OK:
        print(response.json()['fecha'])
        lastTransaction = datetime.strptime(f"{response.json()['fecha']}:000000", '%Y-%m-%d %H:%M:%S:%f')
        nowStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(f"{nowStr}:000000", '%Y-%m-%d %H:%M:%S:%f')
        query = Detection.select().where(
            (Detection.fecha >= (lastTransaction - timedelta(minutes=1))) 
            & (Detection.fecha < now)
            & (Detection.enviado == False)
        ).order_by(Detection.fecha).limit(3000)
        data = { 
            "detections": [{
                "id_zona": det.zona,
                "clase": det.clase.lower(),
                "fecha": det.fecha.strftime('%Y-%m-%d %H:%M:%S')
            } for det in query] 
        }
        response = httpx.post(f'{urlBase}detections/add', json=data, timeout=10.0) 
        print(response.json())
        if response.status_code == httpx.codes.OK:
            for det in query:
                det.enviado = True
                det.save()
            cleanup_old_detections()
    else:
        first()
    
    
def first():
    query = Detection.select()
    if True:
        nowStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(f"{nowStr}:000000", '%Y-%m-%d %H:%M:%S:%f')
        query = Detection.select().where(
            Detection.fecha < now
        ).order_by(Detection.fecha).limit(3000)
        data = { 
            "detections": [{
                "id_zona": det.zona,
                "clase": det.clase.lower(),
                "fecha": det.fecha.strftime('%Y-%m-%d %H:%M:%S')
            } for det in query] 
        }
        response = httpx.post(f'{urlBase}detections/add', json=data, timeout=10.0) 
        print(response.json())
        if response.status_code == httpx.codes.OK:
            for det in query:
                det.enviado = True
                det.save()

def cleanup_old_detections():
    limite = datetime.now() - timedelta(days=30)
    query = Detection.delete().where(
        (Detection.fecha < limite) & (Detection.enviado == True)
    )
    deleted_count = query.execute()
    print(f"Se eliminaron {deleted_count} registros enviados con más de 30 días.")
    

def start(min):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send, 'interval', minutes=min)
    scheduler.start()
