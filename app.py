from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import subprocess
import sys
import threading
import time
import json
from datetime import datetime, timedelta
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
download_timestamps = {} # Para rastrear cuándo se crearon las descargas

def check_ffmpeg_availability():
    """Verificar si FFmpeg está disponible en el sistema"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def cleanup_old_downloads():
    """Limpiar descargas antiguas (más de 10 minutos)"""
    current_time = datetime.now()
    to_remove = []
    
    for download_id, timestamp in download_timestamps.items():
        if current_time - timestamp > timedelta(minutes=10):
            to_remove.append(download_id)
    
    for download_id in to_remove:
        if download_id in download_results:
            del download_results[download_id]
        if download_id in download_timestamps:
            del download_timestamps[download_id]
        if download_id in download_status:
            del download_status[download_id]
        if download_id in download_progress:
            del download_progress[download_id]

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
    current_track = 0
    total_tracks = 1

    def progress_hook(d):
        nonlocal current_track, total_tracks
        
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                progress = int((d['downloaded_bytes'] / total_bytes) * 100)
                
                # Para playlists, mostrar progreso por canción
                if tipo == 'playlist' and total_tracks > 1:
                    overall_progress = int(((current_track - 1) / total_tracks * 100) + (progress / total_tracks))
                    download_progress[download_id] = {
                        "status": f"Descargando canción {current_track}/{total_tracks}: {progress}%",
                        "progress": overall_progress
                    }
                else:
                    download_progress[download_id] = {
                        "status": f"Descargando: {progress}%",
                        "progress": progress
                    }
        elif d['status'] == 'finished':
            # Cuando un archivo se completa, guardar su ruta
            filename = d.get('filename')
            if filename:
                downloaded_files.append(filename)
                current_track += 1
                
            if tipo == 'playlist' and total_tracks > 1:
                download_progress[download_id] = {
                    "status": f"Completada canción {current_track}/{total_tracks}",
                    "progress": int((current_track / total_tracks) * 100)
                }
            else:
                download_progress[download_id] = {"status": "Procesando...", "progress": 100}

    try:
        download_status[download_id] = "downloading"
        download_progress[download_id] = {"status": "Iniciando descarga...", "progress": 0}
        download_results[download_id] = [] # Limpiar resultados previos

        # Limpiar URL
        url = url.strip().split('?')[0]

        # Verificar si FFmpeg está disponible
        ffmpeg_available = check_ffmpeg_availability()
        
        # Opciones base para yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': {
                'default': os.path.join('descargas', '%(title)s.%(ext)s')
            },
            'progress_hooks': [progress_hook],
            'noplaylist': tipo != 'playlist',
            'quiet': True,
            'no_warnings': True,
        }
        
        # Solo agregar postprocessors si FFmpeg está disponible
        if ffmpeg_available:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }]
        else:
            # Sin FFmpeg, descargar el mejor formato disponible (generalmente MP3)
            ydl_opts['format'] = 'bestaudio[ext=mp3]/bestaudio/best'

        playlist_folder = None
        # Opciones específicas para playlists
        if tipo == 'playlist':
            # Obtener información de la playlist para contar canciones
            info = yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}).extract_info(url, download=False)
            playlist_title = info.get('title', f'playlist_{download_id}')
            safe_playlist_title = "".join([c for c in playlist_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            
            # Contar el número total de canciones
            entries = info.get('entries', [])
            total_tracks = len(entries)
            
            download_progress[download_id] = {
                "status": f"Preparando descarga de {total_tracks} canciones...",
                "progress": 0
            }

            # Para descargas individuales (por defecto), mantener archivos separados
            if zip_option != 'zip':
                # Crear subcarpeta para la playlist pero mantener archivos individuales
                playlist_folder = os.path.join('descargas', safe_playlist_title)
                ydl_opts['outtmpl'] = {
                    'default': os.path.join(playlist_folder, '%(title)s.%(ext)s')
                }
            else:
                # Solo para ZIP, usar carpeta temporal
                playlist_folder = os.path.join('descargas', safe_playlist_title)
                ydl_opts['outtmpl'] = {
                    'default': os.path.join(playlist_folder, '%(title)s.%(ext)s')
                }

        # Iniciar descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Procesar resultados según el tipo de descarga
        if tipo == 'playlist':
            if zip_option == 'zip':
                # Solo comprimir si se solicitó específicamente
                download_progress[download_id] = {"status": "Comprimiendo...", "progress": 95}
                zip_filename = zip_playlist_files(playlist_folder, safe_playlist_title)
                if not zip_filename:
                    raise Exception("Error al crear el archivo ZIP")
                download_results[download_id] = [os.path.join('descargas', zip_filename)]
            else:
                # Mantener archivos individuales para descarga automática individual
                download_results[download_id] = downloaded_files
                download_progress[download_id] = {
                    "status": f"¡{len(downloaded_files)} canciones listas para descarga automática!",
                    "progress": 100
                }
        else:
            # Canción individual
            download_results[download_id] = downloaded_files

        download_status[download_id] = "completed"
        
        # Mensaje personalizado según el tipo de descarga
        format_info = "FLAC" if ffmpeg_available else "MP3"
        
        if tipo == 'playlist':
            if zip_option == 'zip':
                status_message = f"¡Playlist en {format_info} comprimida en ZIP y lista para descarga automática!"
            else:
                status_message = f"¡{len(downloaded_files)} canciones en {format_info} listas para descarga automática individual!"
        else:
            status_message = f"¡Canción en {format_info} lista para descarga automática!"
            
        download_progress[download_id] = {"status": status_message, "progress": 100}

    except Exception as e:
        download_status[download_id] = "error"
        download_progress[download_id] = {"status": f"Error: {str(e)}", "progress": 0}
        if download_id in download_results:
            del download_results[download_id] # Limpiar en caso de error

@app.route('/')
def index():
    """Página principal"""
    # Verificar si FFmpeg está disponible
    ffmpeg_available = check_ffmpeg_availability()
    return render_template('index.html', scdl_installed=True, ffmpeg_installed=ffmpeg_available)

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
    download_timestamps[download_id] = datetime.now()
    
    # Limpiar descargas antiguas
    cleanup_old_downloads()
    
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

@app.route('/api/downloads')
def api_downloads():
    """API para obtener archivos descargados"""
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
    
    return jsonify({'files': files})

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
    """Sirve el archivo o archivos para la descarga automática."""
    try:
        # Obtener la lista de archivos del diccionario de resultados
        file_paths = download_results.get(download_id)

        if not file_paths:
            # Crear un archivo de texto informativo en lugar de devolver JSON
            info_content = "ID de descarga no válido o expirado.\nPor favor, intenta descargar nuevamente."
            memory_file = io.BytesIO(info_content.encode('utf-8'))
            
            return send_file(
                memory_file,
                as_attachment=True,
                download_name="error_descarga.txt",
                mimetype='text/plain'
            )

        # Si solo hay un archivo (canción única o playlist ya comprimida)
        if len(file_paths) == 1:
            filepath = file_paths[0]
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
            else:
                # Crear un archivo de texto informativo en lugar de devolver JSON
                info_content = "Archivo no encontrado en el servidor.\nPor favor, intenta descargar nuevamente."
                memory_file = io.BytesIO(info_content.encode('utf-8'))
                
                return send_file(
                    memory_file,
                    as_attachment=True,
                    download_name="archivo_no_encontrado.txt",
                    mimetype='text/plain'
                )

        # Si hay múltiples archivos, crear un ZIP temporal automáticamente
        elif len(file_paths) > 1:
            memory_file = io.BytesIO()
            
            # Generar nombre más descriptivo para el ZIP
            first_file = os.path.basename(file_paths[0])
            playlist_name = first_file.split('.')[0] if first_file else 'playlist'
            zip_name = f"{playlist_name}_playlist_{len(file_paths)}_canciones.zip"

            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for fpath in file_paths:
                    if os.path.exists(fpath):
                        # Usar solo el nombre del archivo, no la ruta completa
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
            # Crear un archivo de texto informativo en lugar de devolver JSON
            info_content = "No se encontraron archivos para esta descarga.\nPor favor, intenta descargar nuevamente."
            memory_file = io.BytesIO(info_content.encode('utf-8'))
            
            return send_file(
                memory_file,
                as_attachment=True,
                download_name="info_descarga.txt",
                mimetype='text/plain'
            )

    except Exception as e:
        # Crear un archivo de texto informativo en lugar de devolver JSON
        info_content = f"Error en descarga automática: {str(e)}\nPor favor, intenta descargar nuevamente."
        memory_file = io.BytesIO(info_content.encode('utf-8'))
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name="error_descarga.txt",
            mimetype='text/plain'
        )
    finally:
        # Limpiar el resultado después de la descarga
        if download_id in download_results:
            del download_results[download_id]


@app.route('/download_individual/<download_id>/<int:file_index>')
def download_individual_file(download_id, file_index):
    """Descargar un archivo individual de una playlist."""
    try:
        file_paths = download_results.get(download_id)
        
        if not file_paths or file_index >= len(file_paths):
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        filepath = file_paths[file_index]
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        else:
            return jsonify({'error': 'Archivo no encontrado en el servidor'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error al descargar archivo individual: {str(e)}'}), 500

@app.route('/get_download_files/<download_id>')
def get_download_files(download_id):
    """Obtener la lista de archivos de una descarga para procesamiento individual."""
    try:
        file_paths = download_results.get(download_id)
        
        if not file_paths:
            return jsonify({'error': 'ID de descarga no válido o expirado'}), 404
            
        valid_files = [os.path.basename(fpath) for fpath in file_paths if os.path.exists(fpath)]
        
        return jsonify({
            'success': True,
            'files': valid_files,
            'count': len(valid_files)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener archivos: {str(e)}'}), 500


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
