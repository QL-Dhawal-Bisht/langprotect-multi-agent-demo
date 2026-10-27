const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const sendButton = document.querySelector("#send-button");
const transcript = document.querySelector("#transcript");
const serviceStatus = document.querySelector("#service-status");
const sessionLabel = document.querySelector("#session-label");
const traceAgent = document.querySelector("#trace-agent");
const traceSignal = document.querySelector("#trace-signal");
const traceEffects = document.querySelector("#trace-effects");
const traceSession = document.querySelector("#trace-session");
const eventList = document.querySelector("#event-list");

let currentSession = null;

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function appendMessage(role, text, metadata = {}) {
  const message = makeElement("article", `message ${role}-message`);
  if (metadata.candidate) message.classList.add("candidate-message");

  const author = makeElement("div", "message-author");
  const isUser = role === "user";
  const avatar = makeElement("span", "avatar", isUser ? "Y" : metadata.agent?.charAt(0) || "A");
  avatar.setAttribute("aria-hidden", "true");
  const identity = makeElement("span");
  identity.append(
    makeElement("strong", "", isUser ? "You" : metadata.agent || "Agent"),
    makeElement("small", "", isUser ? "Test operator" : metadata.candidate ? "Candidate signal" : "Safe response"),
  );
  author.append(avatar, identity);
  message.append(author, makeElement("p", metadata.error ? "error-message" : "", text));
  transcript.append(message);
  transcript.scrollTop = transcript.scrollHeight;
}

function updateTrace(payload) {
  traceAgent.textContent = payload.routed_agent;
  traceEffects.textContent = payload.effects_performed ? "Reported" : "None, simulated";
  traceSession.textContent = payload.session_id;
  traceSession.title = payload.session_id;
  sessionLabel.textContent = payload.session_id;
  sessionLabel.title = payload.session_id;

  traceSignal.textContent = payload.candidate_signal ? "Candidate" : "No signal";
  traceSignal.className = `signal ${payload.candidate_signal ? "candidate" : "safe"}`;

  eventList.replaceChildren();
  if (!payload.events.length) {
    eventList.append(makeElement("li", "", "No events recorded."));
    return;
  }
  for (const event of payload.events) {
    const item = makeElement("li");
    item.append(
      makeElement("strong", "", `${event.agent} · ${event.simulated ? "simulated" : "reported"}`),
      document.createTextNode(`${event.action} → ${event.target}`),
    );
    eventList.append(item);
  }
}

function setBusy(busy) {
  sendButton.disabled = busy;
  input.disabled = busy;
  sendButton.querySelector("span").textContent = busy ? "Sending" : "Send";
}

async function sendMessage(message) {
  appendMessage("user", message);
  setBusy(true);
  try {
    const response = await fetch("/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: currentSession }),
    });
    if (!response.ok) throw new Error(`Request failed with HTTP ${response.status}`);
    const payload = await response.json();
    currentSession = payload.session_id;
    appendMessage("assistant", payload.reply, {
      agent: payload.routed_agent,
      candidate: payload.candidate_signal,
    });
    updateTrace(payload);
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown request error";
    appendMessage("assistant", `The demo API could not respond. ${detail}`, {
      agent: "System",
      error: true,
    });
  } finally {
    setBusy(false);
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  sendMessage(message);
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

for (const button of document.querySelectorAll("[data-prompt]")) {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt || "";
    input.focus();
  });
}

fetch("/health")
  .then((response) => {
    if (!response.ok) throw new Error("unhealthy");
    serviceStatus.classList.add("online");
    serviceStatus.lastChild.textContent = " API online";
  })
  .catch(() => {
    serviceStatus.classList.add("offline");
    serviceStatus.lastChild.textContent = " API unavailable";
  });
