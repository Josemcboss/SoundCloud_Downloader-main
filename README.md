# SoundCloud Downloader 🎵

Una aplicación web moderna y responsiva para descargar canciones y playlists de SoundCloud con interfaz gráfica completa.

## 🌟 Características

### Aplicación Web
- **Interfaz web moderna** con diseño glassmorphism responsivo
- **Modo oscuro completo** con transiciones suaves
- **Seguimiento en tiempo real** del progreso de descarga
- **Gestión de archivos** integrada con vista previa
- **Responsive design** optimizado para móviles y escritorio
- **Instalación automática** de dependencias desde la web

### Funcionalidades de Descarga
- Descarga canciones individuales y playlists completas
- Soporte para formato FLAC (alta calidad) y MP3
- Detección automática del tipo de contenido (canción/playlist)
- Manejo automático de errores y reintentos
- Descarga en paralelo para playlists

## 🚀 Inicio Rápido

### Aplicación Web (Recomendado)

1. **Clona este repositorio:**
```bash
git clone https://github.com/tu-usuario/SoundCloud_Downloader.git
cd SoundCloud_Downloader
```

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Inicia la aplicación web:**
```bash
python app.py
```

4. **Abre tu navegador** y ve a: `http://localhost:5000`

### Script de Línea de Comandos

Si prefieres usar la línea de comandos:
```bash
git clone https://github.com/tu-usuario/soundcloud-downloader.git
cd soundcloud-downloader
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecuta el script:
```bash
python soundcloud_downloader.py
```

2. Selecciona una opción:
   - 1: Descargar canción individual
   - 2: Descargar playlist
   - 3: Salir

3. Ingresa la URL de SoundCloud cuando se te solicite.

Las canciones se descargarán en la carpeta `descargas` con el siguiente formato:
- Nombre del archivo: `título_de_la_canción.extensión`
- Formato: FLAC (si ffmpeg está disponible) o MP3

## Características Técnicas

- Detección automática de ffmpeg
- Instalación automática de dependencias
- Manejo de errores robusto
- Soporte para diferentes sistemas operativos
- Limpieza automática de URLs

## Solución de Problemas

### Error: "ffmpeg no está instalado"
El programa intentará instalar ffmpeg automáticamente. Si falla, puedes instalarlo manualmente:

- Windows:
  1. Descarga ffmpeg desde https://ffmpeg.org/download.html
  2. Extrae los archivos en C:\ffmpeg
  3. Agrega C:\ffmpeg\bin a las variables de entorno PATH

- Linux:
```bash
sudo apt-get install ffmpeg
```

- Mac:
```bash
brew install ffmpeg
```

### Error: "No se puede descargar la playlist"
- Verifica que la URL sea correcta
- Asegúrate de tener una conexión a internet estable
- Intenta con una URL más corta (sin parámetros adicionales)

## 🎨 Modo Oscuro

La aplicación incluye un **modo oscuro completo** con:

- **Toggle automático** - Botón en la navegación superior
- **Persistencia** - Recuerda tu preferencia entre sesiones
- **Transiciones suaves** - Cambios visuales elegantes
- **Atajo de teclado** - `Ctrl + Shift + T` para cambio rápido
- **Detección del tema del sistema** - Se adapta automáticamente

### Cómo usar el modo oscuro:
1. Haz clic en el botón 🌙/☀️ en la barra de navegación
2. O usa el atajo de teclado `Ctrl + Shift + T`
3. Tu preferencia se guardará automáticamente

## 📱 Diseño Responsivo

La interfaz se adapta perfectamente a:

- **📱 Móviles** - Diseño optimizado para pantallas pequeñas
- **💻 Tablets** - Navegación táctil mejorada
- **🖥️ Escritorio** - Experiencia completa con todas las funciones

## 🔧 Gestión de Archivos

- **Vista de archivos descargados** con información detallada
- **Descarga directa** desde el navegador
- **Estadísticas** de tamaño total y tipos de archivo
- **Eliminación** de archivos no deseados
- **Búsqueda y filtrado** de contenido

## ⚙️ Configuración Automática

La aplicación web incluye una página de configuración que:

- **Verifica dependencias** automáticamente
- **Instala SCDL** con un clic
- **Guía de instalación** para FFmpeg
- **Diagnóstico del sistema** en tiempo real

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un Fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Tu Nombre - [@josemenciaa](https://instagram.com/josemenciaa) - 

Link del Proyecto: [https://github.com/tu-usuario/soundcloud-downloader]
