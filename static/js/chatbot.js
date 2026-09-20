// Self-contained CineBot widget. Talks to the app's own /chatbot endpoint
// (see app.py) — no external Dialogflow agent/config required.

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("chatbot-toggle");
  const chatWindow = document.getElementById("chatbot-window");
  const closeBtn = document.getElementById("chatbot-close");
  const messagesEl = document.getElementById("chatbot-messages");
  const form = document.getElementById("chatbot-form");
  const input = document.getElementById("chatbot-input");

  if (!toggleBtn || !chatWindow || !form || !messagesEl || !input) return;

  function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `chatbot-msg chatbot-msg-${sender}`;
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  let greeted = false;

  toggleBtn.addEventListener("click", () => {
    const isOpen = chatWindow.style.display === "flex";
    chatWindow.style.display = isOpen ? "none" : "flex";

    if (!isOpen && !greeted) {
      addMessage("Hi! I'm CineBot 🎬. Try \"suggest horror movies\" or \"movies like Avatar\".", "bot");
      greeted = true;
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      chatWindow.style.display = "none";
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    fetch("/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    })
      .then(res => res.json())
      .then(data => {
        addMessage(data.reply || "Sorry, something went wrong.", "bot");
      })
      .catch(() => {
        addMessage("Sorry, I couldn't reach the server. Please try again.", "bot");
      });
  });
});
