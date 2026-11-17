
from machine import Pin, PWM
from time import sleep_ms, ticks_ms, ticks_diff
import sys
import uselect
import json

BUTTON_GPIO = 14
LED_GPIO = 15
BUZZER_GPIO = 16

UNIT = 0.18
LIMITE_PULSACION = 400
REBOTE = 30
TIEMPO_LETRA = 800

# 
boton = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)
led = Pin(LED_GPIO, Pin.OUT)

buzzer = PWM(Pin(BUZZER_GPIO))
buzzer.freq(1000)
buzzer.duty_u16(0)

led.off()
tiempo_inicio = 0
tiempo_pulsacion = 0

estado_anterior = 1
estado_estable = 1
ultimo_cambio = ticks_ms()

secuencia_morse = ""
ultimo_liberado = None

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)



def enviar_evento(code):
    print(json.dumps({
        "event": "morse",
        "code": code
    }))


def enviar_estado():
    print(json.dumps({
        "event": "ready",
        "board": "Raspberry Pi Pico W",
        "project": "MorseConnect"
    }))


def activar_componentes():
    led.on()
    buzzer.duty_u16(32768)


def apagar_componentes():
    led.off()
    buzzer.duty_u16(0)


def reproducir_morse(code):

    for char in code:

        if char == ".":
            activar_componentes()
            sleep_ms(int(UNIT * 1000))
            apagar_componentes()
            sleep_ms(int(UNIT * 1000))

        elif char == "-":
            activar_componentes()
            sleep_ms(int(UNIT * 3000))
            apagar_componentes()
            sleep_ms(int(UNIT * 1000))

        elif char == " ":
            sleep_ms(int(UNIT * 2000))

        elif char == "/":
            sleep_ms(int(UNIT * 4000))


def procesar_comando():

    try:
        linea = sys.stdin.readline()

        if not linea:
            return

        datos = json.loads(linea)

        if datos.get("cmd") == "play":

            morse = datos.get("morse", "")
            reproducir_morse(morse)

            enviar_respuesta = {
                "event": "played",
                "code": morse
            }

            print(json.dumps(enviar_respuesta))

    except Exception as error:

        print(json.dumps({
            "event": "error",
            "message": str(error)
        }))


print("MorseConnect iniciado")
enviar_estado()

print("Esperando pulsaciones...")



while True:

    ahora = ticks_ms()
    lectura = boton.value()

    if lectura != estado_anterior:

        estado_anterior = lectura
        ultimo_cambio = ahora

    if ticks_diff(ahora, ultimo_cambio) >= REBOTE:

        if lectura != estado_estable:

            estado_estable = lectura

            if estado_estable == 0:

                tiempo_inicio = ahora

                activar_componentes()

                print("Boton presionado")

            else:

                apagar_componentes()

                tiempo_pulsacion = ticks_diff(
                    ahora,
                    tiempo_inicio
                )

                print("Tiempo:", tiempo_pulsacion, "ms")

                # CLASIFICAR PULSACION
                if tiempo_pulsacion < LIMITE_PULSACION:

                    simbolo = "."
                    print("PUNTO")

                else:

                    simbolo = "-"
                    print("RAYA")

                secuencia_morse += simbolo

                ultimo_liberado = ticks_ms()

                print("Secuencia:", secuencia_morse)
                print("-------------------")

    if secuencia_morse and ultimo_liberado is not None:

        tiempo_sin_presionar = ticks_diff(
            ahora,
            ultimo_liberado
        )

        if tiempo_sin_presionar >= TIEMPO_LETRA:

            enviar_evento(secuencia_morse)

            print("Letra enviada:", secuencia_morse)

            secuencia_morse = ""
            ultimo_liberado = None

    if poll.poll(0):

        procesar_comando()

    sleep_ms(5)
