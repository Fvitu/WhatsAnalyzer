/**
 * Internationalization (i18n) module for WhatsAnalyzer
 * Supports English and Spanish with automatic system language detection
 */
(() => {
	const translations = {
		en: {
			// Navigation
			"nav.dashboard": "Dashboard",
			"nav.uploadChat": "Upload chat",

			// Progress bar labels
			"progress.overview": "Overview",
			"progress.mainStats": "Main Stats",
			"progress.activity": "Activity",
			"progress.usage": "Usage",
			"progress.emojis": "Emojis",
			"progress.sentiment": "Sentiment",
			"progress.statistics": "Statistics",
			"progress.response": "Response",

			// Empty state
			"empty.badge": "Smart chat analysis",
			"empty.title": "Discover insights from your",
			"empty.titleHighlight": "WhatsApp conversations",
			"empty.description": "Upload your exported chat file and get detailed statistics about messages, emojis, most used words and activity patterns.",
			"empty.demoBtn": "Try demo chat",
			"empty.uploadBtn": "Upload your chat",

			// Feature cards
			"feature.stats.title": "Detailed statistics",
			"feature.stats.desc": "Total messages, words, emojis and much more in a single view.",
			"feature.participants.title": "Participant analysis",
			"feature.participants.desc": "Discover who sends more messages and their communication style.",
			"feature.temporal.title": "Temporal patterns",
			"feature.temporal.desc": "Visualize activity by hour and day of the week.",

			// Footer
			"footer.privacy": "Your data never leaves your browser. 100% private and secure.",

			// Stats cards
			"stats.totalMessages": "Total messages",
			"stats.participants": "Participants",
			"stats.activeDays": "Active days",
			"stats.timeSpan": "Time span",
			"stats.avgMessages": "Avg. messages/day",
			"stats.hoursChatting": "Hours chatting",
			"stats.timeWasted": 'time "wasted" 😅',
			"stats.emojisUsed": "Emojis used",
			"stats.mediaShared": "Media shared",
			"stats.ofTotalDays": "of total days",
			"stats.day": "day",
			"stats.days": "days",

			// Chart titles
			"chart.messagesPerDay": "Messages per day",
			"chart.participants": "Participants",
			"chart.activityByHour": "Activity by hour",
			"chart.mostUsedWords": "Most used words",
			"chart.favoriteEmojis": "Favorite emojis",
			"chart.emojisByUser": "Emojis by user",
			"chart.sentimentByUser": "Sentiment by user",
			"chart.sentimentTimeline": "Sentiment timeline",
			"chart.participation": "Participation (message %)",
			"chart.conversationStarters": "Conversation starters",
			"chart.avgResponseTime": "Avg. response time",
			"chart.avgWordsPerMessage": "Avg. words per message",

			// Chart labels
			"chart.range": "Range",
			"chart.last7days": "Last 7 days",
			"chart.last30days": "Last 30 days",
			"chart.last3months": "Last 3 months",
			"chart.last6months": "Last 6 months",
			"chart.lastYear": "Last year",
			"chart.allTime": "All time",
			"chart.messages": "Messages",
			"chart.frequency": "Frequency",
			"chart.sentiment": "Sentiment",
			"chart.noMessages": "No messages in this period",
			"chart.noData": "No sentiment data",
			"chart.unavailable": "Sentiment unavailable (install vaderSentiment)",
			"chart.totalEmojis": "Total emojis",
			"chart.participationPct": "Participation %",
			"chart.avgTime": "Avg. time (min)",
			"chart.avgWords": "Avg. words",

			// Download buttons
			"download.json": "Download JSON",
			"download.png": "Download PNG",

			// Modal
			"modal.title": "Upload WhatsApp chat",
			"modal.description": "Export your chat without media and upload the .txt file.",
			"modal.fileLabel": ".txt file",
			"modal.cancel": "Cancel",
			"modal.analyze": "Analyze",

			// Language selector
			"lang.select": "Language",
			"lang.en": "English",
			"lang.es": "Español",
		},
		es: {
			// Navigation
			"nav.dashboard": "Panel",
			"nav.uploadChat": "Subir chat",

			// Progress bar labels
			"progress.overview": "Inicio",
			"progress.mainStats": "Estadísticas",
			"progress.activity": "Actividad",
			"progress.usage": "Uso",
			"progress.emojis": "Emojis",
			"progress.sentiment": "Sentimiento",
			"progress.statistics": "Estadísticas",
			"progress.response": "Respuesta",

			// Empty state
			"empty.badge": "Análisis inteligente de chats",
			"empty.title": "Descubre información de tus",
			"empty.titleHighlight": "conversaciones de WhatsApp",
			"empty.description":
				"Sube tu archivo de chat exportado y obtén estadísticas detalladas sobre mensajes, emojis, palabras más usadas y patrones de actividad.",
			"empty.demoBtn": "Probar demo",
			"empty.uploadBtn": "Subir tu chat",

			// Feature cards
			"feature.stats.title": "Estadísticas detalladas",
			"feature.stats.desc": "Total de mensajes, palabras, emojis y mucho más en una sola vista.",
			"feature.participants.title": "Análisis de participantes",
			"feature.participants.desc": "Descubre quién envía más mensajes y su estilo de comunicación.",
			"feature.temporal.title": "Patrones temporales",
			"feature.temporal.desc": "Visualiza la actividad por hora y día de la semana.",

			// Footer
			"footer.privacy": "Tus datos nunca salen de tu navegador. 100% privado y seguro.",

			// Stats cards
			"stats.totalMessages": "Total de mensajes",
			"stats.participants": "Participantes",
			"stats.activeDays": "Días activos",
			"stats.timeSpan": "Período de tiempo",
			"stats.avgMessages": "Mensajes/día prom.",
			"stats.hoursChatting": "Horas chateando",
			"stats.timeWasted": 'tiempo "perdido" 😅',
			"stats.emojisUsed": "Emojis usados",
			"stats.mediaShared": "Multimedia compartida",
			"stats.ofTotalDays": "del total de días",
			"stats.day": "día",
			"stats.days": "días",

			// Chart titles
			"chart.messagesPerDay": "Mensajes por día",
			"chart.participants": "Participantes",
			"chart.activityByHour": "Actividad por hora",
			"chart.mostUsedWords": "Palabras más usadas",
			"chart.favoriteEmojis": "Emojis favoritos",
			"chart.emojisByUser": "Emojis por usuario",
			"chart.sentimentByUser": "Sentimiento por usuario",
			"chart.sentimentTimeline": "Línea de sentimiento",
			"chart.participation": "Participación (% mensajes)",
			"chart.conversationStarters": "Iniciadores de conversación",
			"chart.avgResponseTime": "Tiempo de respuesta prom.",
			"chart.avgWordsPerMessage": "Palabras por mensaje prom.",

			// Chart labels
			"chart.range": "Rango",
			"chart.last7days": "Últimos 7 días",
			"chart.last30days": "Últimos 30 días",
			"chart.last3months": "Últimos 3 meses",
			"chart.last6months": "Últimos 6 meses",
			"chart.lastYear": "Último año",
			"chart.allTime": "Todo el tiempo",
			"chart.messages": "Mensajes",
			"chart.frequency": "Frecuencia",
			"chart.sentiment": "Sentimiento",
			"chart.noMessages": "Sin mensajes en este período",
			"chart.noData": "Sin datos de sentimiento",
			"chart.unavailable": "Sentimiento no disponible (instalar vaderSentiment)",
			"chart.totalEmojis": "Total de emojis",
			"chart.participationPct": "% Participación",
			"chart.avgTime": "Tiempo prom. (min)",
			"chart.avgWords": "Palabras prom.",

			// Download buttons
			"download.json": "Descargar JSON",
			"download.png": "Descargar PNG",

			// Modal
			"modal.title": "Subir chat de WhatsApp",
			"modal.description": "Exporta tu chat sin multimedia y sube el archivo .txt.",
			"modal.fileLabel": "Archivo .txt",
			"modal.cancel": "Cancelar",
			"modal.analyze": "Analizar",

			// Language selector
			"lang.select": "Idioma",
			"lang.en": "English",
			"lang.es": "Español",
		},
	};

	const SUPPORTED_LANGUAGES = ["en", "es"];
	const DEFAULT_LANGUAGE = "en";
	const STORAGE_KEY = "whatsanalyzer-lang";

	/**
	 * Detect the user's preferred language from browser settings
	 */
	const detectSystemLanguage = () => {
		const browserLang = navigator.language || navigator.userLanguage || "";
		const langCode = browserLang.split("-")[0].toLowerCase();
		return SUPPORTED_LANGUAGES.includes(langCode) ? langCode : DEFAULT_LANGUAGE;
	};

	/**
	 * Get the current language (from storage or system detection)
	 */
	const getCurrentLanguage = () => {
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved && SUPPORTED_LANGUAGES.includes(saved)) {
			return saved;
		}
		return detectSystemLanguage();
	};

	/**
	 * Set the current language and save to storage
	 */
	const setLanguage = (lang) => {
		if (!SUPPORTED_LANGUAGES.includes(lang)) {
			lang = DEFAULT_LANGUAGE;
		}
		localStorage.setItem(STORAGE_KEY, lang);
		document.documentElement.setAttribute("lang", lang);
		applyTranslations(lang);

		// Dispatch event for other modules to react
		window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: lang } }));
	};

	/**
	 * Get a translation by key
	 */
	const t = (key, lang = null) => {
		const currentLang = lang || getCurrentLanguage();
		return translations[currentLang]?.[key] || translations[DEFAULT_LANGUAGE]?.[key] || key;
	};

	/**
	 * Apply translations to all elements with data-i18n attribute
	 */
	const applyTranslations = (lang = null) => {
		const currentLang = lang || getCurrentLanguage();

		// Update all elements with data-i18n attribute
		document.querySelectorAll("[data-i18n]").forEach((el) => {
			const key = el.getAttribute("data-i18n");
			const translation = t(key, currentLang);

			// Check if we need to update innerHTML (for elements with icons) or textContent
			if (el.hasAttribute("data-i18n-html")) {
				el.innerHTML = translation;
			} else {
				// Preserve child elements (like icons) by only updating text nodes
				const hasChildElements = Array.from(el.childNodes).some((node) => node.nodeType === Node.ELEMENT_NODE);
				if (hasChildElements) {
					// Find or create text node after icon elements
					let textNode = Array.from(el.childNodes).find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
					if (textNode) {
						textNode.textContent = " " + translation;
					} else {
						el.appendChild(document.createTextNode(" " + translation));
					}
				} else {
					el.textContent = translation;
				}
			}
		});

		// Update elements with data-i18n-placeholder attribute
		document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
			const key = el.getAttribute("data-i18n-placeholder");
			el.placeholder = t(key, currentLang);
		});

		// Update elements with data-i18n-title attribute
		document.querySelectorAll("[data-i18n-title]").forEach((el) => {
			const key = el.getAttribute("data-i18n-title");
			el.title = t(key, currentLang);
		});

		// Update elements with data-i18n-aria attribute
		document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
			const key = el.getAttribute("data-i18n-aria");
			el.setAttribute("aria-label", t(key, currentLang));
		});

		// Update the language selector to show current selection
		const langSelect = document.getElementById("languageSelect");
		if (langSelect) {
			langSelect.value = currentLang;
		}
	};

	/**
	 * Initialize language selector dropdown
	 */
	const initLanguageSelector = () => {
		const langSelect = document.getElementById("languageSelect");
		if (!langSelect) return;

		langSelect.value = getCurrentLanguage();
		langSelect.addEventListener("change", (e) => {
			setLanguage(e.target.value);
		});
	};

	/**
	 * Initialize i18n module
	 */
	const init = () => {
		const currentLang = getCurrentLanguage();
		document.documentElement.setAttribute("lang", currentLang);
		initLanguageSelector();
		applyTranslations(currentLang);
	};

	// Export to global scope
	window.i18n = {
		t,
		getCurrentLanguage,
		setLanguage,
		applyTranslations,
		init,
		SUPPORTED_LANGUAGES,
	};

	// Initialize on DOM ready
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
