// LinguaFlow — interface logic (vanilla JS + fetch)

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

async function api(url, options = {}) {
    const res = await fetch(url, options);
    const ct = res.headers.get("content-type") || "";
    const body = ct.includes("application/json") ? await res.json() : await res.text();
    if (!res.ok) {
        const detail = (body && body.detail) ? body.detail : (typeof body === "string" ? body : "Erreur");
        throw new Error(detail);
    }
    return body;
}

/* ----------------------------- Upload page ----------------------------- */
function initUpload() {
    const form = $("#uploadForm");
    if (!form) return;
    const dropZone = $("#dropZone");
    const fileInput = $("#fileInput");
    const browseBtn = $("#browseBtn");
    const fileName = $("#fileName");
    const result = $("#uploadResult");

    browseBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length) fileName.textContent = fileInput.files[0].name;
    });
    ["dragenter", "dragover"].forEach(ev =>
        dropZone.addEventListener(ev, e => { e.preventDefault(); dropZone.classList.add("dragover"); }));
    ["dragleave", "drop"].forEach(ev =>
        dropZone.addEventListener(ev, e => { e.preventDefault(); dropZone.classList.remove("dragover"); }));
    dropZone.addEventListener("drop", e => {
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            fileName.textContent = e.dataTransfer.files[0].name;
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) { alert("Veuillez choisir un fichier."); return; }
        const data = new FormData();
        data.append("file", fileInput.files[0]);
        data.append("target_lang", $("#targetLang").value);
        data.append("source_lang", $("#sourceLang").value);
        data.append("engine", $("#engineSelect").value);
        data.append("correction", $("#correction").checked ? "true" : "false");

        const btn = $("#submitBtn");
        btn.disabled = true; result.classList.remove("hidden");
        result.innerHTML = "<p>Téléversement…</p>";
        try {
            const resp = await api("/api/upload", { method: "POST", body: data });
            result.innerHTML = `<p>Fichier « ${escapeHtml(data.get('file').name)} » importé.</p>
                <p>Type : <strong>${data.get("file").name.split('.').pop()}</strong> ·
                Langue détectée : <strong>${data.detected_lang || "indéterminée"}</strong></p>
                <p>Redirection vers le suivi…</p>`;
            window.location.href = `/tasks/${resp.task_id}`;
        } catch (err) {
            result.innerHTML = `<div class="error-box">Échec de l'import : ${escapeHtml(err.message)}</div>`;
        } finally {
            $("#submitBtn").disabled = false;
        }
    });
}

/* --------------------------- Task detail page -------------------------- */
function initTaskPage() {
    const el = $("#progressBar");
    if (!el) return;
    const taskId = document.body.dataset.taskId || location.pathname.split("/").pop();
    let interval = null;

    async function poll() {
        try {
            const p = await api(`/api/tasks/${taskId}/progress`);
            const bar = $("#progressBar");
            bar.style.width = (p.percent || 0) + "%";
            $("#progressMessage").textContent = `${p.status} — ${p.message} (${p.done}/${p.total})`;
            if (p.status === "completed" || p.status === "failed" || p.status === "interrupted") {
                clearInterval(interval);
                loadTask(taskId);
            }
        } catch (e) { /* transient */ }
    }

    $("#resumeButton")?.addEventListener("click", async () => {
        try {
            await api(`/api/tasks/${taskId}/resume`, { method: "POST" });
            $("#resumeButton").classList.add("hidden");
            if (!interval) interval = setInterval(poll, 1200);
            poll();
        } catch (e) { alert("Reprise impossible : " + e.message); }
    });

    loadTask(taskId);
    interval = setInterval(poll, 1200);
}

async function loadTask(taskId) {
    let t;
    try { t = await api(`/api/tasks/${taskId}`); } catch (e) { return; }
    const next = $("#nextSegments");
    const downloadLink = $("#downloadLink");
    if (downloadLink) {
        if (t.status === "completed" && t.result_path) {
            downloadLink.href = `/api/tasks/${taskId}/download`;
            downloadLink.classList.remove("hidden");
            $("#resumeButton")?.classList.add("hidden");
        } else if (t.status === "interrupted" || t.status === "failed") {
            $("#resumeButton")?.classList.remove("hidden");
        }
    }
    $("#taskStatus").textContent = t.status;
    if (t.errors) showBox("errorBox", "Erreur : " + t.errors);
    if (t.warnings) showBox("warningBox", "Avertissements : " + t.warnings, true);
    try {
        const p = await api(`/api/tasks/${taskId}/preview?limit=200`);
        if (next) {
            next.innerHTML = p.segments.map(s => `<tr>
                <td>${s.index + 1}</td><td>${escapeHtml(s.source || "")}</td>
                <td>${escapeHtml(s.translated || "")}</td></tr>`).join("");
        }
    } catch (e) {}
}

/* ---------------------------- History page ----------------------------- */
function initHistory() {
    const tbody = $("#historyBody");
    if (!tbody) return;
    async function load() {
        const tasks = await api("/api/tasks");
        tbody.innerHTML = tasks.map(t => `<tr>
            <td>${escapeHtml(t.filename)}</td>
            <td>${t.file_type}</td>
            <td>${t.source_lang || t.detected_lang || "?"} → ${t.target_lang}</td>
            <td>${t.engine_used || "-"} <span class="badge ${t.engine_mode}">${t.engine_mode}</span></td>
            <td class="status-${t.status}">${t.status}</td>
            <td>${t.segments_processed}/${t.segments_total}</td>
            <td>
                <a href="/tasks/${t.task_id}">Détail</a>
                ${t.result_path ? ` · <a href="/api/tasks/${t.task_id}/download">Télécharger</a>` : ""}
            </td></tr>`).join("") || `<tr><td colspan="7" class="hint">Aucune tâche.</td></tr>`;
    }
    $("#refreshBtn")?.addEventListener("click", load);
    $("#clearHistoryBtn")?.addEventListener("click", async () => {
        if (!confirm("Effacer tout l'historique et les fichiers associés ?")) return;
        await api("/api/history", { method: "DELETE" });
        load();
    });
    load();
}

/* ---------------------------- Settings page ---------------------------- */
async function initSettings() {
    const form = $("#settingsForm");
    if (!form) return;
    try {
        const s = await api("/api/settings");
        $("#s_target").value = s.default_target_lang || "fr";
        $("#s_correction").checked = !!s.correction_enabled;
        $("#s_ocr").checked = !!s.ocr_enabled;
        $("#s_remote_enabled").checked = !!s.remote_enabled;
        $("#s_remote_endpoint").value = s.remote_endpoint || "";
    } catch (e) {}
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            default_target_lang: $("#s_target").value,
            correction_enabled: $("#s_correction").checked,
            ocr_enabled: $("#s_ocr").checked,
            remote_enabled: $("#s_remote_enabled").checked,
            remote_endpoint: $("#s_remote_endpoint").value,
        };
        const key = $("#s_remote_api_key").value;
        if (key) payload.remote_api_key = key;
        try {
            await api("/api/settings", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            $("#settingsSaved").textContent = "Enregistré.";
        } catch (e) { $("#settingsSaved").textContent = "Erreur : " + e.message; }
    });
}

/* ---------------------------- Glossary page ---------------------------- */
async function initGlossary() {
    const gTable = $("#glossaryBody");
    if (!gTable) return;
    async function loadGlossary() {
        const rows = await api("/api/glossary");
        gTable.innerHTML = rows.map(r => `<tr>
            <td>${escapeHtml(r.source_term)}</td><td>${escapeHtml(r.target_term)}</td>
            <td>${escapeHtml(r.domain || "")}</td>
            <td><button class="danger" data-del-glossary="${r.id}">Suppr.</button></td></tr>`).join("")
            || `<tr><td colspan="4" class="hint">Aucun terme.</td></tr>`;
    }
    async function loadProtected() {
        const rows = await api("/api/protected-terms");
        $("#protectedBody").innerHTML = rows.map(r => `<tr>
            <td>${escapeHtml(r.term)}</td><td>${escapeHtml(r.category || "")}</td>
            <td><button class="danger" data-del-protected="${r.id}">Suppr.</button></td></tr>`).join("")
            || `<tr><td colspan="3" class="hint">Aucun terme.</td></tr>`;
    }
    $("#glossaryForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        await api("/api/glossary", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source_term: $("#g_source").value, target_term: $("#g_target").value, domain: $("#g_domain").value }),
        });
        $("#g_source").value = $("#g_target").value = $("#g_domain").value = "";
        loadGlossary();
    });
    $("#protectedForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        await api("/api/protected-terms", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ term: $("#p_term").value, category: $("#p_category").value }),
        });
        $("#p_term").value = $("#p_category").value = "";
        loadProtected();
    });
    document.addEventListener("click", async (e) => {
        const g = e.target.dataset.delGlossary, p = e.target.dataset.delProtected;
        if (g) { await api(`/api/glossary/${g}`, { method: "DELETE" }); loadGlossary(); }
        if (p) { await api(`/api/protected-terms/${p}`, { method: "DELETE" }); loadProtected(); }
    });
    loadGlossary(); loadProtected();
}

/* ------------------------------- helpers ------------------------------- */
function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function showBox(id, text, warning) {
    const el = $("#" + id);
    if (el) { el.textContent = text; el.classList.remove("hidden"); }
}

document.addEventListener("DOMContentLoaded", () => {
    const path = location.pathname;
    if (path === "/" || path === "") initUpload();
    else if (path.startsWith("/tasks/")) initTaskPage();
    else if (path === "/history") initHistory();
    else if (path === "/settings") initSettings();
    else if (path === "/glossary") initGlossary();
});
