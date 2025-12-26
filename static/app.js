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
