const inputText = document.getElementById("inputText");
const structuredMode = document.getElementById("structuredMode");
const summarizeBtn = document.getElementById("summarizeBtn");
const outputBox = document.getElementById("outputBox");
const statusPill = document.getElementById("statusPill");

const sampleText =
  "Artificial intelligence is transforming industries worldwide. From healthcare to finance, AI automates complex tasks and improves decision making at scale.";

if (!inputText.value) {
  inputText.value = sampleText;
}

function setStatus(type, text) {
  statusPill.className = `pill ${type}`;
  statusPill.textContent = text;
}

async function summarize() {
  const text = inputText.value.trim();
  if (!text) {
    setStatus("error", "Empty input");
    outputBox.textContent = "Please enter text before summarizing.";
    return;
  }

  summarizeBtn.disabled = true;
  setStatus("loading", "Working");
  outputBox.textContent = "Calling ADK agent...";

  try {
    const endpoint = structuredMode.checked ? "/summarize/structured" : "/summarize";
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: text }),
    });

    const rawBody = await response.text();
    let payload;
    try {
      payload = rawBody ? JSON.parse(rawBody) : {};
    } catch {
      payload = { detail: rawBody || "Request failed" };
    }

    if (!response.ok) {
      throw new Error(payload.detail || "Request failed");
    }

    if (structuredMode.checked) {
      outputBox.textContent = JSON.stringify(payload, null, 2);
    } else {
      outputBox.textContent = payload.summary || "No summary returned.";
    }
    setStatus("success", "Success");
  } catch (error) {
    setStatus("error", "Error");
    outputBox.textContent = String(error);
  } finally {
    summarizeBtn.disabled = false;
  }
}

summarizeBtn.addEventListener("click", summarize);
