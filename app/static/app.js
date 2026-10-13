const labels = { todo: "未着手", in_progress: "進行中", done: "完了", low: "優先度 低", medium: "優先度 中", high: "優先度 高" };
const form = document.querySelector("#task-form");
const list = document.querySelector("#task-list");

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function render(tasks) {
  document.querySelector("#task-count").textContent = tasks.length;
  if (!tasks.length) { list.innerHTML = '<p class="empty">条件に一致するタスクはありません。</p>'; return; }
  list.innerHTML = tasks.map((task) => `
    <article class="task-card">
      <div><h3>${escapeHtml(task.title)}</h3><p>${escapeHtml(task.description || "説明はありません")}</p>
        <div class="task-meta"><span class="badge ${task.status === "done" ? "done" : ""}">${labels[task.status]}</span><span class="badge ${task.priority === "high" ? "high" : ""}">${labels[task.priority]}</span>${task.due_date ? `<span class="badge">期限 ${escapeHtml(task.due_date)}</span>` : ""}</div>
      </div>
      <div class="task-actions"><button class="icon-button" data-action="toggle" data-id="${task.id}" title="完了状態を切り替え">${task.status === "done" ? "↩" : "✓"}</button><button class="icon-button" data-action="delete" data-id="${task.id}" title="削除">×</button></div>
    </article>`).join("");
}

async function loadTasks() {
  const status = document.querySelector("#filter-status").value;
  const sortBy = document.querySelector("#sort-by").value;
  const params = new URLSearchParams({ limit: "100", sort_by: sortBy, sort_order: sortBy === "priority" ? "desc" : "asc" });
  if (status) params.set("status", status);
  const response = await fetch(`/api/tasks?${params}`);
  if (!response.ok) throw new Error("タスクの取得に失敗しました");
  render((await response.json()).items);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#form-message");
  const data = Object.fromEntries(new FormData(form).entries());
  if (!data.description) delete data.description;
  if (!data.due_date) delete data.due_date;
  const response = await fetch("/api/tasks", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
  if (!response.ok) { message.textContent = "入力内容を確認してください"; return; }
  form.reset(); message.textContent = "作成しました"; setTimeout(() => { message.textContent = ""; }, 1800); await loadTasks();
});

list.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]"); if (!button) return;
  const id = button.dataset.id;
  if (button.dataset.action === "delete" && !window.confirm("このタスクを削除しますか？")) return;
  if (button.dataset.action === "delete") await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  if (button.dataset.action === "toggle") {
    const task = (await (await fetch(`/api/tasks/${id}`)).json());
    await fetch(`/api/tasks/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: task.status === "done" ? "todo" : "done" }) });
  }
  await loadTasks();
});

document.querySelector("#filter-status").addEventListener("change", loadTasks);
document.querySelector("#sort-by").addEventListener("change", loadTasks);
loadTasks().catch((error) => { list.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`; });
