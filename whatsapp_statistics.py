import re
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# --- Expresiones Regulares ---
# Se admite una coma opcional y año de 2 o 4 dígitos.
message_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}) - (.*)$")

# Para detectar emojis individualmente (sin agrupar secuencias)
emoji_pattern = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # Emoticons
    "\U0001f300-\U0001f5ff"  # Símbolos y pictogramas
    "\U0001f680-\U0001f6ff"  # Transporte y símbolos
    "\U0001f1e0-\U0001f1ff"  # Banderas
    "]",
    flags=re.UNICODE,
)

# Patrón para identificar links
link_pattern = re.compile(r"https?://\S+")

# --- Funciones Auxiliares ---


def parse_date(date_str, time_str):
    """
    Dado un string de fecha y hora, prueba distintos formatos para parsearlo.
    Se prueban tanto mes/día/año como día/mes/año, con año de 2 o 4 dígitos.
    Prioriza mes/día/año (formato común en WhatsApp exports).
    """
    date_time_str = f"{date_str} {time_str}"
    formatos = [
        "%m/%d/%y %H:%M",  # US format: month/day/year (2 digits) - priority
        "%m/%d/%Y %H:%M",  # US format: month/day/year (4 digits)
        "%d/%m/%y %H:%M",  # EU format: day/month/year (2 digits)
        "%d/%m/%Y %H:%M",  # EU format: day/month/year (4 digits)
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(date_time_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha/hora no reconocido: '{date_time_str}'")


def should_ignore_message(sender, message):
    """
    Devuelve True si el mensaje es de sistema o no se considera conversacional.
    Se ignoran:
      - Mensajes cuyo texto sea "null".
      - Mensajes con avisos típicos de sistema (cifrado, creación de grupo, etc.).
    """
    texto = message.strip().lower()
    ignore_patterns = [
        "null",
        "end-to-end encrypted",
        "messages and calls are end-to-end encrypted",
        "only people in this chat can read",
        "learn more",
        "creó el grupo",
        "añadió",
    ]
    for pat in ignore_patterns:
        if pat in texto:
            return True
    return False


def _parse_chat_lines(lines_iterable):
    """Parsea iterables de líneas de chat y retorna la lista de mensajes."""
    messages = []
    current_message = None

    for line in lines_iterable:
        line = line.rstrip("\n")
        if not line:
            continue

        match = message_pattern.match(line)
        if match:
            date_str, time_str, rest = match.groups()
            try:
                dt = parse_date(date_str, time_str)
            except ValueError:
                continue

            if ": " in rest:
                sender, message_text = rest.split(": ", 1)
            else:
                sender = None
                message_text = rest

            if should_ignore_message(sender, message_text):
                current_message = None
                continue

            current_message = {
                "datetime": dt,
                "sender": sender,
                "message": message_text,
            }
            messages.append(current_message)
        else:
            if current_message is not None:
                current_message["message"] += "\n" + line
    return messages


def parse_chat(filename):
    """
    Lee el archivo de WhatsApp desde disco y retorna la lista de mensajes.
    """
    with open(filename, encoding="utf-8") as f:
        return _parse_chat_lines(f)


def parse_chat_stream(stream):
    """Parsea un chat desde un objeto tipo archivo ya cargado en memoria."""
    return _parse_chat_lines(stream)


def format_duration(td):
    """
    Formatea un timedelta para mostrarlo en minutos o en horas con un decimal.
    """
    total_seconds = td.total_seconds()
    if total_seconds < 3600:
        minutos = total_seconds / 60
        return f"{minutos:.1f} min"
    else:
        horas = total_seconds / 3600
        return f"{horas:.1f} hs"


def analyze_messages(messages):
    """
    A partir de la lista de mensajes filtrados, calcula las estadísticas:
      - Estadísticas generales: total de mensajes, participantes, mensajes por persona.
      - Actividad: mensajes por día, por hora (de 00 a 23), por día de la semana,
                   y la hora, día y persona más activos.
      - Texto y Multimedia: palabras promedio por mensaje, palabras más utilizadas,
                            total de multimedia y links.
      - Emojis: total de emojis, ranking de emojis global y por persona (solo top 10).
      - Conversaciones: iniciadores y tiempo promedio de conversación (segmentadas con gap de 2 horas).
      - Racha conversacional más larga (días consecutivos) con inicio y fin.
    """
    stats = {}

    # Ordenar mensajes por fecha para segmentar adecuadamente las conversaciones
    messages = sorted(messages, key=lambda m: m["datetime"])
    total_messages = len(messages)
    stats["total_mensajes"] = total_messages

    participantes = set()
    mensajes_por_persona = defaultdict(int)
    palabras_por_persona = defaultdict(int)  # Total de palabras por persona
    mensajes_count_persona = defaultdict(int)  # Para calcular promedio
    multimedia_count = 0
    total_emojis = 0
    total_links = 0
    palabras_counter = Counter()
    emojis_counter = Counter()
    mensajes_por_dia = defaultdict(int)
    mensajes_por_hora = defaultdict(int)  # Contaremos por hora (0-23)
    mensajes_por_dia_semana = defaultdict(int)
    total_palabras = 0

    # Emojis por persona
    emojis_por_persona = defaultdict(Counter)

    # Lapso global
    if messages:
        inicio_global = messages[0]["datetime"]
        fin_global = messages[-1]["datetime"]
        lapso = fin_global - inicio_global
    else:
        inicio_global = fin_global = lapso = None

    dias_semana = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }

    # Estadísticas básicas
    for msg in messages:
        dt = msg["datetime"]
        dia = dt.date().isoformat()
        mensajes_por_dia[dia] += 1

        mensajes_por_hora[dt.hour] += 1

        weekday = dias_semana[dt.weekday()]
        mensajes_por_dia_semana[weekday] += 1

        if msg["sender"] is not None:
            participantes.add(msg["sender"])
            mensajes_por_persona[msg["sender"]] += 1

        texto = msg["message"]
        if "<Media omitted>" in texto:
            multimedia_count += 1
            texto = texto.replace("<Media omitted>", "")

        links = link_pattern.findall(texto)
        total_links += len(links)

        emojis_en_msg = emoji_pattern.findall(texto)
        total_emojis += len(emojis_en_msg)
        for em in emojis_en_msg:
            emojis_counter[em] += 1
            if msg["sender"] is not None:
                emojis_por_persona[msg["sender"]][em] += 1

        palabras = re.findall(r"\b\w+\b", texto.lower())
        palabras_en_msg = len(palabras)
        total_palabras += palabras_en_msg
        palabras_counter.update(palabras)

        # Contar palabras por persona
        if msg["sender"] is not None:
            palabras_por_persona[msg["sender"]] += palabras_en_msg
            mensajes_count_persona[msg["sender"]] += 1

    palabras_promedio = total_palabras / total_messages if total_messages > 0 else 0

    # Aseguramos keys de "00" a "23" para mensajes por hora
    mensajes_por_hora_formateado = {
        f"{h:02d}": mensajes_por_hora.get(h, 0) for h in range(24)
    }

    # Hora, día de la semana y persona más activos
    if mensajes_por_hora:
        hora_mas_activa = max(mensajes_por_hora, key=mensajes_por_hora.get)
        hora_mas_activa_cant = mensajes_por_hora[hora_mas_activa]
    else:
        hora_mas_activa = None
        hora_mas_activa_cant = 0

    if mensajes_por_dia_semana:
        dia_semana_mas_activo = max(
            mensajes_por_dia_semana, key=mensajes_por_dia_semana.get
        )
        dia_semana_mas_activo_cant = mensajes_por_dia_semana[dia_semana_mas_activo]
    else:
        dia_semana_mas_activo = None
        dia_semana_mas_activo_cant = 0

    if mensajes_por_persona:
        persona_mas_activa = max(mensajes_por_persona, key=mensajes_por_persona.get)
        persona_mas_activa_cant = mensajes_por_persona[persona_mas_activa]
    else:
        persona_mas_activa = None
        persona_mas_activa_cant = 0

    # Conversaciones: segmentación usando gap de 2 horas
    conversaciones = []
    if messages:
        conv_iniciador = messages[0]["sender"]
        conv_inicio = messages[0]["datetime"]
        conv_fin = messages[0]["datetime"]
        prev_dt = messages[0]["datetime"]
        for msg in messages[1:]:
            dt = msg["datetime"]
            if (dt - prev_dt) < timedelta(hours=2):
                conv_fin = dt
            else:
                duracion = conv_fin - conv_inicio
                if duracion.total_seconds() > 0:
                    conversaciones.append(
                        {
                            "inicio": conv_inicio,
                            "fin": conv_fin,
                            "duracion": duracion,
                            "iniciador": conv_iniciador,
                        }
                    )
                conv_iniciador = msg["sender"]
                conv_inicio = dt
                conv_fin = dt
            prev_dt = dt
        duracion = conv_fin - conv_inicio
        if duracion.total_seconds() > 0:
            conversaciones.append(
                {
                    "inicio": conv_inicio,
                    "fin": conv_fin,
                    "duracion": duracion,
                    "iniciador": conv_iniciador,
                }
            )

    # Sólo considerar conversaciones con duración > 0
    conversaciones_validas = [
        c for c in conversaciones if c["duracion"].total_seconds() > 0
    ]
    if conversaciones_validas:
        duraciones = [
            conv["duracion"].total_seconds() for conv in conversaciones_validas
        ]
        promedio_segundos = sum(duraciones) / len(duraciones)
        promedio_duracion = format_duration(timedelta(seconds=promedio_segundos))
        # Calcular horas totales "desperdiciadas" chateando
        total_horas_chat = sum(duraciones) / 3600
    else:
        promedio_duracion = "0 min"
        total_horas_chat = 0

    # Iniciadores de conversaciones y porcentajes
    iniciadores = Counter()
    for conv in conversaciones_validas:
        if conv["iniciador"]:
            iniciadores[conv["iniciador"]] += 1
    total_conversaciones = len(conversaciones_validas)
    iniciadores_porcentajes = {
        persona: f"{(count / total_conversaciones * 100):.1f}%"
        for persona, count in iniciadores.items()
    }

    # Podio de iniciadores (ordenado de mayor a menor)
    podio_iniciadores = iniciadores.most_common()

    # Calcular tiempo de respuesta promedio por persona
    # Solo consideramos respuestas dentro de una conversación activa (gap < 2 horas)
    tiempos_respuesta_por_persona = defaultdict(list)

    if len(messages) > 1:
        prev_msg = messages[0]
        for msg in messages[1:]:
            dt = msg["datetime"]
            prev_dt = prev_msg["datetime"]
            gap = (dt - prev_dt).total_seconds()

            # Solo contar como respuesta si:
            # 1. El gap es menor a 2 horas (misma conversación)
            # 2. Es de una persona diferente (es una respuesta, no continuación)
            # 3. El gap es mayor a 5 segundos (evitar mensajes muy seguidos)
            if gap < 7200 and gap > 5 and msg["sender"] and prev_msg["sender"]:
                if msg["sender"] != prev_msg["sender"]:
                    tiempos_respuesta_por_persona[msg["sender"]].append(gap)

            prev_msg = msg

    # Calcular promedio de tiempo de respuesta por persona
    promedio_respuesta_por_persona = {}
    for persona, tiempos in tiempos_respuesta_por_persona.items():
        if tiempos:
            promedio_seg = sum(tiempos) / len(tiempos)
            promedio_respuesta_por_persona[persona] = {
                "promedio_segundos": promedio_seg,
                "promedio_formateado": format_duration(timedelta(seconds=promedio_seg)),
                "total_respuestas": len(tiempos),
            }

    # Calcular promedio de palabras por mensaje por persona
    palabras_promedio_por_persona = {}
    for persona in participantes:
        if mensajes_count_persona[persona] > 0:
            promedio = palabras_por_persona[persona] / mensajes_count_persona[persona]
            palabras_promedio_por_persona[persona] = round(promedio, 1)
        else:
            palabras_promedio_por_persona[persona] = 0

    # Racha conversacional: días consecutivos (usando toordinal)
    fechas = sorted({msg["datetime"].date() for msg in messages})
    dias_activos = len(fechas)  # Días con al menos un mensaje

    longest_streak = 0
    current_streak = 1
    streak_start = streak_end = None
    temp_start = fechas[0] if fechas else None
    for i in range(1, len(fechas)):
        # Permitir racha si la diferencia es 0 (mismo día) o 1 (día siguiente)
        if (fechas[i] - fechas[i - 1]).days <= 1:
            current_streak += 1
        else:
            if current_streak > longest_streak:
                longest_streak = current_streak
                streak_start = temp_start
                streak_end = fechas[i - 1]
            current_streak = 1
            temp_start = fechas[i]
    if fechas:
        if current_streak > longest_streak:
            longest_streak = current_streak
            streak_start = temp_start
            streak_end = fechas[-1]
    if streak_start and streak_end:
        racha_dias = (streak_end - streak_start).days + 1
    else:
        racha_dias = 0

    # Formatear fechas al formato dd-mm-yyyy para lapso y racha
    # Calcular días totales de conversación
    total_dias = (
        (fin_global.date() - inicio_global.date()).days
        if (inicio_global and fin_global)
        else 0
    )

    lapso_tiempo = {
        "inicio": inicio_global.strftime("%d-%m-%Y") if inicio_global else None,
        "fin": fin_global.strftime("%d-%m-%Y") if fin_global else None,
        "duracion": str(lapso) if lapso else None,
        "total_dias": total_dias,
    }
    racha_conversacional = {
        "duracion_dias": racha_dias,
        "inicio": streak_start.strftime("%d-%m-%Y") if streak_start else None,
        "fin": streak_end.strftime("%d-%m-%Y") if streak_end else None,
    }

    # Armado final de estadísticas agrupado por categorías
    stats_final = {
        # Estadísticas generales
        "total_mensajes": stats["total_mensajes"],
        "participantes": list(participantes),
        "mensajes_por_persona": dict(mensajes_por_persona),
        "persona_mas_activa": {
            "persona": persona_mas_activa,
            "cantidad": persona_mas_activa_cant,
        },
        # Actividad
        "mensajes_por_dia": dict(mensajes_por_dia),
        "mensajes_por_hora": mensajes_por_hora_formateado,
        "dia_semana_mas_activo": {
            "dia": dia_semana_mas_activo,
            "cantidad": dia_semana_mas_activo_cant,
        },
        "mensajes_promedio_por_dia": (
            total_messages / ((fin_global.date() - inicio_global.date()).days + 1)
            if (inicio_global and fin_global)
            else 0
        ),
        "dias_activos": dias_activos,  # Días con al menos un mensaje
        # Texto y Multimedia
        "palabras_promedio_por_mensaje": palabras_promedio,
        "palabras_promedio_por_persona": palabras_promedio_por_persona,
        "palabras_mas_utilizadas": palabras_counter.most_common(10),
        "total_multimedia": multimedia_count,
        "total_links": total_links,
        # Emojis
        "total_emojis": total_emojis,
        "emojis_mas_utilizados": emojis_counter.most_common(10),
        "emojis_por_persona": {
            persona: counter.most_common(10)
            for persona, counter in emojis_por_persona.items()
        },
        # Conversaciones
        "iniciadores_de_conversacion": {
            "iniciadores": dict(iniciadores),
            "porcentajes": iniciadores_porcentajes,
            "total_conversaciones": total_conversaciones,
            "podio": podio_iniciadores,
        },
        "tiempo_promedio_conversacion": promedio_duracion,
        "tiempo_respuesta_por_persona": promedio_respuesta_por_persona,
        "horas_totales_chat": round(total_horas_chat, 1),
        "lapso_tiempo": lapso_tiempo,
        "racha_conversacional": racha_conversacional,
    }

    return stats_final


def process_chat(input_file, output_file):
    """
    Procesa el chat exportado de WhatsApp (archivo .txt) y exporta las estadísticas en formato JSON.

    Parámetros:
      input_file: ruta al archivo de chat.
      output_file: ruta de salida para el JSON resultante.
    """
    messages = parse_chat(input_file)
    stats = analyze_messages(messages)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    print(f"Estadísticas exportadas a {output_file}")


# --- Ejemplo de uso ---
""" if __name__ == "__main__":
    chat_file = "prueba.txt"  # Modificá la ruta según corresponda
    salida_file = "salida.json"  # Ruta para el JSON resultante
    process_chat(chat_file, salida_file)
 """
