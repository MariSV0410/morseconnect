# MorseConnect – publicar para recibir mensajes en un celular

## Qué hace esta versión
- La página se adapta a computadora y celular.
- El botón **Enviar por Internet** publica el texto y su código Morse en una bandeja compartida.
- La bandeja se actualiza automáticamente cada 3 segundos en todos los dispositivos que tengan abierto el mismo enlace.
- No es necesario que el celular instale Tailscale ni una aplicación. Solo abre el enlace web.

## Publicación (requiere cuentas del usuario)
1. Crea una cuenta en GitHub y un repositorio nuevo llamado `MorseConnect`.
2. Sube el contenido de esta carpeta al repositorio. No subas `.venv`, `.env` ni `morse.db`.
3. Crea una cuenta en Render y elige **New + > Web Service**.
4. Conecta tu repositorio de GitHub.
5. Configura: Runtime **Python**; Build Command `pip install -r requirements.txt`; Start Command `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 8`.
6. Agrega la variable `HARDWARE_MODE` con valor `simulation` para el servicio web.
7. Pulsa **Deploy**. Render mostrará una dirección HTTPS parecida a `https://morseconnect-xxxx.onrender.com`. Esa será la dirección que abres en el celular y compartes.

## Prueba
1. Abre el enlace en la computadora y en el celular.
2. En la computadora, escribe un mensaje y pulsa **Convertir a Morse**.
3. Pulsa **Enviar por Internet**.
4. En el celular, espera unos segundos: aparecerá en **Mensajes recibidos**.

## Importante
- La bandeja de esta versión es compartida: cualquiera que tenga el enlace puede ver los mensajes y publicar otros. No la uses para información privada.
- En el alojamiento gratuito, el servicio puede suspenderse por inactividad y el archivo SQLite puede no ser persistente tras reinicios o nuevos despliegues. Para conservar historial de forma fiable, configura una base de datos PostgreSQL o almacenamiento persistente.
- La Raspberry Pi Pico W y el LED/buzzer no se pueden controlar desde el servidor de Internet porque están conectados físicamente a tu computadora. Para accionar hardware remoto se necesita un agente local seguro en el equipo que tenga la placa.
- No se ha publicado automáticamente: para obtener un enlace real debes completar los pasos con tus cuentas de GitHub y Render.
