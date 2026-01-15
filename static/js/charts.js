(() => {
	// Modern green-themed palette matching WhatsApp style
	const palette = ["#25D366", "#a78bfa", "#22d3ee", "#fbbf24", "#fb923c", "#f472b6", "#34d399", "#818cf8"];

	// i18n helper - returns translation or key if not found
	const t = (key) => window.i18n?.t(key) || key;

	// Demo chat sample (WhatsApp export format).
	// This is a real-style chat sample (no precomputed statistics). Use it to
	// download and upload to the backend for analysis.
	const demoChat = `7/01/22, 21:05 - Grupo: Ana creó el grupo "Plan Evento"
7/01/22, 21:06 - Ana: Bienvenidos al grupo! Aquí iremos dejando avisos y material.
7/01/22, 21:07 - Carlos: Gracias! 👋
7/02/22, 08:00 - Marta: Buen día a todos ☀️
7/02/22, 08:05 - Luis: <Media omitted>
7/02/22, 08:06 - Elena: Wow, buena foto 🙌
7/03/22, 12:10 - Carlos: ¿Alguien trajo la lista de tareas?
7/03/22, 12:11 - Ana: Sí, la subí al drive: https://example.com/plan-evento (revisen permisos)
7/03/22, 12:12 - Marta: Perfecto, lo veo ahora
7/04/22, 18:20 - Luis: Atención: cambio de horario a las 20:00
7/04/22, 18:21 - Carlos: Ok, lo tengo anotado
7/05/22, 22:04 - Ana: <Media omitted>
7/05/22, 22:14 - Carlos: Oaaa
7/05/22, 22:14 - Carlos: Dale
7/05/22, 22:14 - Carlos: 👍👍
7/06/22, 09:30 - Marta: Enlace útil sobre logística: https://logistica.example.org/info
7/06/22, 09:31 - Ana: Gracias! lo reviso
7/07/22, 14:00 - Elena: ¿Quién puede traer el equipo de sonido?
7/07/22, 14:02 - Luis: Yo puedo, lo llevo yo
7/08/22, 11:15 - Ana: Eu porque no salen?
7/08/22, 11:17 - Carlos: Estamos haciendo algo de catequesis
7/08/22, 11:18 - Ana: Ah, entendido. Gracias!
7/08/22, 11:20 - Marta: Hola a todos, llego un poco tarde
7/08/22, 11:21 - Carlos: Bienvenido!
7/08/22, 11:22 - Marta: Gracias, subo las fotos luego
7/08/22, 11:23 - Ana: Perfecto, esperamos
7/09/22, 16:45 - Carlos: Atención: se eliminó un mensaje
7/09/22, 16:46 - Carlos: This message was deleted
7/10/22, 09:05 - Carlos: Recuerden la reunión a las 19:00
7/10/22, 09:06 - Marta: Listo, me anoto
7/10/22, 19:01 - Luis: Estoy muy molesto con cómo se organizó todo; fue un desastre y no pienso volver a ayudar si sigue así 😡😤
7/11/22, 18:20 - Carlos: Aquí va un mensaje largo que ocupa varias líneas:
La segunda línea del mismo mensaje con más contexto y detalles técnicos que deberían
ser interpretados por el parser y unirlas en una sola entrada de mensaje.
7/11/22, 18:25 - Elena: Excelente explicación, gracias por el detalle.
7/12/22, 20:30 - Ana: Qué tal estuvo hoy?
7/12/22, 20:31 - Carlos: Muy bien, hubo mucha participación
7/12/22, 20:33 - Marta: Me gustó la dinámica
7/13/22, 08:45 - Ana: Gracias a todos, buen día
7/13/22, 08:46 - Carlos: Buen día ☀️
7/13/22, 08:47 - Marta: Buen día! 😊
7/14/22, 10:00 - Luis: Compartí ubicación: https://www.google.com/maps/place/Some+Place
7/14/22, 10:01 - Ana: Contact card omitted
7/15/22, 12:00 - Carlos: @Elena puedes confirmar la lista de invitados?
7/15/22, 12:05 - Elena: Confirmado. Lista actualizada.
7/16/22, 21:30 - Marta: Estoy muy contento con cómo salió todo 🎉🎉
7/16/22, 21:31 - Ana: Estoy muy decepcionado con cómo salió todo. Fue un desastre y no siento que se haya coordinado nada. No volveré a participar si esto sigue así.
7/17/22, 07:00 - Carlos: Hola, recordatorio: encuesta pendiente (llenar en https://survey.example)
7/17/22, 07:05 - Elena: Ya la completé
7/18/22, 22:10 - Luis: Cambio de número: Luis cambió su número de teléfono
7/19/22, 09:00 - Ana: ¿Alguien tiene backup de las fotos? Las necesito para la próxima publicación
7/19/22, 09:02 - Ana: Además, honestamente estoy muy molesto por la organización, muchas cosas fallaron y eso me frustró.
7/19/22, 09:10 - Marta: Yo las subo en un rato
7/20/22, 11:45 - Carlos: Último mensaje de prueba: emojis 👍😂😅❤️🔥🙏🥳😉
7/20/22, 11:46 - Ana: Fin del chat de prueba.`;

	const charts = {};

	const formatNumber = (value, digits = 0) =>
		Number.isFinite(value) ? value.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits }) : "--";

	const setText = (id, value) => {
		const node = document.getElementById(id);
		if (!node) return;
		node.textContent = value ?? "--";
	};

	const buildChart = (id, config) => {
		const canvas = document.getElementById(id);
		if (!canvas || !canvas.getContext) return;
		if (charts[id]) charts[id].destroy();
		charts[id] = new Chart(canvas.getContext("2d"), config);
	};

	const clearChart = (id) => {
		if (charts[id]) {
			charts[id].destroy();
			delete charts[id];
		}
	};

	const setCanvasHeight = (id, numBars) => {
		const canvas = document.getElementById(id);
		if (!canvas) return;
		// Dynamic height: 40px per bar (min 180px, max 600px)
		const height = Math.max(180, Math.min(600, numBars * 40));
		canvas.height = height;
		canvas.style.height = `${height}px`;
	};

	const sumTupleList = (items = []) => items.reduce((acc, item) => acc + (Number(item?.[1]) || 0), 0);

	const normalizeTuples = (items = [], limit = 40) =>
		items.filter((pair) => Array.isArray(pair) && pair.length >= 2 && pair[0] !== undefined && pair[0] !== null && Number(pair[1]) > 0).slice(0, limit);

	const hasWordCloud = () => !!Chart?.registry?.controllers?.get("wordCloud") || !!Chart?.registry?.controllers?.get("wordcloud");

	const parseDate = (str) => {
		// Dates come in ISO format YYYY-MM-DD from backend
		const d = new Date(str + "T00:00:00");
		return Number.isNaN(d.getTime()) ? null : d;
	};

	const filterMessagesByRange = (mensajesPorDia = {}, range = "all") => {
		const entries = Object.entries(mensajesPorDia)
			.map(([label, val]) => ({ date: parseDate(label), label, value: Number(val) || 0 }))
			.filter((x) => x.date);

		if (!entries.length) return { labels: [], data: [] };

		entries.sort((a, b) => a.date - b.date);

		// Use today's date as reference for filtering
		const today = new Date();
		today.setHours(0, 0, 0, 0);

		const cutoff = (() => {
			const d = new Date(today);
			switch (range) {
				case "7d":
					d.setDate(d.getDate() - 6);
					return d;
				case "30d":
					d.setDate(d.getDate() - 29);
					return d;
				case "3m":
					d.setMonth(d.getMonth() - 3);
					return d;
				case "6m":
					d.setMonth(d.getMonth() - 6);
					return d;
				case "1y":
					d.setFullYear(d.getFullYear() - 1);
					return d;
				default:
					return null;
			}
		})();

		const filtered = cutoff ? entries.filter((e) => e.date >= cutoff && e.date <= today) : entries;
		return {
			labels: filtered.map((e) => e.label),
			data: filtered.map((e) => e.value),
		};
	};

	const updateStats = (stats) => {
		setText("total-messages-value", formatNumber(Number(stats.total_mensajes)));
		setText("participants-value", formatNumber((stats.participantes || []).length));
		setText("media-shared-value", formatNumber(Number(stats.total_multimedia)));

		const lapso = stats.lapso_tiempo || {};
		const range = lapso.inicio && lapso.fin ? `${lapso.inicio} - ${lapso.fin}` : "--";
		setText("time-span-value", range);

		const totalDias = Number(lapso.total_dias);
		if (totalDias > 0) {
			const dayWord = totalDias === 1 ? t("stats.day") : t("stats.days");
			setText("total-dias-value", `${totalDias} ${dayWord}`);
		} else {
			setText("total-dias-value", "");
		}

		// Active days (days with at least one message)
		const diasActivos = Number(stats.dias_activos) || 0;
		setText("active-days-value", formatNumber(diasActivos));
		if (totalDias > 0 && diasActivos > 0) {
			const pct = ((diasActivos / totalDias) * 100).toFixed(0);
			setText("active-days-detail", `${pct}% ${t("stats.ofTotalDays")}`);
		}

		setText("avg-messages-value", formatNumber(Number(stats.mensajes_promedio_por_dia), 1));
		setText("emoji-count-value", formatNumber(Number(stats.total_emojis)));

		// Hours chatting
		const horasChat = Number(stats.horas_totales_chat) || 0;
		if (horasChat >= 24) {
			const days = Math.floor(horasChat / 24);
			const hours = Math.round(horasChat % 24);
			setText("hours-chatting-value", `${days}d ${hours}h`);
		} else {
			setText("hours-chatting-value", `${horasChat.toFixed(1)}h`);
		}
	};

	const renderCharts = (stats) => {
		const safeRender = (fn) => {
			try {
				fn();
			} catch (err) {
				console.warn("Chart render failed", err);
			}
		};

		const mensajesPorDia = stats.mensajes_por_dia || {};
		const rangeSelect = document.getElementById("message-range");
		const renderMessages = (range = "all") => {
			const { labels, data } = filterMessagesByRange(mensajesPorDia, range);
			// Always render the chart, even if empty, to clear previous data
			safeRender(() =>
				buildChart("messageActivityChart", {
					type: "bar",
					data: {
						labels,
						datasets: [
							{
								label: t("chart.messages"),
								data,
								backgroundColor: palette[0],
								borderRadius: 4,
							},
						],
					},
					options: {
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { display: false },
							// Show message when no data
							...(labels.length === 0 && {
								title: {
									display: true,
									text: t("chart.noMessages"),
									font: { size: 14 },
								},
							}),
						},
						scales: { y: { beginAtZero: true } },
					},
				})
			);
		};

		if (Object.keys(mensajesPorDia).length) {
			renderMessages(rangeSelect?.value || "all");
			if (rangeSelect) {
				rangeSelect.addEventListener("change", (e) => renderMessages(e.target.value));
			}
		}

		const mensajesPorPersona = stats.mensajes_por_persona || {};
		const participantLabels = Object.keys(mensajesPorPersona);
		const participantData = participantLabels.map((k) => Number(mensajesPorPersona[k]));
		if (participantLabels.length) {
			safeRender(() =>
				buildChart("participantChart", {
					type: "doughnut",
					data: {
						labels: participantLabels,
						datasets: [
							{
								data: participantData,
								backgroundColor: participantLabels.map((_, idx) => palette[idx % palette.length]),
							},
						],
					},
					options: { responsive: true, maintainAspectRatio: false },
				})
			);
		}

		const mensajesPorHora = stats.mensajes_por_hora || {};
		const hourLabels = Array.from({ length: 24 }, (_, h) => h.toString().padStart(2, "0"));
		const hourData = hourLabels.map((h) => Number(mensajesPorHora[h]) || 0);
		safeRender(() =>
			buildChart("hourActivityChart", {
				type: "bar",
				data: {
					labels: hourLabels,
					datasets: [
						{
							label: t("chart.messages"),
							data: hourData,
							backgroundColor: palette[3],
							borderRadius: 3,
						},
					],
				},
				options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
			})
		);

		const palabrasSource = stats.palabras_mas_utilizadas_nlp || stats.palabras_mas_utilizadas || [];
		const palabras = normalizeTuples(palabrasSource, 20);

		// Use bar chart for words - more reliable and no warnings
		if (palabras.length) {
			const items = palabras.slice(0, 10).map(([w, c]) => ({ word: String(w), weight: Number(c) || 0 }));
			safeRender(() =>
				buildChart("wordCloudChart", {
					type: "bar",
					data: {
						labels: items.map((i) => i.word),
						datasets: [
							{
								label: t("chart.frequency"),
								data: items.map((i) => i.weight),
								backgroundColor: palette[0],
								borderRadius: 4,
							},
						],
					},
					options: {
						indexAxis: "y",
						responsive: true,
						maintainAspectRatio: false,
						plugins: { legend: { display: false } },
						scales: {
							x: { beginAtZero: true, ticks: { precision: 0 } },
						},
					},
				})
			);
		} else {
			clearChart("wordCloudChart");
		}

		// --- Sentiment charts ---
		const sentGlobal = stats.sentimiento_global || {};
		const sentimentEnabled = sentGlobal.engine && sentGlobal.engine !== "disabled";
		const sentimentHint = sentimentEnabled ? t("chart.noData") : t("chart.unavailable");

		const sentByUser = stats.sentimiento_por_persona || {};
		let sentUsers = Object.keys(sentByUser);
		if (sentUsers.length) {
			// Sort users by sentiment: most positive → most negative
			sentUsers = sentUsers.sort((a, b) => {
				const valA = Number(sentByUser[a]?.promedio_compound) || 0;
				const valB = Number(sentByUser[b]?.promedio_compound) || 0;
				return valB - valA;
			});
			const sentVals = sentUsers.map((u) => Number(sentByUser[u]?.promedio_compound) || 0);
			const sentColors = sentVals.map((v) => (v >= 0.05 ? palette[0] : v <= -0.05 ? "#ef4444" : "#94a3b8"));
			setCanvasHeight("sentimentByUserChart", sentUsers.length);
			safeRender(() =>
				buildChart("sentimentByUserChart", {
					type: "bar",
					data: {
						labels: sentUsers,
						datasets: [
							{
								label: t("chart.sentiment"),
								data: sentVals,
								backgroundColor: sentColors,
								borderRadius: 4,
							},
						],
					},
					options: {
						indexAxis: "y",
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { display: false },
							tooltip: {
								callbacks: {
									label: (ctx) => {
										const user = sentUsers[ctx.dataIndex];
										const info = sentByUser[user];
										if (!info) return "";
										const total = info.total || 1;
										const posPct = ((info.positive / total) * 100).toFixed(0);
										const neuPct = ((info.neutral / total) * 100).toFixed(0);
										const negPct = ((info.negative / total) * 100).toFixed(0);
										return [
											`Avg: ${Number(info.promedio_compound).toFixed(3)}`,
											`Positive: ${posPct}% (${info.positive})`,
											`Neutral: ${neuPct}% (${info.neutral})`,
											`Negative: ${negPct}% (${info.negative})`,
										];
									},
								},
							},
						},
						scales: {
							x: {
								beginAtZero: true,
								min: -1,
								max: 1,
								ticks: { callback: (v) => Number(v).toFixed(1) },
							},
						},
					},
				})
			);
		} else {
			// Render an empty chart with a title so the section doesn't look broken
			safeRender(() =>
				buildChart("sentimentByUserChart", {
					type: "bar",
					data: { labels: [], datasets: [{ data: [] }] },
					options: {
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { display: false },
							title: { display: true, text: sentimentHint, font: { size: 14 } },
						},
					},
				})
			);
		}

		const sentByDay = stats.sentimiento_por_dia || {};
		const sentDayEntries = Object.entries(sentByDay)
			.map(([d, v]) => ({ date: parseDate(d), label: d, value: Number(v) || 0 }))
			.filter((x) => x.date)
			.sort((a, b) => a.date - b.date);
		if (sentDayEntries.length) {
			safeRender(() =>
				buildChart("sentimentTimelineChart", {
					type: "line",
					data: {
						labels: sentDayEntries.map((e) => e.label),
						datasets: [
							{
								label: t("chart.sentiment"),
								data: sentDayEntries.map((e) => e.value),
								borderColor: palette[0],
								backgroundColor: "rgba(37, 211, 102, 0.15)",
								tension: 0.25,
								fill: true,
								pointRadius: 0,
							},
						],
					},
					options: {
						responsive: true,
						maintainAspectRatio: false,
						plugins: { legend: { display: false } },
						scales: {
							y: {
								min: -1,
								max: 1,
								ticks: { callback: (v) => Number(v).toFixed(1) },
							},
						},
					},
				})
			);
		} else {
			safeRender(() =>
				buildChart("sentimentTimelineChart", {
					type: "line",
					data: { labels: [], datasets: [{ data: [] }] },
					options: {
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { display: false },
							title: { display: true, text: sentimentHint, font: { size: 14 } },
						},
					},
				})
			);
		}

		const emojis = normalizeTuples(stats.emojis_mas_utilizados || [], 20);
		if (emojis.length) {
			safeRender(() =>
				buildChart("mostUsedEmojisChart", {
					type: "bar",
					data: {
						labels: emojis.map(([e]) => String(e)),
						datasets: [
							{
								data: emojis.map(([, c]) => Number(c) || 0),
								backgroundColor: palette[2],
								borderRadius: 4,
							},
						],
					},
					options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
				})
			);
		}

		const emojisPorPersona = stats.emojis_por_persona || {};
		const emojiUserLabels = Object.keys(emojisPorPersona);
		const emojiUserData = emojiUserLabels.map((name) => sumTupleList(normalizeTuples(emojisPorPersona[name] || [])));
		if (emojiUserLabels.length) {
			setCanvasHeight("emojiUsageByUserChart", emojiUserLabels.length);
			safeRender(() =>
				buildChart("emojiUsageByUserChart", {
					type: "bar",
					data: {
						labels: emojiUserLabels,
						datasets: [
							{
								data: emojiUserData,
								backgroundColor: emojiUserLabels.map((_, idx) => palette[idx % palette.length]),
								borderRadius: 4,
							},
						],
					},
					options: {
						indexAxis: "y",
						responsive: true,
						maintainAspectRatio: false,
						plugins: { legend: { display: false } },
					},
				})
			);
		}

		const totalMensajes = Number(stats.total_mensajes) || 0;
		if (participantLabels.length && totalMensajes > 0) {
			setCanvasHeight("responseRateChart", participantLabels.length);
			safeRender(() =>
				buildChart("responseRateChart", {
					type: "bar",
					data: {
						labels: participantLabels,
						datasets: [
							{
								data: participantLabels.map((name) => {
									const val = ((Number(mensajesPorPersona[name]) || 0) * 100) / totalMensajes;
									return Number.isFinite(val) ? Number(val.toFixed(1)) : 0;
								}),
								backgroundColor: participantLabels.map((_, idx) => palette[idx % palette.length]),
								borderRadius: 4,
							},
						],
					},
					options: {
						indexAxis: "y",
						responsive: true,
						maintainAspectRatio: false,
						plugins: { legend: { display: false } },
						scales: {
							x: {
								beginAtZero: true,
								max: 100,
								ticks: { callback: (val) => `${val}%` },
							},
						},
					},
				})
			);
		}

		// Conversation starters podium
		const iniciadores = stats.iniciadores_de_conversacion || {};
		const podio = iniciadores.podio || [];
		const podiumContainer = document.getElementById("conversation-starters-podium");
		if (podiumContainer && podio.length) {
			const medals = ["🥇", "🥈", "🥉"];
			const html = podio
				.slice(0, 5)
				.map(([name, count], idx) => {
					const pct = iniciadores.porcentajes?.[name] || "0%";
					const medal = medals[idx] || `#${idx + 1}`;
					const barWidth = podio[0][1] > 0 ? (count / podio[0][1]) * 100 : 0;
					return `
					<div class="d-flex align-items-center gap-3">
						<span class="fs-4">${medal}</span>
						<div class="flex-grow-1">
							<div class="d-flex justify-content-between mb-1">
								<span class="fw-medium">${name}</span>
								<span class="text-muted small">${count} convs (${pct})</span>
							</div>
							<div class="progress" style="height: 8px;">
								<div class="progress-bar" role="progressbar" style="width: ${barWidth}%; background-color: ${palette[idx % palette.length]};"></div>
							</div>
						</div>
					</div>
				`;
				})
				.join("");
			podiumContainer.innerHTML = html;
		}

		// Response time by person chart
		const tiempoRespuesta = stats.tiempo_respuesta_por_persona || {};
		const respLabels = Object.keys(tiempoRespuesta);
		if (respLabels.length) {
			const respData = respLabels.map((name) => {
				const seg = tiempoRespuesta[name]?.promedio_segundos || 0;
				return Math.round(seg / 60); // Convert to minutes
			});
			setCanvasHeight("responseTimeChart", respLabels.length);
			safeRender(() =>
				buildChart("responseTimeChart", {
					type: "bar",
					data: {
						labels: respLabels,
						datasets: [
							{
								label: t("chart.avgTime"),
								data: respData,
								backgroundColor: respLabels.map((_, idx) => palette[idx % palette.length]),
								borderRadius: 4,
							},
						],
					},
					options: {
						indexAxis: "y",
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: { display: false },
							tooltip: {
								callbacks: {
									label: (ctx) => {
										const name = respLabels[ctx.dataIndex];
										const info = tiempoRespuesta[name];
										return info ? `${info.promedio_formateado} (${info.total_respuestas} responses)` : "";
									},
								},
							},
						},
						scales: {
							x: {
								beginAtZero: true,
								ticks: { callback: (val) => `${val} min` },
							},
						},
					},
				})
			);
		}

		// Words per message by person chart
		const palabrasPorPersona = stats.palabras_promedio_por_persona || {};
		const wordsLabels = Object.keys(palabrasPorPersona);
		if (wordsLabels.length) {
			const wordsData = wordsLabels.map((name) => palabrasPorPersona[name] || 0);
			setCanvasHeight("wordsPerMessageChart", wordsLabels.length);
			safeRender(() =>
				buildChart("wordsPerMessageChart", {
					type: "bar",
					data: {
						labels: wordsLabels,
						datasets: [
							{
								label: t("chart.avgWords"),
								data: wordsData,
								backgroundColor: wordsLabels.map((_, idx) => palette[idx % palette.length]),
								borderRadius: 4,
							},
						],
					},
					options: {
						indexAxis: "y",
						responsive: true,
						maintainAspectRatio: false,
						plugins: { legend: { display: false } },
						scales: {
							x: {
								beginAtZero: true,
								ticks: { callback: (val) => `${val} words` },
							},
						},
					},
				})
			);
		}
	};

	const toggleTheme = () => {
		const switcher = document.getElementById("darkModeSwitch");
		const root = document.documentElement;
		if (!switcher) return;

		const saved = localStorage.getItem("theme");
		const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
		const initial = saved || (prefersDark ? "dark" : "light");
		root.setAttribute("data-bs-theme", initial);
		switcher.checked = initial === "dark";

		switcher.addEventListener("change", () => {
			const mode = switcher.checked ? "dark" : "light";
			root.setAttribute("data-bs-theme", mode);
			localStorage.setItem("theme", mode);
		});
	};

	const readEmbeddedData = () => {
		const el = document.getElementById("chat-data");
		if (!el) return null;
		try {
			const text = el.textContent?.trim() || "null";
			return JSON.parse(text);
		} catch (err) {
			console.warn("Could not parse chat data", err);
			return null;
		}
	};

	const isValidStats = (stats) => stats && typeof stats === "object" && Object.keys(stats).length > 0;

	const showStats = () => {
		document.getElementById("empty-state")?.classList.add("d-none");
		const statsContent = document.getElementById("stats-content");
		if (statsContent) {
			statsContent.classList.remove("d-none");
			// Reset animations for new data
			const animatedElements = statsContent.querySelectorAll(".animate-in");
			animatedElements.forEach((el) => {
				el.classList.remove("animate-in-active");
				el.style.opacity = "0";
				el.style.transform = "translateY(20px)";
			});
			// Setup scroll observer for new elements
			setTimeout(() => setupScrollAnimations(), 50);
		}
	};

	const showEmpty = () => {
		document.getElementById("stats-content")?.classList.add("d-none");
		document.getElementById("empty-state")?.classList.remove("d-none");
	};

	let currentStats = null;

	const loadData = (stats) => {
		if (!isValidStats(stats)) {
			showEmpty();
			return;
		}

		currentStats = stats;
		showStats();
		updateStats(stats);
		renderCharts(stats);
	};

	const downloadJSON = () => {
		if (!currentStats) return;
		const dataStr = JSON.stringify(currentStats, null, 2);
		const blob = new Blob([dataStr], { type: "application/json" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `whatsapp-stats-${new Date().toISOString().slice(0, 10)}.json`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	};

	const downloadPNG = async () => {
		const statsContent = document.getElementById("stats-content");
		if (!statsContent || typeof html2canvas === "undefined") return;

		// Show loading state on button
		const btn = document.getElementById("download-png-btn");
		const originalBtnHTML = btn ? btn.innerHTML : "";
		if (btn) {
			btn.disabled = true;
			btn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i><span>Generating...</span>';
		}

		const isDark = document.documentElement.getAttribute("data-bs-theme") === "dark";
		const bgColor = isDark ? "#0d1117" : "#ffffff";
		const cardBg = isDark ? "#1c2128" : "#ffffff";

		// Store original scroll position
		const originalScrollTop = window.scrollY;

		// Collect elements to modify
		const animatedElements = statsContent.querySelectorAll(".animate-in");
		const allCards = statsContent.querySelectorAll(".stat-card, .card");
		const downloadSection = statsContent.querySelector(".download-section");

		try {
			// Hide download section from capture
			if (downloadSection) downloadSection.style.display = "none";

			// Force all animations to complete
			animatedElements.forEach((el) => {
				el.classList.add("animate-in-active");
				el.style.cssText += "opacity: 1 !important; transform: none !important;";
			});

			// Force solid backgrounds on all cards
			allCards.forEach((card) => {
				card.style.cssText += `background: ${cardBg} !important; background-image: none !important; opacity: 1 !important;`;
			});

			// Scroll to ensure all content is rendered
			window.scrollTo(0, 0);
			await new Promise((r) => setTimeout(r, 50));
			window.scrollTo(0, document.body.scrollHeight);
			await new Promise((r) => setTimeout(r, 100));
			window.scrollTo(0, 0);
			await new Promise((r) => setTimeout(r, 150));

			// Update all charts
			if (window.Chart) {
				Object.values(Chart.instances).forEach((chart) => {
					chart?.resize?.();
					chart?.update?.("none");
				});
				await new Promise((r) => setTimeout(r, 200));
			}

			// Capture with html2canvas
			const canvas = await html2canvas(statsContent, {
				backgroundColor: bgColor,
				scale: 2,
				useCORS: true,
				allowTaint: true,
				logging: false,
				imageTimeout: 0,
				onclone: (clonedDoc) => {
					// Apply styles in cloned document for consistent capture
					const clonedContent = clonedDoc.getElementById("stats-content");
					if (clonedContent) {
						// Hide download section in clone
						const clonedDownload = clonedContent.querySelector(".download-section");
						if (clonedDownload) clonedDownload.style.display = "none";

						// Force all elements visible in clone
						clonedContent.querySelectorAll(".animate-in").forEach((el) => {
							el.style.cssText += "opacity: 1 !important; transform: none !important;";
						});

						// Force card backgrounds in clone
						clonedContent.querySelectorAll(".stat-card, .card").forEach((card) => {
							card.style.cssText += `background: ${cardBg} !important; background-image: none !important; opacity: 1 !important;`;
						});
					}
				},
			});

			// Download the image
			const link = document.createElement("a");
			link.download = `whatsapp-stats-${new Date().toISOString().slice(0, 10)}.png`;
			link.href = canvas.toDataURL("image/png", 1.0);
			link.click();
		} catch (err) {
			console.error("Screenshot error:", err);
			alert("Error generating image. Please try again.");
		} finally {
			// Restore download section
			if (downloadSection) downloadSection.style.display = "";

			// Restore animated elements
			animatedElements.forEach((el) => {
				el.style.opacity = "";
				el.style.transform = "";
			});

			// Restore card styles
			allCards.forEach((card) => {
				card.style.background = "";
				card.style.backgroundImage = "";
				card.style.opacity = "";
			});

			// Restore scroll position
			window.scrollTo(0, originalScrollTop);

			// Restore button
			if (btn) {
				btn.disabled = false;
				btn.innerHTML = originalBtnHTML;
			}
		}
	};

	// Intersection Observer for scroll-based animations
	const setupScrollAnimations = () => {
		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						entry.target.classList.add("animate-in-active");
						observer.unobserve(entry.target);
					}
				});
			},
			{
				threshold: 0.05,
				rootMargin: "0px 0px 100px 0px",
			}
		);

		document.querySelectorAll(".animate-in").forEach((el) => {
			observer.observe(el);
		});
	};

	document.addEventListener("DOMContentLoaded", () => {
		toggleTheme();
		setupScrollAnimations();

		const demoBtn = document.getElementById("use-demo-btn");
		if (demoBtn)
			demoBtn.addEventListener("click", async () => {
				// Send the demo chat directly to the backend for analysis (user never sees raw chat)
				try {
					const form = new FormData();
					const blob = new Blob([demoChat], { type: "text/plain;charset=utf-8" });
					// Append as a file input named 'chatFile' (matches backend expectation)
					form.append("chatFile", blob, `demo-whatsapp-chat-${new Date().toISOString().slice(0, 10)}.txt`);

					// Try to include CSRF token if present in page (upload modal form)
					const csrfInput = document.querySelector('input[name="csrf_token"]');
					if (csrfInput && csrfInput.value) {
						form.append("csrf_token", csrfInput.value);
					}

					const resp = await fetch(window.location.pathname, {
						method: "POST",
						body: form,
						credentials: "same-origin",
					});

					if (resp.ok) {
						const html = await resp.text();
						// Replace the current document with server's response so charts update
						document.open();
						document.write(html);
						document.close();
					} else {
						// On failure, open upload modal as fallback
						const uploadModal = new bootstrap.Modal(document.getElementById("uploadModal"));
						uploadModal.show();
					}
				} catch (err) {
					const uploadModal = new bootstrap.Modal(document.getElementById("uploadModal"));
					uploadModal.show();
				}
			});

		const downloadJsonBtn = document.getElementById("download-json-btn");
		if (downloadJsonBtn) downloadJsonBtn.addEventListener("click", downloadJSON);

		const downloadPngBtn = document.getElementById("download-png-btn");
		if (downloadPngBtn) downloadPngBtn.addEventListener("click", downloadPNG);

		const embedded = readEmbeddedData();
		if (isValidStats(embedded)) loadData(embedded);
		else showEmpty();

		// Re-render charts and update stats when language changes
		window.addEventListener("languageChanged", () => {
			if (currentStats) {
				updateStats(currentStats);
				renderCharts(currentStats);
			}
		});
	});
})();
