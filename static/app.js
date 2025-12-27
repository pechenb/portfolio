document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("comment-form");
  const input = document.getElementById("comment-input");
  const list = document.getElementById("comments-list");
  const tgBtn = document.getElementById("tg-login");
  const tgBotUsername = document.body.dataset?.tgBot || "";

  if (form && input && list) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = input.value.trim();
      if (!body) return;
      try {
        const res = await fetch("/comments", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ body }),
        });
        if (!res.ok) throw new Error("Failed to post");
        const data = await res.json();
        prependComment(list, data);
        input.value = "";
      } catch (err) {
        console.error(err);
        alert("Could not post comment. Are you logged in?");
      }
    });
  }

  if (tgBtn) {
    tgBtn.addEventListener("click", () => {
      launchTelegramLogin(tgBotUsername);
    });
  }
});

function prependComment(list, data) {
  const item = document.createElement("div");
  item.className = "comment";
  item.innerHTML = `
    <div class="comment__avatar" style="background-image:url('${data.avatar || ""}')"></div>
    <div class="comment__body">
      <div class="comment__meta">
        <span class="comment__author">${data.author || "Anonymous"}</span>
        <span class="comment__time">just now</span>
      </div>
      <div class="comment__text"></div>
    </div>
  `;
  item.querySelector(".comment__text").textContent = data.body || "";
  list.prepend(item);
}

function launchTelegramLogin(botUsername) {
  if (!botUsername) {
    alert("Telegram bot username is not configured.");
    return;
  }
  const popup = window.open(
    `https://oauth.telegram.org/auth?bot=${encodeURIComponent(botUsername)}&origin=${encodeURIComponent(
      window.location.origin
    )}&return_to=${encodeURIComponent(window.location.origin)}`,
    "tgAuth",
    "width=600,height=700"
  );
  if (!popup) {
    alert("Please allow popups for Telegram login.");
  }
}

// Called from Telegram widget when auth succeeds
window.onTelegramAuth = async function (user) {
  try {
    const res = await fetch("/auth/telegram", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user }),
    });
    if (!res.ok) throw new Error("Login failed");
    window.location.reload();
  } catch (err) {
    console.error(err);
    alert("Telegram login failed");
  }
};
