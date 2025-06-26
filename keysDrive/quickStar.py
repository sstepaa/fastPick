from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

def login(clientKeys, credentialsPerson):
    gauth = GoogleAuth()
    
    #1- Cargar configuración de Oauth
    gauth.LoadClientConfigFile(clientKeys)
    
    #2- Intenta cargar credenciales guardadas (Si existen)
    if os.path.exists(credentialsPerson):
        gauth.LoadCredentialsFile(credentialsPerson)
        
    #3- Si no hay credenciales o están expiradas, autenticar nuevamente
    if gauth.credentials is None or gauth.access_token_expired:
        gauth.LocalWebserverAuth()  # Abre navegador para autenticación
        gauth.SaveCredentialsFile(credentialsPerson)
    else:
        gauth.Authorize()
        
    return GoogleDrive(gauth)
