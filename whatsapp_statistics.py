import re
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from functools import lru_cache

try:
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
except Exception:  # pragma: no cover
    SentimentIntensityAnalyzer = None

# --- Expresiones Regulares ---
# Se admite una coma opcional y año de 2 o 4 dígitos.
message_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}) - (.*)$")

# Para detectar emojis individualmente (rangos Unicode ampliados)
emoji_pattern = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # Emoticons (caras)
    "\U0001f300-\U0001f5ff"  # Símbolos y pictogramas misceláneos
    "\U0001f680-\U0001f6ff"  # Transporte y símbolos de mapas
    "\U0001f700-\U0001f77f"  # Símbolos alquímicos
    "\U0001f780-\U0001f7ff"  # Formas geométricas extendidas
    "\U0001f800-\U0001f8ff"  # Flechas suplementarias-C
    "\U0001f900-\U0001f9ff"  # Símbolos y pictogramas suplementarios (emojis nuevos)
    "\U0001fa00-\U0001fa6f"  # Símbolos de ajedrez
    "\U0001fa70-\U0001faff"  # Símbolos y pictogramas extendidos-A (emojis 2020+)
    "\U0001fb00-\U0001fbff"  # Símbolos para terminales legacy
    "\U0001f1e0-\U0001f1ff"  # Indicadores de región (banderas)
    "\U00002702-\U000027b0"  # Dingbats
    "\U000024c2-\U0001f251"  # Símbolos encerrados
    "\U0001f004"  # Mahjong tile
    "\U0001f0cf"  # Carta de joker
    "\U00002600-\U000026ff"  # Símbolos misceláneos (sol, luna, etc.)
    "\U00002700-\U000027bf"  # Dingbats
    "\U0000fe00-\U0000fe0f"  # Selectores de variación
    "\U0001f100-\U0001f1ff"  # Suplemento alfanumérico encerrado
    "]",
    flags=re.UNICODE,
)

# Patrón para identificar links
link_pattern = re.compile(r"https?://\S+")

_basic_word_pattern = re.compile(r"\b\w+\b", flags=re.UNICODE)


def _basic_stopwords_en():
    return {
        # Articles & Determiners
        "the",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        # Pronouns
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
        "his",
        "her",
        "its",
        "our",
        "their",
        "mine",
        "yours",
        "hers",
        "ours",
        "theirs",
        "myself",
        "yourself",
        "himself",
        "herself",
        "itself",
        "ourselves",
        "themselves",
        # Prepositions
        "in",
        "on",
        "at",
        "to",
        "for",
        "with",
        "by",
        "from",
        "of",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "over",
        "out",
        "up",
        "down",
        "off",
        # Conjunctions
        "and",
        "or",
        "but",
        "nor",
        "so",
        "yet",
        "both",
        "either",
        "neither",
        "because",
        "although",
        "while",
        "if",
        "unless",
        "until",
        "when",
        "where",
        # Verbs (common/auxiliary)
        "is",
        "am",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        "done",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "must",
        "can",
        "could",
        "get",
        "got",
        "getting",
        "goes",
        "going",
        "went",
        "gone",
        # Common adverbs
        "very",
        "really",
        "just",
        "also",
        "too",
        "only",
        "even",
        "still",
        "now",
        "then",
        "here",
        "there",
        "always",
        "never",
        "ever",
        "already",
        "again",
        "often",
        "sometimes",
        "usually",
        # Question words
        "what",
        "which",
        "who",
        "whom",
        "whose",
        "why",
        "how",
        # Common chat words
        "yes",
        "no",
        "not",
        "ok",
        "okay",
        "yeah",
        "yea",
        "yep",
        "nope",
        "like",
        "well",
        "oh",
        "ah",
        "um",
        "uh",
        "hm",
        "hmm",
        "lol",
        "haha",
        "hahaha",
        "lmao",
        "omg",
        # Other common words
        "as",
        "than",
        "such",
        "more",
        "most",
        "some",
        "any",
        "all",
        "each",
        "other",
        "another",
        "same",
        "different",
        "own",
        "one",
        "two",
        "first",
        "last",
        "next",
        "new",
        "old",
        "good",
        "bad",
        "thing",
        "things",
        "something",
        "anything",
        "nothing",
        "everything",
        "someone",
        "anyone",
        "everyone",
        "nobody",
        "time",
        "day",
        "way",
        "lot",
        "much",
        "many",
        "few",
        "little",
        "bit",
        "want",
        "need",
        "know",
        "think",
        "see",
        "look",
        "come",
        "make",
        "take",
        "give",
        "tell",
        "say",
        "said",
        "let",
        "put",
        "try",
        "keep",
    }


def _basic_stopwords_es():
    return {
        # Artículos
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "unos",
        "unas",
        "lo",
        # Contracciones
        "al",
        "del",
        # Pronombres personales
        "yo",
        "tú",
        "tu",
        "él",
        "ella",
        "ello",
        "nosotros",
        "nosotras",
        "vosotros",
        "vosotras",
        "ustedes",
        "ellos",
        "ellas",
        "me",
        "te",
        "se",
        "nos",
        "os",
        "le",
        "les",
        "lo",
        "la",
        "los",
        "las",
        # Posesivos
        "mi",
        "mis",
        "tu",
        "tus",
        "su",
        "sus",
        "nuestro",
        "nuestra",
        "nuestros",
        "nuestras",
        "vuestro",
        "vuestra",
        "vuestros",
        "vuestras",
        "mío",
        "mía",
        "míos",
        "mías",
        "tuyo",
        "tuya",
        "tuyos",
        "tuyas",
        "suyo",
        "suya",
        "suyos",
        "suyas",
        # Demostrativos
        "este",
        "esta",
        "estos",
        "estas",
        "esto",
        "ese",
        "esa",
        "esos",
        "esas",
        "eso",
        "aquel",
        "aquella",
        "aquellos",
        "aquellas",
        "aquello",
        # Preposiciones
        "a",
        "ante",
        "bajo",
        "con",
        "contra",
        "de",
        "desde",
        "durante",
        "en",
        "entre",
        "hacia",
        "hasta",
        "mediante",
        "para",
        "por",
        "según",
        "sin",
        "sobre",
        "tras",
        # Conjunciones
        "y",
        "e",
        "o",
        "u",
        "ni",
        "que",
        "pero",
        "sino",
        "aunque",
        "porque",
        "pues",
        "como",
        "si",
        "cuando",
        "donde",
        "mientras",
        "aunque",
        # Verbos auxiliares y comunes
        "ser",
        "soy",
        "eres",
        "es",
        "somos",
        "sois",
        "son",
        "era",
        "eras",
        "éramos",
        "eran",
        "fue",
        "fueron",
        "sido",
        "siendo",
        "estar",
        "estoy",
        "estás",
        "está",
        "estamos",
        "estáis",
        "están",
        "estaba",
        "estuve",
        "estuvo",
        "estado",
        "estando",
        "haber",
        "he",
        "has",
        "ha",
        "hay",
        "hemos",
        "habéis",
        "han",
        "había",
        "hubo",
        "habido",
        "habiendo",
        "tener",
        "tengo",
        "tienes",
        "tiene",
        "tenemos",
        "tienen",
        "tenía",
        "tuvo",
        "tenido",
        "teniendo",
        "poder",
        "puedo",
        "puedes",
        "puede",
        "podemos",
        "pueden",
        "podía",
        "pudo",
        "podido",
        "pudiendo",
        "hacer",
        "hago",
        "haces",
        "hace",
        "hacemos",
        "hacen",
        "hacía",
        "hizo",
        "hecho",
        "haciendo",
        "ir",
        "voy",
        "vas",
        "va",
        "vamos",
        "van",
        "iba",
        "fue",
        "ido",
        "yendo",
        "decir",
        "digo",
        "dices",
        "dice",
        "decimos",
        "dicen",
        "dijo",
        "dicho",
        "ver",
        "veo",
        "ves",
        "ve",
        "vemos",
        "ven",
        "vio",
        "visto",
        "dar",
        "doy",
        "das",
        "da",
        "damos",
        "dan",
        "dio",
        "dado",
        "saber",
        "sé",
        "sabes",
        "sabe",
        "sabemos",
        "saben",
        "supo",
        "sabido",
        "querer",
        "quiero",
        "quieres",
        "quiere",
        "queremos",
        "quieren",
        "quiso",
        # Adverbios comunes
        "más",
        "menos",
        "muy",
        "mucho",
        "mucha",
        "muchos",
        "muchas",
        "poco",
        "poca",
        "pocos",
        "pocas",
        "tan",
        "tanto",
        "tanta",
        "tantos",
        "tantas",
        "bien",
        "mal",
        "mejor",
        "peor",
        "siempre",
        "nunca",
        "jamás",
        "ya",
        "aún",
        "todavía",
        "ahora",
        "antes",
        "después",
        "luego",
        "aquí",
        "ahí",
        "allí",
        "acá",
        "allá",
        "cerca",
        "lejos",
        "también",
        "tampoco",
        "solo",
        "sólo",
        "además",
        # Interrogativos
        "qué",
        "quién",
        "quiénes",
        "cuál",
        "cuáles",
        "cuánto",
        "cuánta",
        "cuántos",
        "cuántas",
        "cómo",
        "dónde",
        "cuándo",
        "por qué",
        # Indefinidos
        "algo",
        "alguien",
        "alguno",
        "alguna",
        "algunos",
        "algunas",
        "nada",
        "nadie",
        "ninguno",
        "ninguna",
        "todo",
        "toda",
        "todos",
        "todas",
        "cada",
        "otro",
        "otra",
        "otros",
        "otras",
        "mismo",
        "misma",
        "mismos",
        "mismas",
        "uno",
        "dos",
        "tres",
        "vez",
        "veces",
        "día",
        "días",
        # Palabras de chat comunes
        "sí",
        "no",
        "ok",
        "bueno",
        "buena",
        "pues",
        "vale",
        "oye",
        "mira",
        "jaja",
        "jajaja",
        "jajajaja",
        "jejeje",
        "xd",
        "xdd",
        "ay",
        "uy",
        "ah",
        "oh",
        "eh",
        "hola",
        "chao",
        "adiós",
        # Otras palabras muy comunes
        "cosa",
        "cosas",
        "vez",
        "veces",
        "forma",
        "manera",
        "parte",
        "tiempo",
        "año",
        "años",
        "vida",
    }


@lru_cache(maxsize=8)
def _get_spacy_nlp(lang: str):
    """Lazy-load spaCy pipelines. Returns None if spaCy (or model) isn't available."""
    if spacy is None:
        return None

    model = "en_core_web_sm" if lang == "en" else "es_core_news_sm"
    try:
        # Disable components not needed for lemmatization to keep it fast.
        return spacy.load(model, disable=["ner", "parser"])
    except Exception:
        return None


@lru_cache(maxsize=2)
def _get_vader():
    if SentimentIntensityAnalyzer is None:
        return None
    try:
        return SentimentIntensityAnalyzer()
    except Exception:
        return None


def _detect_lang_fast(text: str, stop_en: set, stop_es: set) -> str:
    """Heuristic language detector: compares stopword hits for EN vs ES."""
    # Limit token scan for performance on long messages.
    tokens = _basic_word_pattern.findall(text.lower())[:60]
    if not tokens:
        return "en"
    en_hits = sum(1 for t in tokens if t in stop_en)
    es_hits = sum(1 for t in tokens if t in stop_es)
    return "es" if es_hits > en_hits else "en"


def _normalize_text_for_nlp(text: str) -> str:
    text = text.replace("<Media omitted>", " ")
    text = link_pattern.sub(" ", text)
    return text


def _sentiment_label(compound: float) -> str:
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


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
    Soporta patrones en inglés y español.
    """
    texto = message.strip().lower()
    ignore_patterns = [
        # Genéricos
        "null",
        # Inglés - Cifrado y privacidad
        "end-to-end encrypted",
        "messages and calls are end-to-end encrypted",
        "only people in this chat can read",
        "learn more",
        "your security code with",
        "security code changed",
        "tap to learn more",
        # Inglés - Acciones de grupo
        "created group",
        "added you",
        "added to this group",
        "removed from this group",
        "left the group",
        "changed the subject",
        "changed this group's icon",
        "changed the group description",
        "you're now an admin",
        "is no longer an admin",
        "changed their phone number",
        "deleted this message",
        "this message was deleted",
        "you deleted this message",
        "waiting for this message",
        "missed voice call",
        "missed video call",
        # Español - Cifrado y privacidad
        "cifrado de extremo a extremo",
        "los mensajes y las llamadas están cifrados",
        "solo las personas de este chat pueden leer",
        "más información",
        "tu código de seguridad con",
        "el código de seguridad cambió",
        "toca para más información",
        # Español - Acciones de grupo
        "creó el grupo",
        "creó este grupo",
        "te añadió",
        "te agregó",
        "añadió",
        "agregó",
        "se unió con el enlace",
        "salió del grupo",
        "abandonó el grupo",
        "eliminó a",
        "expulsó a",
        "ahora eres administrador",
        "ya no es administrador",
        "cambió el asunto",
        "cambió el icono del grupo",
        "cambió la descripción del grupo",
        "cambió su número de teléfono",
        "eliminó este mensaje",
        "eliminaste este mensaje",
        "se eliminó este mensaje",
        "esperando este mensaje",
        "llamada de voz perdida",
        "videollamada perdida",
        # Mensajes de ubicación
        "location:",
        "ubicación:",
        "live location",
        "ubicación en tiempo real",
        # Contactos compartidos
        "contact card omitted",
        "tarjeta de contacto omitida",
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
    palabras_counter_raw = Counter()
    palabras_counter_nlp = Counter()
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

    # --- NLP/Sentiment setup (done once; used during the main loop) ---
    stop_en = set(_basic_stopwords_en())
    stop_es = set(_basic_stopwords_es())

    if spacy is not None:
        try:
            from spacy.lang.en.stop_words import STOP_WORDS as SPACY_STOP_EN  # type: ignore

            stop_en |= set(SPACY_STOP_EN)
        except Exception:
            pass
        try:
            from spacy.lang.es.stop_words import STOP_WORDS as SPACY_STOP_ES  # type: ignore

            stop_es |= set(SPACY_STOP_ES)
        except Exception:
            pass

    nlp_en = _get_spacy_nlp("en")
    nlp_es = _get_spacy_nlp("es")
    use_spacy = (nlp_en is not None) or (nlp_es is not None)
    grouped_texts = {"en": [], "es": []} if use_spacy else None

    vader = _get_vader()
    sent_sum_by_persona = defaultdict(float)
    sent_count_by_persona = defaultdict(int)
    sent_counts_by_persona = defaultdict(
        lambda: {"positive": 0, "neutral": 0, "negative": 0}
    )
    sent_sum_by_day = defaultdict(float)
    sent_count_by_day = defaultdict(int)
    sent_global_counts = {"positive": 0, "neutral": 0, "negative": 0}
    sent_global_sum = 0.0
    sent_global_n = 0

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
        palabras_counter_raw.update(palabras)

        # Contar palabras por persona
        if msg["sender"] is not None:
            palabras_por_persona[msg["sender"]] += palabras_en_msg
            mensajes_count_persona[msg["sender"]] += 1

        # NLP/sentiment text (normalized once)
        normalized = _normalize_text_for_nlp(msg["message"])
        lang = _detect_lang_fast(normalized, stop_en, stop_es)

        # Lemma/stopword word frequencies
        if grouped_texts is not None:
            grouped_texts[lang].append(normalized)
        else:
            # Fallback mode (no spaCy models): tokenize + stopwords inline
            primary = stop_en if lang == "en" else stop_es
            secondary = stop_es if lang == "en" else stop_en
            for w in _basic_word_pattern.findall(normalized.lower()):
                if len(w) < 2:
                    continue
                if w.isdigit():
                    continue
                if w in primary or w in secondary:
                    continue
                palabras_counter_nlp[w] += 1

        # Sentiment (VADER) in-stream
        sender = msg.get("sender")
        if vader is not None and sender:
            text = normalized.strip()
            if text:
                compound = float(vader.polarity_scores(text).get("compound", 0.0))
                label = _sentiment_label(compound)

                sent_sum_by_persona[sender] += compound
                sent_count_by_persona[sender] += 1
                sent_counts_by_persona[sender][label] += 1

                day = dt.date().isoformat()
                sent_sum_by_day[day] += compound
                sent_count_by_day[day] += 1

                sent_global_sum += compound
                sent_global_n += 1
                sent_global_counts[label] += 1

    palabras_promedio = total_palabras / total_messages if total_messages > 0 else 0

    # --- NLP: stopwords + lemmatization (spaCy if available) ---
    def _consume_spacy_texts(nlp, texts, stop_primary: set, stop_secondary: set):
        if not texts:
            return
        if nlp is None:
            # If one language model isn't available, fallback to basic tokenization.
            for t in texts:
                for w in _basic_word_pattern.findall((t or "").lower()):
                    if len(w) < 2:
                        continue
                    if w.isdigit():
                        continue
                    if w in stop_primary or w in stop_secondary:
                        continue
                    palabras_counter_nlp[w] += 1
            return

        for doc in nlp.pipe(texts, batch_size=256):
            for tok in doc:
                if tok.is_space or tok.is_punct:
                    continue
                if not tok.is_alpha:
                    continue
                lemma = (tok.lemma_ or tok.text).lower().strip()
                if not lemma or lemma == "-pron-":
                    lemma = tok.text.lower().strip()
                if len(lemma) < 2:
                    continue
                if lemma in stop_primary or lemma in stop_secondary:
                    continue
                palabras_counter_nlp[lemma] += 1

    if grouped_texts is not None:
        # Use both stopword sets regardless of detected language for bilingual chats.
        _consume_spacy_texts(nlp_en, grouped_texts.get("en", []), stop_en, stop_es)
        _consume_spacy_texts(nlp_es, grouped_texts.get("es", []), stop_es, stop_en)

    sentimiento_por_persona = {}
    for persona in participantes:
        n = sent_count_by_persona.get(persona, 0)
        avg = (sent_sum_by_persona.get(persona, 0.0) / n) if n else 0.0
        counts = sent_counts_by_persona.get(
            persona, {"positive": 0, "neutral": 0, "negative": 0}
        )
        sentimiento_por_persona[persona] = {
            "promedio_compound": round(avg, 4),
            "positive": int(counts.get("positive", 0)),
            "neutral": int(counts.get("neutral", 0)),
            "negative": int(counts.get("negative", 0)),
            "total": int(n),
        }

    sentimiento_por_dia = {}
    for day, n in sent_count_by_day.items():
        if n:
            sentimiento_por_dia[day] = round(sent_sum_by_day[day] / n, 4)

    sentimiento_global = {
        "promedio_compound": (
            round((sent_global_sum / sent_global_n), 4) if sent_global_n else 0.0
        ),
        "positive": int(sent_global_counts["positive"]),
        "neutral": int(sent_global_counts["neutral"]),
        "negative": int(sent_global_counts["negative"]),
        "total": int(sent_global_n),
        "engine": "vader" if vader is not None else "disabled",
        "coverage": {
            "scored_messages": int(sent_global_n),
            "total_messages": int(total_messages),
            "scored_pct": (
                round((sent_global_n / total_messages) * 100, 1)
                if total_messages
                else 0.0
            ),
        },
    }

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
        # Keep both raw and NLP-cleaned variants. Frontend can prefer NLP.
        "palabras_mas_utilizadas_raw": palabras_counter_raw.most_common(10),
        "palabras_mas_utilizadas_nlp": palabras_counter_nlp.most_common(50),
        # Backward-compatible key (now returns NLP-cleaned words)
        "palabras_mas_utilizadas": (
            palabras_counter_nlp.most_common(10)
            if palabras_counter_nlp
            else palabras_counter_raw.most_common(10)
        ),
        "total_multimedia": multimedia_count,
        "total_links": total_links,
        # Sentiment
        "sentimiento_por_persona": sentimiento_por_persona,
        "sentimiento_por_dia": sentimiento_por_dia,
        "sentimiento_global": sentimiento_global,
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
        # NLP/Analysis metadata - informa qué funcionalidades están activas
        "nlp_info": {
            "spacy_available": spacy is not None,
            "spacy_en_model": nlp_en is not None,
            "spacy_es_model": nlp_es is not None,
            "lemmatization_active": use_spacy,
            "stopwords_en_count": len(stop_en),
            "stopwords_es_count": len(stop_es),
            "sentiment_engine": "vader" if vader is not None else "disabled",
            "sentiment_available": vader is not None,
            "words_processed_nlp": sum(palabras_counter_nlp.values()),
            "words_processed_raw": sum(palabras_counter_raw.values()),
        },
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
