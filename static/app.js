document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("comment-form");
  const input = document.getElementById("comment-input");
  const list = document.getElementById("comments-list");
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

  // Yandex Metrika consent + lazy load
  const yandexId = document.body?.dataset.yandexId;
  const banner = document.getElementById("cookie-banner");
  const acceptBtn = document.getElementById("cookie-accept");
  const consentKey = "yandexMetrikaConsent";

  const hasConsent = localStorage.getItem(consentKey) === "accepted";

  if (yandexId) {
    if (hasConsent) {
      loadYandex(yandexId);
    } else if (banner) {
      banner.classList.remove("hidden");
    }
  }

  if (banner && acceptBtn && yandexId) {
    acceptBtn.addEventListener("click", () => {
      localStorage.setItem(consentKey, "accepted");
      banner.classList.add("hidden");
      loadYandex(yandexId);
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

function loadYandex(counterId) {
  if (!counterId || window.__ymInitialized) return;
  window.__ymInitialized = true;
  (function (m, e, t, r, i, k, a) {
    m[i] =
      m[i] ||
      function () {
        (m[i].a = m[i].a || []).push(arguments);
      };
    m[i].l = 1 * new Date();
    k = e.createElement(t);
    a = e.getElementsByTagName(t)[0];
    k.async = 1;
    k.src = r;
    a.parentNode.insertBefore(k, a);
  })(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

  window.ym(counterId, "init", {
    clickmap: true,
    trackLinks: true,
    accurateTrackBounce: true,
    webvisor: true,
    defer: true,
  });
}
