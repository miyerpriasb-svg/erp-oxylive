from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

# Definimos los permisos necesarios
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'

# REEMPLAZA EL TEXTO ENTRE COMILLAS CON TU ID REAL
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1lIaw-VtcBsCVpKF-k900h4Jdkel0O_2P2WJc2usWJEY")

def obtener_servicio_sheets():
    if not os.path.exists(CREDENTIALS_FILE):
        print("Error: No se encontró el archivo credentials.json")
        return None
    
    credenciales = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credenciales)

def registrar_avance_en_sheets(fecha, proceso, trabajador, avance, cliente):
    """Agrega una fila nueva al final de la pestaña Bitácora"""
    servicio = obtener_servicio_sheets()
    if not servicio: return

    # Los datos que se insertarán como una fila nueva
    valores = [[fecha, proceso, trabajador, f"{avance}%", cliente]]
    cuerpo = {'values': valores}
    
    # 'Bitacora!A:E' le dice a Google que busque esa pestaña y agregue los datos de la columna A a la E
    servicio.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Bitacora!A:E',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=cuerpo
    ).execute()