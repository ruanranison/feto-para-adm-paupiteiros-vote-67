(function () {
  const nav = document.querySelector(".nav");
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("navMenu");
  const shareBtn = document.getElementById("shareWhatsApp");
  const copyBtn = document.getElementById("copyLink");
  const toast = document.getElementById("copyToast");

  const pageUrl = window.location.href.split("#")[0];
  const shareText =
    "Vote 67 — Feto (Ruan Ranison) para administrador do Paupiteiros. Conheça a campanha: " +
    pageUrl;

  if (shareBtn) {
    shareBtn.href =
      "https://wa.me/?text=" + encodeURIComponent(shareText);
  }

  if (toggle && nav && menu) {
    toggle.addEventListener("click", function () {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Abrir menu");
      });
    });
  }

  if (copyBtn && toast) {
    copyBtn.addEventListener("click", async function () {
      try {
        await navigator.clipboard.writeText(pageUrl);
        toast.textContent = "Link copiado.";
      } catch (err) {
        toast.textContent = pageUrl;
      }
      window.setTimeout(function () {
        toast.textContent = "";
      }, 2800);
    });
  }
})();
