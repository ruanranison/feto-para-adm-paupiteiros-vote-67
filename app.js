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
    shareBtn.href = "https://wa.me/?text=" + encodeURIComponent(shareText);
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

  /* Urna eletrônica */
  const digitsEl = document.getElementById("urnaDigits");
  const candidateEl = document.getElementById("urnaCandidate");
  const msgEl = document.getElementById("urnaMsg");
  const pad = document.getElementById("urnaPad");
  const btnBranco = document.getElementById("urnaBranco");
  const btnCorrige = document.getElementById("urnaCorrige");
  const btnConfirma = document.getElementById("urnaConfirma");

  if (!digitsEl || !candidateEl || !msgEl || !pad) return;

  let digits = "";
  let locked = false;

  function render() {
    const slots = digitsEl.querySelectorAll(".urna__slot");
    slots.forEach(function (slot, i) {
      slot.textContent = digits[i] || "_";
    });

    const isFeto = digits === "67";
    candidateEl.hidden = !isFeto;

    if (locked) return;

    if (digits.length === 0) {
      msgEl.textContent = "Digite o número do candidato";
      msgEl.classList.remove("is-ok");
    } else if (isFeto) {
      msgEl.textContent = "Candidato encontrado. Aperte CONFIRMA.";
      msgEl.classList.remove("is-ok");
    } else if (digits.length >= 2) {
      msgEl.textContent = "Número inválido nesta campanha. Use CORRIGE.";
      msgEl.classList.remove("is-ok");
    } else {
      msgEl.textContent = "Continue digitando…";
      msgEl.classList.remove("is-ok");
    }
  }

  function pressDigit(d) {
    if (locked) return;
    if (digits.length >= 2) return;
    digits += String(d);
    render();
  }

  function corrige() {
    locked = false;
    digits = "";
    candidateEl.hidden = true;
    msgEl.classList.remove("is-ok");
    render();
  }

  function branco() {
    if (locked) return;
    digits = "";
    candidateEl.hidden = true;
    msgEl.textContent = "Voto em branco (demo). Use CORRIGE para voltar.";
    msgEl.classList.remove("is-ok");
    digitsEl.querySelectorAll(".urna__slot").forEach(function (slot) {
      slot.textContent = "_";
    });
  }

  function confirma() {
    if (locked) return;
    if (digits === "67") {
      locked = true;
      msgEl.textContent = "Voto registrado · 67 · Feto";
      msgEl.classList.add("is-ok");
      return;
    }
    if (digits.length === 0) {
      msgEl.textContent = "Digite 67 antes de confirmar.";
      return;
    }
    msgEl.textContent = "Só o 67 confirma nesta urna. Use CORRIGE.";
  }

  pad.querySelectorAll("button[data-key]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      pressDigit(btn.getAttribute("data-key"));
    });
  });

  if (btnCorrige) btnCorrige.addEventListener("click", corrige);
  if (btnBranco) btnBranco.addEventListener("click", branco);
  if (btnConfirma) btnConfirma.addEventListener("click", confirma);

  window.addEventListener("keydown", function (e) {
    if (!document.getElementById("vote")) return;
    const vote = document.getElementById("vote");
    const rect = vote.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top > window.innerHeight) return;

    if (e.key >= "0" && e.key <= "9") {
      pressDigit(e.key);
    } else if (e.key === "Backspace") {
      e.preventDefault();
      corrige();
    } else if (e.key === "Enter") {
      confirma();
    }
  });

  render();
})();
