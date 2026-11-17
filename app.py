import os
import threading
import requests
from flask import Flask, render_template, request, jsonify
from morse import text_to_morse, morse_to_text
from database import init_db, save_message, get_messages, clear_messages
from hardware import HardwareController

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
init_db()

# Los caracteres que llegan desde el pulsador se acumulan aquí.
button_buffer = {'morse': ''}
button_lock = threading.Lock()


def receive_button_piece(piece):
    with button_lock:
        button_buffer['morse'] += (' / ' if piece.strip() == '/' else piece + ' ')


hardware = HardwareController(on_morse_input=receive_button_piece)


@app.get('/')
def index():
    return render_template('index.html', hardware_enabled=hardware.enabled,
                           hardware_error=hardware.error)


@app.post('/api/encode')
def encode():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()
    if not text:
        return jsonify(error='Escribe un mensaje para convertirlo.'), 400
    try:
        code = text_to_morse(text)
        save_message(text.upper(), code, 'texto_a_morse')
        return jsonify(text=text.upper(), morse=code)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@app.post('/api/decode')
def decode():
    data = request.get_json(silent=True) or {}
    code = str(data.get('morse', '')).strip()
    if not code:
        return jsonify(error='Escribe puntos y rayas. Usa espacios entre letras y / entre palabras.'), 400
    try:
        text = morse_to_text(code)
        save_message(text, code, 'morse_a_texto')
        return jsonify(text=text, morse=code)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@app.post('/api/play')
def play():
    data = request.get_json(silent=True) or {}
    code = str(data.get('morse', '')).strip()
    if not code:
        return jsonify(error='No hay código Morse para reproducir.'), 400
    if not hardware.enabled:
        return jsonify(error='Modo de simulación o Pico W desconectada. Configura HARDWARE_MODE=pico y SERIAL_PORT en .env, y ejecuta main.py en la placa.'), 409
    try:
        # Ejecutar en un hilo para no bloquear la página.
        threading.Thread(target=hardware.play_morse, args=(code,), daemon=True).start()
        return jsonify(message='Reproducción iniciada en LED y buzzer.')
    except Exception as exc:
        return jsonify(error=str(exc)), 500


@app.get('/api/button')
def button_result():
    with button_lock:
        code = button_buffer['morse']
        button_buffer['morse'] = ''
    if not code:
        return jsonify(morse='', text='')
    # El buffer contiene códigos de letras concatenados; separamos para traducir.
    normalized = code.replace('  ', ' / ')
    try:
        text = morse_to_text(normalized)
    except ValueError:
        text = 'Señal recibida; espera a completar la letra o revisa los intervalos.'
    if text:
        save_message(text, normalized, 'boton_a_texto', medio='Botón/GPIO')
    return jsonify(morse=normalized, text=text)


@app.get('/api/history')
def history():
    return jsonify(messages=get_messages())


@app.delete('/api/history')
def delete_history():
    clear_messages()
    return jsonify(message='Historial eliminado.')



@app.get('/api/inbox')
def inbox():
    """Bandeja compartida para todos los visitantes de la aplicación web."""
    return jsonify(messages=[m for m in get_messages(100) if m.get('direccion') == 'internet_recibido'])


@app.post('/api/inbox')
def post_inbox():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()[:1000]
    code = str(data.get('morse', '')).strip()[:2000]
    sender = str(data.get('sender', 'Visitante')).strip()[:40] or 'Visitante'
    if not text or not code:
        return jsonify(error='Primero convierte un mensaje a código Morse.'), 400
    save_message(f'{sender}: {text}', code, 'internet_recibido', medio='Internet', estado='Recibido')
    return jsonify(message='Mensaje publicado en la bandeja de MorseConnect.')

@app.post('/api/receive')
def receive_remote():
    """Endpoint para que otro equipo Morse reciba mensajes por HTTP."""
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()
    code = str(data.get('morse', '')).strip()
    if not text or not code:
        return jsonify(error='Se requiere texto y código Morse.'), 400
    save_message(text, code, 'internet_recibido', medio='Internet', estado='Recibido')
    return jsonify(message='Mensaje recibido correctamente.')


@app.post('/api/send_remote')
def send_remote():
    data = request.get_json(silent=True) or {}
    destination = str(data.get('url', '')).strip().rstrip('/')
    text = str(data.get('text', '')).strip()
    code = str(data.get('morse', '')).strip()
    if not destination.startswith(('http://', 'https://')):
        return jsonify(error='Escribe la dirección del otro equipo, por ejemplo http://192.168.1.50:5000'), 400
    try:
        response = requests.post(destination + '/api/receive', json={'text': text, 'morse': code}, timeout=8)
        response.raise_for_status()
        save_message(text, code, 'texto_a_morse', medio='Internet', estado='Enviado')
        return jsonify(message='Mensaje enviado al otro dispositivo.')
    except requests.RequestException as exc:
        return jsonify(error=f'No se pudo enviar el mensaje: {exc}'), 502


@app.get('/api/status')
def status():
    return jsonify(hardware='pico_w' if hardware.enabled else 'simulation',
                   hardware_error=hardware.error)


if __name__ == '__main__':
    # host 0.0.0.0 permite que otro equipo de la misma red pueda conectarse.
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=False)
