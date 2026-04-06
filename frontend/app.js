const BACKEND = "http://localhost:8000/chat";
let history = [];
let loading = false;

const msgsEl = document.getElementById("messages");
const inputEl = document.getElementById("input");
const btnEl   = document.getElementById("sendBtn");
const chipsEl = document.getElementById("chips");

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function useChip(el) {
  inputEl.value = el.textContent;
  autoResize(inputEl);
  chipsEl.style.display = "none";
  sendMessage();
}

function scroll() {
  msgsEl.scrollTop = msgsEl.scrollHeight;
}

function detectUrgency(text) {
  const t = text.toUpperCase();
  if (t.includes("[EMERGENCY]") || t.includes("EMERGENCY")) return "emergency";
  if (t.includes("[URGENT]")    || t.includes("URGENT"))    return "urgent";
  return "routine";
}

function addUserBubble(text) {
  const el = document.createElement("div");
  el.className = "msg user";
  el.innerHTML = `
    <div class="avatar user">U</div>
    <div class="bubble">${escHtml(text)}</div>`;
  msgsEl.appendChild(el);
  scroll();
}

function addTyping() {
  const el = document.createElement("div");
  el.className = "msg bot";
  el.id = "typing";
  el.innerHTML = `
    <div class="avatar bot">M</div>
    <div class="bubble">
      <div class="typing">
        <div class="tdot"></div>
        <div class="tdot"></div>
        <div class="tdot"></div>
      </div>
    </div>`;
  msgsEl.appendChild(el);
  scroll();
}

function removeTyping() {
  const el = document.getElementById("typing");
  if (el) el.remove();
}

function addBotBubble(reply, sources) {
  const urgency = detectUrgency(reply);
  const clean = reply
    .replace(/\[ROUTINE\]|\[URGENT\]|\[EMERGENCY\]/gi, "")
    .trim();

  const sourceHtml = "";

  const el = document.createElement("div");
  el.className = "msg bot";
  el.innerHTML = `
    <div class="avatar bot">M</div>
    <div class="bubble">
      <span class="badge ${urgency}">${urgency.toUpperCase()}</span>
      <div>${clean}</div>
      ${sourceHtml}
    </div>`;
  msgsEl.appendChild(el);
  scroll();
}

function addErrorBubble(msg) {
  const el = document.createElement("div");
  el.className = "msg bot";
  el.innerHTML = `
    <div class="avatar bot">M</div>
    <div class="bubble" style="color:#c0392b;">
      ⚠️ ${escHtml(msg)}
    </div>`;
  msgsEl.appendChild(el);
  scroll();
}

function escHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || loading) return;

  loading = true;
  btnEl.disabled = true;
  inputEl.value = "";
  inputEl.style.height = "auto";

  addUserBubble(text);
  addTyping();

  history.push({ role: "user", content: text });

  try {
    const res = await fetch(BACKEND, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history: history.slice(0, -1)   // exclude the just-added message
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `Server error ${res.status}`);
    }

    const data = await res.json();
    removeTyping();
    addBotBubble(data.reply, data.sources);
    history.push({ role: "assistant", content: data.reply });

  } catch (err) {
    removeTyping();
    addErrorBubble(
      err.message.includes("fetch")
        ? "Cannot reach backend. Make sure FastAPI is running at localhost:8000."
        : err.message
    );
    history.pop();
  }

  loading = false;
  btnEl.disabled = false;
  inputEl.focus();
}