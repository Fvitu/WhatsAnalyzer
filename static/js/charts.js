(() => {
	// Modern green-themed palette matching WhatsApp style
	const palette = ["#25D366", "#a78bfa", "#22d3ee", "#fbbf24", "#fb923c", "#f472b6", "#34d399", "#818cf8"];

	// i18n helper - returns translation or key if not found
	const t = (key) => window.i18n?.t(key) || key;

	const demoData = {
		total_mensajes: 420,
		participantes: ["Alex", "Sam", "Taylor"],
		mensajes_por_persona: { Alex: 180, Sam: 150, Taylor: 90 },
		total_multimedia: 32,
		lapso_tiempo: { inicio: "01-01-2024", fin: "28-02-2024", duracion: "58 days, 0:00:00" },
		mensajes_promedio_por_dia: 7.2,
		tiempo_promedio_conversacion: "24 min",
		total_emojis: 210,
		total_links: 12,
		mensajes_por_dia: {
			"2024-01-01": 12,
			"2024-01-02": 8,
			"2024-01-03": 14,
			"2024-01-04": 6,
			"2024-01-05": 9,
			"2024-02-01": 11,
			"2024-02-10": 7,
			"2024-02-15": 13,
			"2024-02-20": 10,
			"2024-02-28": 16,
		},
		mensajes_por_hora: {
			"00": 3,
			"01": 1,
			"02": 0,
			"03": 0,
			"04": 0,
			"05": 0,
			"06": 1,
			"07": 2,
			"08": 8,
			"09": 10,
			10: 14,
			11: 12,
			12: 18,
			13: 20,
			14: 22,
			15: 24,
			16: 28,
			17: 32,
			18: 36,
			19: 30,
			20: 24,
			21: 18,
			22: 12,
			23: 8,
		},
		palabras_mas_utilizadas_nlp: [
			["meet", 22],
			["thank", 16],
			["great", 14],
			["call", 13],
			["tomorrow", 12],
			["sure", 10],
			["today", 9],
			["share", 8],
			["plan", 7],
			["time", 6],
		],
		palabras_mas_utilizadas: [
			["meet", 22],
			["thank", 16],
			["great", 14],
			["call", 13],
			["tomorrow", 12],
			["sure", 10],
			["today", 9],
			["share", 8],
			["plan", 7],
			["time", 6],
		],
		sentimiento_por_persona: {
			Alex: { promedio_compound: 0.21, positive: 80, neutral: 70, negative: 30, total: 180 },
			Sam: { promedio_compound: 0.05, positive: 55, neutral: 70, negative: 25, total: 150 },
			Taylor: { promedio_compound: -0.08, positive: 25, neutral: 45, negative: 20, total: 90 },
		},
		sentimiento_por_dia: {
			"2024-01-01": 0.02,
			"2024-01-02": 0.05,
			"2024-01-03": -0.01,
			"2024-01-04": 0.12,
			"2024-01-05": 0.08,
			"2024-02-01": 0.04,
			"2024-02-10": -0.06,
			"2024-02-15": 0.1,
			"2024-02-20": 0.0,
			"2024-02-28": 0.14,
		},
		sentimiento_global: { promedio_compound: 0.07, positive: 160, neutral: 185, negative: 75, total: 420, engine: "vader" },
		emojis_mas_utilizados: [
			["😂", 30],
			["👍", 22],
			["❤️", 18],
			["😊", 15],
			["🔥", 14],
			["🎉", 12],
			["🙏", 11],
			["🥳", 9],
			["😉", 8],
			["😅", 7],
		],
		emojis_por_persona: {
			Alex: [
				["😂", 12],
				["👍", 8],
				["❤️", 6],
			],
			Sam: [
				["😂", 9],
				["🔥", 7],
				["🎉", 5],
			],
			Taylor: [
				["😊", 6],
				["🙏", 4],
				["😉", 3],
			],
		},
		iniciadores_de_conversacion: { iniciadores: {}, porcentajes: {}, total_conversaciones: 0 },
	};

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

		try {
			const canvas = await html2canvas(statsContent, {
				backgroundColor: document.documentElement.getAttribute("data-bs-theme") === "dark" ? "#212529" : "#ffffff",
				scale: 2,
				useCORS: true,
				logging: false,
			});
			const url = canvas.toDataURL("image/png");
			const a = document.createElement("a");
			a.href = url;
			a.download = `whatsapp-stats-${new Date().toISOString().slice(0, 10)}.png`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		} catch (err) {
			console.warn("Failed to capture screenshot", err);
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
		if (demoBtn) demoBtn.addEventListener("click", () => loadData(demoData));

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
