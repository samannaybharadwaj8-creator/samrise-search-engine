const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let lastQuery = "";

function toast(message) {
  const el = $("toast"); el.textContent = message; el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2400);
}
async function refresh() {
  const [stats, docs, index] = await Promise.all([
    fetch("/api/stats").then(r=>r.json()),
    fetch("/api/documents").then(r=>r.json()),
    fetch("/api/index").then(r=>r.json())
  ]);
  $("stat-docs").textContent = stats.documents;
  $("stat-terms").textContent = stats.terms;
  $("stat-postings").textContent = stats.postings;
  $("stat-avg").textContent = stats.avg_terms;
  $("docCount").textContent = `${docs.length} DOCS`;
  $("docList").innerHTML = docs.length ? docs.map(d => `
    <div class="doc-item"><div class="doc-icon">▤</div><div class="doc-info"><b>${esc(d.title)}</b><small>${esc(d.category)} · ID ${d.id}</small></div>
    <button class="delete-btn" data-delete="${d.id}" title="Delete document">×</button></div>`).join("") : '<div class="empty">NO DOCUMENTS IN COLLECTION</div>';
  $("indexBody").innerHTML = index.length ? index.slice(0,80).map(row => `
    <tr><td>${esc(row.term)}</td><td>${row.documents.map(id=>`<span class="pill">#${id}</span>`).join(" ")}</td><td>${row.frequency}</td><td><span class="pill">INDEXED</span></td></tr>`).join("") : '<tr><td colspan="4">Index is empty.</td></tr>';
}
async function runSearch() {
  const q = $("searchInput").value.trim(); lastQuery = q;
  if (!q) { $("queryMeta").textContent = "Enter a query to retrieve matching documents from your index."; $("results").innerHTML = ""; return; }
  const data = await fetch(`/api/search?q=${encodeURIComponent(q)}`).then(r=>r.json());
  $("queryMeta").textContent = `${data.results.length} RESULT(S) · QUERY TOKENS: ${data.terms.join(", ") || "none"}`;
  $("results").innerHTML = data.results.length ? data.results.map(d=>`
    <article class="result-card"><div><small>${esc(d.category)} · DOCUMENT #${d.id}</small><h3>${esc(d.title)}</h3><p>${esc(d.snippet)}</p></div><div class="score">SCORE<br><b>${d.score}</b></div></article>`).join("") : '<div class="empty">NO MATCHES FOUND — TRY ANOTHER TERM</div>';
}
$("searchBtn").addEventListener("click", runSearch);
$("searchInput").addEventListener("keydown", e=>{if(e.key==="Enter")runSearch();});
$("addBtn").addEventListener("click", async ()=>{
  const payload = {title:$("docTitle").value,category:$("docCategory").value,content:$("docContent").value};
  const response = await fetch("/api/documents",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok) { $("formNote").textContent = data.error; $("formNote").style.color = "#ff766b"; return; }
  $("docTitle").value=""; $("docCategory").value=""; $("docContent").value="";
  $("formNote").textContent="DOCUMENT ADDED · INDEX UPDATED"; $("formNote").style.color="#75c99b";
  toast("Document added and indexed."); await refresh();
});
$("docList").addEventListener("click", async e=>{
  const btn=e.target.closest("[data-delete]"); if(!btn)return;
  const response=await fetch(`/api/documents/${btn.dataset.delete}`,{method:"DELETE"});
  const data=await response.json(); toast(data.message || data.error); await refresh();
  if(lastQuery)runSearch();
});
refresh();
