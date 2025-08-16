from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import subprocess
import sys
import threading
import time
import json
from datetime import datetime
import zipfile
import shutil
import yt_dlp
import io

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_soundcloud_downloader_2024'

# Variables globales para el estado de descarga
download_status = {}
download_progress = {}
download_results = {} # Para almacenar la ruta de los archivos descargados

def zip_playlist_files(playlist_folder, zip_name):
    """Comprimir archivos de una carpeta en un ZIP y luego eliminar la carpeta."""
    try:
        zip_path = os.path.join('descargas', f"{zip_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(playlist_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, file) # Añadir solo el archivo, no la ruta completa
        
        # Eliminar la carpeta de la playlist después de comprimir
        shutil.rmtree(playlist_folder)
        
        return f"{zip_name}.zip"
    except Exception as e:
        print(f"Error al crear ZIP: {e}")
        return None

def descargar_contenido_async(url, tipo, download_id, zip_option=None):
    """Función para descargar en segundo plano usando yt-dlp."""
    downloaded_files = [] # Para almacenar rutas de archivos

    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                progress = int((d['downloaded_bytes'] / total_bytes) * 100)
                download_progress[download_id] = {
                    "status": f"Descargando: {progress}%",
                    "progress": progress
                }
        elif d['status'] == 'finished':
            # Cuando un archivo se completa, guardar su ruta
            filepath = d.get('info_dict', {}).get('filepath')
            if filepath:
                downloaded_files.append(filepath)
            download_progress[download_id] = {"status": "Procesando...", "progress": 100}

    try:
        download_status[download_id] = "downloading"
        download_progress[download_id] = {"status": "Iniciando descarga...", "progress": 0}
        download_results[download_id] = [] # Limpiar resultados previos

        # Limpiar URL
        url = url.strip().split('?')[0]

        # Opciones base para yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
            'outtmpl': {
                'default': os.path.join('descargas', '%(title)s.%(ext)s')
            },
            'progress_hooks': [progress_hook],
            'noplaylist': tipo != 'playlist',
            'quiet': True,
            'no_warnings': True,
        }

        playlist_folder = None
        # Opciones específicas para playlists
        if tipo == 'playlist':
            info = yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}).extract_info(url, download=False)
            playlist_title = info.get('title', f'playlist_{download_id}')
            safe_playlist_title = "".join([c for c in playlist_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()

            # Si se va a comprimir, descargar a una carpeta temporal
            if zip_option == 'zip':
                playlist_folder = os.path.join('descargas', safe_playlist_title)
                ydl_opts['outtmpl'] = {
                    'default': os.path.join(playlist_folder, '%(title)s.%(ext)s')
                }

        # Iniciar descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Comprimir si es una playlist y se seleccionó la opción ZIP
        if tipo == 'playlist' and zip_option == 'zip':
            download_progress[download_id] = {"status": "Comprimiendo...", "progress": 95}
            zip_filename = zip_playlist_files(playlist_folder, safe_playlist_title)
            if not zip_filename:
                raise Exception("Error al crear el archivo ZIP")
            # Guardar la ruta del ZIP
            download_results[download_id] = [os.path.join('descargas', zip_filename)]
        else:
            # Guardar las rutas de los archivos individuales
            download_results[download_id] = downloaded_files

        download_status[download_id] = "completed"
        download_progress[download_id] = {"status": "¡Descarga completada!", "progress": 100}

    except Exception as e:
        download_status[download_id] = "error"
        download_progress[download_id] = {"status": f"Error: {str(e)}", "progress": 0}
        if download_id in download_results:
            del download_results[download_id] # Limpiar en caso de error

@app.route('/')
def index():
    """Página principal"""
    # Ya no se verifican dependencias locales
    return render_template('index.html', scdl_installed=True, ffmpeg_installed=True)

@app.route('/download', methods=['POST'])
def download():
    """Iniciar descarga"""
    data = request.json
    url = data.get('url', '').strip()
    tipo = data.get('type', 'single')
    zip_option = data.get('zipOption', 'separate')

    if not url or 'soundcloud.com' not in url:
        return jsonify({'success': False, 'message': 'URL de SoundCloud inválida'})

    if 'discover/sets/artist-stations' in url:
        return jsonify({
            'success': False, 
            'message': 'Las Artist Stations no son compatibles. Usa playlists normales.'
        })

    download_id = str(int(time.time() * 1000))
    
    thread = threading.Thread(
        target=descargar_contenido_async,
        args=(url, tipo, download_id, zip_option)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'download_id': download_id})

@app.route('/status/<download_id>')
def get_status(download_id):
    """Obtener estado de descarga"""
    status = download_status.get(download_id, 'not_found')
    progress = download_progress.get(download_id, {"status": "No encontrado", "progress": 0})
    
    return jsonify({
        'status': status,
        'progress': progress
    })

@app.route('/downloads')
def list_downloads():
    """Listar archivos descargados"""
    downloads_dir = 'descargas'
    files = []
    
    if os.path.exists(downloads_dir):
        for filename in os.listdir(downloads_dir):
            if filename.endswith(('.mp3', '.flac', '.wav', '.m4a', '.zip')):
                filepath = os.path.join(downloads_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                    files.append({
                        'name': filename,
                        'size': f"{size / (1024*1024):.1f} MB",
                        'modified': modified.strftime("%d/%m/%Y %H:%M")
                    })
    
    # Ordenar por fecha de modificación (más reciente primero)
    files.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('downloads.html', files=files)

@app.route('/download_file/<path:filename>')
def download_file(filename):
    """Descargar archivo individual"""
    try:
        downloads_dir = 'descargas'
        filepath = os.path.join(downloads_dir, filename)
        if os.path.exists(filepath):
            # Detectar si es una solicitud desde el navegador web
            user_agent = request.headers.get('User-Agent', '')
            is_browser = any(browser in user_agent.lower() for browser in ['chrome', 'firefox', 'safari', 'edge', 'opera'])
            
            if is_browser:
                # Para navegadores, forzar descarga directa
                return send_file(filepath, as_attachment=True, download_name=filename)
            else:
                # Para otros clientes (como curl, wget, etc.)
                return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:        return jsonify({'error': f'Error al descargar archivo: {str(e)}'}), 500

@app.route('/auto_download/<download_id>')
def auto_download(download_id):
    """Sirve el archivo o ZIP correcto para la descarga automática."""
    try:
        # Obtener la lista de archivos del diccionario de resultados
        file_paths = download_results.get(download_id)

        if not file_paths:
            return jsonify({'error': 'ID de descarga no válido o expirado'}), 404

        # Si solo hay un archivo (canción única o playlist ya comprimida)
        if len(file_paths) == 1:
            filepath = file_paths[0]
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
            else:
                return jsonify({'error': 'Archivo no encontrado en el servidor'}), 404

        # Si hay múltiples archivos, crear un ZIP al vuelo
        # Si hay múltiples archivos, crear un ZIP al vuelo en memoria
        elif len(file_paths) > 1:
            memory_file = io.BytesIO()
            zip_name = "playlist.zip" # Nombre genérico

            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for fpath in file_paths:
                    if os.path.exists(fpath):
                        zipf.write(fpath, os.path.basename(fpath))
            
            memory_file.seek(0)

            # Enviar el ZIP desde la memoria
            return send_file(
                memory_file,
                as_attachment=True,
                download_name=zip_name,
                mimetype='application/zip'
            )

        else: # Si la lista está vacía
            return jsonify({'error': 'No se encontraron archivos para esta descarga'}), 404

    except Exception as e:
        return jsonify({'error': f'Error en descarga automática: {str(e)}'}), 500
    finally:
        # Limpiar el resultado para que no se pueda volver a descargar
        if download_id in download_results:
            del download_results[download_id]


if __name__ == '__main__':
    # Crear carpeta de descargas si no existe
    if not os.path.exists('descargas'):
        os.makedirs('descargas')
    
    # Configuración para desarrollo local
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Configuración para producción
    if not os.path.exists('descargas'):
        os.makedirs('descargas')
