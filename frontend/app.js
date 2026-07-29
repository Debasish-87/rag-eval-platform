/* ---------------------------------------------------------------
   RAG Evaluation Platform — dashboard
   Talks to the FastAPI backend (app/main.py). All state is fetched
   live; no build step, no framework.
----------------------------------------------------------------*/

const METRIC_GROUPS = {
  retrieval: ["precision@2", "recall@2", "mrr", "map@2", "ndcg@2", "hit_rate"],
  generation: ["faithfulness", "correctness", "semantic_similarity"],
  judge: ["llm_faithfulness", "answer_relevance", "hallucination"],
};

const GROUP_COLOR = {
  retrieval: "#f5a524",
  generation: "#35d0b8",
  judge: "#9b8cff",
};

const LOWER_IS_BETTER = new Set(["hallucination"]);

function metricGroup(name) {
  for (const [group, names] of Object.entries(METRIC_GROUPS)) {
    if (names.includes(name)) return group;
  }
  return "generation";
}

function scoreClass(name, value) {
  const good = LOWER_IS_BETTER.has(name) ? value <= 0.25 : value >= 0.75;
  const bad = LOWER_IS_BETTER.has(name) ? value >= 0.6 : value < 0.4;
  if (good) return "metric-chip--good";
  if (bad) return "metric-chip--bad";
  return "metric-chip--warn";
}

function fmtScore(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "\u2014";
  return Number(value).toFixed(4);
}

function fmtPct(value) {
  if (value === null || value === undefined) return "\u2014";
  return `${Math.round(value * 100)}%`;
}

// ---------------- State ----------------

const state = {
  apiBase: localStorage.getItem("ragEvalApiBase") || "http://127.0.0.1:8000",
  benchmarks: [],
  selectedBenchmarkId: null,
  charts: {},
  timer: null,
};

const el = (id) => document.getElementById(id);

// ---------------- Networking ----------------

async function apiGet(path) {
  const url = `${state.apiBase.replace(/\/$/, "")}${path}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${path}`);
  return res.json();
}

function setStatus(mode, label) {
  const pill = el("apiStatus");
  pill.className = `status-pill status-${mode}`;
  pill.querySelector(".status-label").textContent = label;
}

// ---------------- Renderers ----------------

function renderStats(summary) {
  el("statProjects").textContent = summary.projects;
  el("statDatasets").textContent = summary.datasets;
  el("statExperiments").textContent = summary.experiments;
  el("statBenchmarks").textContent = summary.benchmarks;
  el("statEvaluations").textContent = summary.evaluations;
  el("statAverage").textContent = fmtScore(summary.average_score);
}

function renderLeaderboard(rows) {
  const body = el("leaderboardBody");

  if (!rows.length) {
    body.innerHTML = `<tr class="empty-row"><td colspan="6">No benchmark runs yet. Run: python scripts/run_evaluation.py</td></tr>`;
    return;
  }

  body.innerHTML = rows
    .map((r) => {
      const rankClass = r.rank === 1 ? "rank-cell rank-cell--top" : "rank-cell";
      const rankLabel = r.rank === 1 ? `#1` : `#${r.rank}`;
      return `
        <tr>
          <td class="${rankClass}">${rankLabel}</td>
          <td>${escapeHtml(r.experiment)}</td>
          <td class="mono">${escapeHtml(r.benchmark)}</td>
          <td><span class="badge badge--${r.status}">${escapeHtml(r.status)}</span></td>
          <td class="mono">${r.evaluations}</td>
          <td class="score-cell">${fmtScore(r.overall_score)}</td>
        </tr>`;
    })
    .join("");
}

function renderComparisonChart(rows) {
  const ctx = el("comparisonChart");
  const labels = rows.map((r) => `${r.experiment} · ${r.benchmark.replace("benchmark-", "")}`);
  const data = rows.map((r) => r.overall_score);

  if (state.charts.comparison) state.charts.comparison.destroy();

  state.charts.comparison = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Overall score",
          data,
          backgroundColor: "#f5a52488",
          borderColor: "#f5a524",
          borderWidth: 1.5,
          borderRadius: 4,
          maxBarThickness: 34,
        },
      ],
    },
    options: baseChartOptions({ max: 1 }),
  });
}

function renderMetricChart(metricAverages) {
  const ctx = el("metricChart");
  const names = Object.keys(metricAverages);
  const colors = names.map((n) => GROUP_COLOR[metricGroup(n)]);

  if (state.charts.metric) state.charts.metric.destroy();

  state.charts.metric = new Chart(ctx, {
    type: "bar",
    data: {
      labels: names,
      datasets: [
        {
          label: "Average score",
          data: names.map((n) => metricAverages[n]),
          backgroundColor: colors.map((c) => c + "aa"),
          borderColor: colors,
          borderWidth: 1.5,
          borderRadius: 4,
          maxBarThickness: 28,
        },
      ],
    },
    options: baseChartOptions({ max: 1, indexAxis: "y" }),
  });
}

function renderDetailChart(metrics) {
  const ctx = el("detailChart");
  const names = Object.keys(metrics);
  const colors = names.map((n) => GROUP_COLOR[metricGroup(n)]);

  if (state.charts.detail) state.charts.detail.destroy();

  state.charts.detail = new Chart(ctx, {
    type: "radar",
    data: {
      labels: names,
      datasets: [
        {
          label: "Score",
          data: names.map((n) => metrics[n]),
          backgroundColor: "#35d0b833",
          borderColor: "#35d0b8",
          pointBackgroundColor: colors,
          pointBorderColor: colors,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 1,
          ticks: { display: false },
          grid: { color: "#212734" },
          angleLines: { color: "#212734" },
          pointLabels: { color: "#8891a3", font: { family: "JetBrains Mono", size: 10.5 } },
        },
      },
      plugins: { legend: { display: false } },
    },
  });
}

function baseChartOptions({ max = 1, indexAxis = "x" } = {}) {
  const valueAxis = { min: 0, max, grid: { color: "#1a1f2b" }, ticks: { color: "#565f72", font: { family: "JetBrains Mono", size: 10.5 } } };
  const labelAxis = { grid: { display: false }, ticks: { color: "#8891a3", font: { family: "Inter", size: 11 } } };

  return {
    indexAxis,
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales:
      indexAxis === "y"
        ? { x: valueAxis, y: labelAxis }
        : { y: valueAxis, x: labelAxis },
  };
}

function renderSamples(rows) {
  const body = el("samplesBody");

  if (!rows.length) {
    body.innerHTML = `<tr class="empty-row"><td colspan="5">No evaluations for this benchmark.</td></tr>`;
    return;
  }

  body.innerHTML = rows
    .map((r) => {
      const m = r.metrics || {};
      const chip = (name) =>
        name in m
          ? `<span class="metric-chip ${scoreClass(name, m[name])}">${fmtScore(m[name])}</span>`
          : `<span class="metric-chip">\u2014</span>`;

      return `
        <tr>
          <td class="cell-truncate" title="${escapeHtml(r.query)}">${escapeHtml(r.query)}</td>
          <td class="cell-truncate" title="${escapeHtml(r.answer)}">${escapeHtml(r.answer)}</td>
          <td>${chip("faithfulness")}</td>
          <td>${chip("correctness")}</td>
          <td>${chip("semantic_similarity")}</td>
        </tr>`;
    })
    .join("");
}

function renderTerminalFeed(latest, metrics) {
  const feed = el("terminalFeed");
  if (!latest) {
    feed.innerHTML = `<div class="terminal-line dim">$ python scripts/run_evaluation.py</div><div class="terminal-line dim">No runs yet.</div>`;
    return;
  }

  const lines = [
    `<div class="terminal-line dim">$ python scripts/run_evaluation.py</div>`,
    `<div class="terminal-line head">Benchmark #${latest.id} &middot; ${escapeHtml(latest.name)}</div>`,
    `<div class="terminal-line ok">Dataset Loaded &check;</div>`,
    `<div class="terminal-line ok">Status: ${escapeHtml(latest.status)}</div>`,
  ];

  if (metrics && metrics.metrics) {
    lines.push(`<div class="terminal-line dim"></div>`);
    lines.push(`<div class="terminal-line retrieval">Running Retrieval Metrics...</div>`);
    METRIC_GROUPS.retrieval.forEach((n) => {
      if (n in metrics.metrics) lines.push(termLine(n, metrics.metrics[n]));
    });
    lines.push(`<div class="terminal-line dim"></div>`);
    lines.push(`<div class="terminal-line generation">Running Generation Metrics...</div>`);
    METRIC_GROUPS.generation.forEach((n) => {
      if (n in metrics.metrics) lines.push(termLine(n, metrics.metrics[n]));
    });
    lines.push(`<div class="terminal-line dim"></div>`);
    lines.push(`<div class="terminal-line judge">Running LLM-Judge Metrics...</div>`);
    METRIC_GROUPS.judge.forEach((n) => {
      if (n in metrics.metrics) lines.push(termLine(n, metrics.metrics[n]));
    });
  }

  lines.push(`<div class="terminal-line dim"></div>`);
  lines.push(`<div class="terminal-line ok">Leaderboard Updated &check;</div>`);
  lines.push(`<div class="terminal-line ok">Reports Generated &check;</div>`);

  feed.innerHTML = lines.join("");
  feed.scrollTop = 0;
}

function termLine(name, value) {
  return `<div class="terminal-line">  ${name.padEnd(20, "\u00a0")}${fmtScore(value)}</div>`;
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------------- Detail (drill-down) ----------------

function populateBenchmarkSelect(benchmarks) {
  const select = el("benchmarkSelect");
  const previous = state.selectedBenchmarkId;

  select.innerHTML = benchmarks
    .map((b) => `<option value="${b.id}">#${b.id} · ${b.name}</option>`)
    .join("");

  const stillExists = benchmarks.some((b) => b.id === previous);
  state.selectedBenchmarkId = stillExists ? previous : benchmarks[0]?.id ?? null;

  if (state.selectedBenchmarkId !== null) {
    select.value = String(state.selectedBenchmarkId);
  }
}

function setDownloadLinks(id) {
  const base = state.apiBase.replace(/\/$/, "");
  el("downloadJson").href = `${base}/reports/${id}/json`;
  el("downloadCsv").href = `${base}/reports/${id}/csv`;
  el("downloadMd").href = `${base}/reports/${id}/markdown`;
}

async function loadDetail(id) {
  if (id === null || id === undefined) return;

  setDownloadLinks(id);

  try {
    const [metrics, samples] = await Promise.all([
      apiGet(`/benchmarks/${id}/metrics`),
      apiGet(`/benchmarks/${id}/evaluations?limit=50`),
    ]);

    renderDetailChart(metrics.metrics);
    renderSamples(samples);

    return metrics;
  } catch (err) {
    console.error(err);
  }
}

// ---------------- Main load cycle ----------------

async function loadAll() {
  try {
    const [summary, leaderboard, benchmarks] = await Promise.all([
      apiGet("/summary"),
      apiGet("/leaderboard/"),
      apiGet("/benchmarks/"),
    ]);

    setStatus("ok", "connected");

    renderStats(summary);
    renderLeaderboard(leaderboard);
    renderComparisonChart(leaderboard);
    renderMetricChart(summary.metric_averages);

    const sortedBenchmarks = [...benchmarks].sort((a, b) => b.id - a.id);
    populateBenchmarkSelect(sortedBenchmarks);

    const detailMetrics = await loadDetail(state.selectedBenchmarkId);
    renderTerminalFeed(summary.latest_benchmark, detailMetrics);

    el("lastUpdated").textContent = `updated ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    console.error(err);
    setStatus("error", "unreachable");
  }
}

// ---------------- Wiring ----------------

function scheduleAutoRefresh() {
  if (state.timer) clearInterval(state.timer);
  if (el("autoRefresh").checked) {
    state.timer = setInterval(loadAll, 8000);
  }
}

function init() {
  el("apiBaseInput").value = state.apiBase;

  el("apiBaseInput").addEventListener("change", (e) => {
    state.apiBase = e.target.value.trim() || state.apiBase;
    localStorage.setItem("ragEvalApiBase", state.apiBase);
    loadAll();
  });

  el("refreshBtn").addEventListener("click", loadAll);
  el("autoRefresh").addEventListener("change", scheduleAutoRefresh);

  el("benchmarkSelect").addEventListener("change", async (e) => {
    state.selectedBenchmarkId = Number(e.target.value);
    await loadDetail(state.selectedBenchmarkId);
  });

  loadAll();
  scheduleAutoRefresh();
}

init();
