import requests,json,re
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
# Configuración de la API de Zoom
load_dotenv()
TOKEN = os.getenv("TOKEN_JWT")
# URL de la API de Zoom para obtener las grabaciones
GET_RECORDINGS_URL = "https://api.zoom.us/v2/users/me/recordings"

# Parámetros de la solicitud de la API
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def downloader():
    #defino la fecha 2020-12-1 porque en mi caso en este mes y año tengo la primer grabación mas antigua.
    datefrom = datetime(2020, 12, 1).date()
    dateto = datefrom + timedelta(days=30)

    while(datefrom < datetime.now().date()):

        params = {
            "from": datefrom,
            "to": dateto,
            "page_size": 300,  # Tamaño máximo de página para obtener todas las grabaciones
            "page_number": 1
        }
        print(headers.get("Authorization"))
        # Hacer la solicitud para obtener las grabaciones
        response = requests.get(GET_RECORDINGS_URL, headers=headers, params=params)
        response_data = response.json()
        print(response.json())
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200 and response_data.get("meetings"):
            # Iterar sobre todas las grabaciones y descargarlas
            for meeting in response_data["meetings"]:
                meeting_id = meeting["uuid"]
                recording_files = meeting["recording_files"]
                topic = re.sub(r"[^\w\s]", "_", meeting["topic"].replace("/","_"))

                for file in recording_files:
                    if(file["recording_type"] == "shared_screen_with_speaker_view"):
                        download_url = file["download_url"]+"?access_token="+TOKEN
                        file_name = file["recording_start"].replace(":", "-") + " - " + topic +".mp4"
                        # Descargar el archivo de grabación
                        print(file["download_url"])
                        response = requests.get(download_url, stream=True)
                        if response.status_code == 200:
                             with open(file_name, "wb") as f:
                                 for chunk in response.iter_content(chunk_size=1024):
                                     f.write(chunk)
                             print(f"Descargado: {file_name}")
                        else:
                             print(f"Error al descargar el archivo {file_name}")
        else:
            print("Error al obtener las grabaciones")
        datefrom = dateto + timedelta(days=1)
        dateto = dateto + timedelta(days=30)
