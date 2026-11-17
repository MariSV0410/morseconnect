# MorseConnect — sistema de comunicación con código Morse

## Cómo iniciar el proyecto en Windows

1. Descomprime la carpeta completa `MorseConnect`.
2. Abre esa carpeta.
3. Ejecuta `INICIAR_MORSECONNECT.bat`.
4. La primera ejecución crea el entorno virtual e instala las dependencias de Python (requiere Internet).
5. Abre `http://127.0.0.1:5000` si el navegador no se abre automáticamente.
6. Mantén abierta la ventana de terminal mientras utilizas la aplicación. Para detener el servidor, presiona `Ctrl + C`.

**No abras `templates/index.html` directamente.** La página utiliza plantillas Flask y debe abrirse desde el servidor Python para procesar correctamente sus variables y cargar los estilos.

## Diseño y funciones

El proyecto conserva el diseño de fondo blanco con detalles verde pastel, rosa y amarillo suave. Incluye traductor de texto a Morse, traductor de Morse a texto, reproducción de señales mediante LED y buzzer cuando el hardware esté configurado, lectura del botón, historial y envío de mensajes entre equipos.

## Placa y circuito

La placa de la fotografía parece una Raspberry Pi Pico W, pero el modelo y el cableado deben confirmarse antes de activar los GPIO. El proyecto inicia en modo de simulación. No actives el modo de hardware ni conectes señales a GPIO hasta verificar el cableado real. La Pico W trabaja con lógica de 3.3 V; nunca introduzcas 5 V en un GPIO.

## Si la página aparece sin diseño

- Comprueba que ejecutaste `INICIAR_MORSECONNECT.bat`.
- Entra por `http://127.0.0.1:5000`, no abriendo el HTML con doble clic.
- Verifica que exista `static/style.css` dentro de la carpeta del proyecto.
