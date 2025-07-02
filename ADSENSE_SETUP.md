# 📢 Configuración de Google AdSense

Esta aplicación está preparada para mostrar anuncios de Google AdSense de manera elegante y que no interfiera con la experiencia del usuario.

## 🚀 Configuración Rápida

### 1. Crear cuenta de AdSense
1. Ve a [Google AdSense](https://www.google.com/adsense/)
2. Crea una cuenta o inicia sesión
3. Agrega tu sitio web

### 2. Obtener tu Publisher ID
1. En tu panel de AdSense, ve a "Cuenta" → "Información de la cuenta"
2. Copia tu **Publisher ID** (formato: `ca-pub-XXXXXXXXXXXXXXXXX`)

### 3. Crear unidades de anuncio
Crea las siguientes unidades de anuncio en AdSense:

#### Banner Superior/Inferior
- **Tipo:** Display
- **Tamaño:** Responsive o 728x90
- **Nombre:** "Banner Principal"

#### Anuncio Rectangular
- **Tipo:** Display  
- **Tamaño:** 300x250 o Responsive
- **Nombre:** "Rectangle Medio"

#### Anuncio Lateral
- **Tipo:** Display
- **Tamaño:** 160x600 o Responsive
- **Nombre:** "Sidebar"

### 4. Configurar en la aplicación

Reemplaza en `templates/base.html` y `templates/index.html`:

```html
<!-- Cambia esto -->
data-ad-client="ca-pub-XXXXXXXXXXXXXXXXX"
data-ad-slot="XXXXXXXXXX"

<!-- Por tus valores reales -->
data-ad-client="ca-pub-1234567890123456"
data-ad-slot="9876543210"
```

## 📍 Ubicación de los Anuncios

- **Banner Superior:** Aparece al inicio de cada página
- **Banner Inferior:** Aparece al final de cada página
- **Anuncio Rectangular:** En el medio de la página principal
- **Anuncio Lateral:** En la página de descargas (solo en pantallas grandes)

## 🎨 Diseño Integrado

Los anuncios están estilizados para:
- ✅ Integrarse con el tema claro/oscuro
- ✅ Tener bordes redondeados y efectos glassmorphism
- ✅ Ser responsive en todos los dispositivos
- ✅ No interrumpir la experiencia del usuario

## 💰 Optimización

Para maximizar los ingresos:
1. **Posicionamiento:** Los anuncios están en ubicaciones estratégicas
2. **Responsive:** Se adaptan a todos los tamaños de pantalla
3. **Lazy Loading:** Los anuncios se cargan con retraso para mejor rendimiento
4. **Tema Adaptivo:** Se ven bien en modo claro y oscuro

## 🔧 Personalización

Para modificar la apariencia de los anuncios, edita las clases CSS:
- `.ad-container`: Contenedor principal del anuncio
- `.ad-label`: Etiqueta "Publicidad"
- `.ad-banner`, `.ad-rectangle`, `.ad-sidebar`: Tipos específicos

## ⚠️ Importante

- Asegúrate de cumplir con las políticas de AdSense
- No hagas clic en tus propios anuncios
- Los anuncios pueden tardar hasta 24-48 horas en aparecer después de la configuración
- Mantén tus IDs de anuncio privados y seguros

## 🌐 Deploying con Anuncios

Cuando subas a producción:
1. Reemplaza todos los `XXXXXXXXX` con tus IDs reales
2. Verifica que el dominio esté aprobado en AdSense
3. Monitorea el rendimiento en el panel de AdSense
