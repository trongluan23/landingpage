(function () {
  "use strict";

  const form = document.getElementById("generator-form");
  const promptEl = document.getElementById("prompt");
  const charCount = document.getElementById("char-count");
  const generateBtn = document.getElementById("generate-btn");

  const styleChips = document.getElementById("style-chips");
  let selectedStyle = styleChips.querySelector(".chip.is-active").dataset.value;

  const autoLayoutCheckbox = document.getElementById("auto-layout");
  const manualLayoutGroup = document.getElementById("manual-layout-group");

  const emptyState = document.getElementById("empty-state");
  const loadingState = document.getElementById("loading-state");
  const loadingText = document.getElementById("loading-text");
  const errorState = document.getElementById("error-state");
  const errorText = document.getElementById("error-text");

  const previewFrame = document.getElementById("preview-frame");
  const codeView = document.getElementById("code-view");
  const codeContent = document.getElementById("code-content");
  const viewportWrapper = document.getElementById("viewport-wrapper");
  const viewportSelect = document.getElementById("viewport-select");

  const tabs = document.querySelectorAll(".tab");
  const copyBtn = document.getElementById("copy-btn");
  const newtabBtn = document.getElementById("newtab-btn");
  const downloadBtn = document.getElementById("download-btn");

  let currentHtml = "";
  let activeTab = "preview";

  const LOADING_MESSAGES = [
    "Đang phân tích yêu cầu...",
    "Đang lên bố cục trang...",
    "Đang viết nội dung...",
    "Đang phối màu & kiểu chữ...",
    "Hoàn thiện chi tiết cuối..."
  ];

  // ---- character counter ----
  promptEl.addEventListener("input", () => {
    charCount.textContent = promptEl.value.length;
  });

  // ---- style chips ----
  styleChips.addEventListener("click", (e) => {
    const btn = e.target.closest(".chip");
    if (!btn) return;
    styleChips.querySelectorAll(".chip").forEach((c) => c.classList.remove("is-active"));
    btn.classList.add("is-active");
    selectedStyle = btn.dataset.value;
  });

  // ---- auto layout toggle ----
  autoLayoutCheckbox.addEventListener("change", () => {
    if (autoLayoutCheckbox.checked) {
      manualLayoutGroup.style.display = "none";
    } else {
      manualLayoutGroup.style.display = "block";
    }
  });

  // ---- tabs ----
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("is-active"));
      tab.classList.add("is-active");
      activeTab = tab.dataset.tab;
      renderActiveTab();
    });
  });

  function renderActiveTab() {
    if (!currentHtml) return;
    if (activeTab === "preview") {
      previewFrame.hidden = false;
      codeView.hidden = true;
    } else {
      previewFrame.hidden = true;
      codeView.hidden = false;
    }
  }

  // ---- viewport switch ----
  viewportSelect.addEventListener("change", () => {
    viewportWrapper.dataset.viewport = viewportSelect.value;
  });

  // ---- states ----
  function showState(state) {
    emptyState.hidden = state !== "empty";
    loadingState.hidden = state !== "loading";
    errorState.hidden = state !== "error";
    previewFrame.hidden = state !== "result" || activeTab !== "preview";
    codeView.hidden = state !== "result" || activeTab !== "code";
  }

  let loadingInterval = null;
  function startLoadingMessages() {
    let i = 0;
    loadingText.textContent = LOADING_MESSAGES[0];
    loadingInterval = setInterval(() => {
      i = (i + 1) % LOADING_MESSAGES.length;
      loadingText.textContent = LOADING_MESSAGES[i];
    }, 2200);
  }
  function stopLoadingMessages() {
    clearInterval(loadingInterval);
  }

  // ---- form submit ----
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const prompt = promptEl.value.trim();
    if (!prompt) {
      promptEl.focus();
      return;
    }

    const payload = {
      prompt,
      industry: document.getElementById("industry").value.trim(),
      language: document.getElementById("language").value,
      style: selectedStyle,
      layout: autoLayoutCheckbox.checked ? "auto" : document.getElementById("layout").value,
      color: document.getElementById("color").value.trim(),
      cta: document.getElementById("cta").value.trim(),
      logo: document.getElementById("logo").value.trim(),
      heroImage: document.getElementById("heroImage").value.trim(),
      additionalImages: Array.from(document.querySelectorAll(".additional-image-input"))
        .map(input => input.value.trim())
        .filter(url => url.length > 0)
    };

    generateBtn.disabled = true;
    generateBtn.classList.add("is-loading");
    showState("loading");
    startLoadingMessages();
    [copyBtn, newtabBtn, downloadBtn].forEach((b) => (b.disabled = true));

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Đã có lỗi xảy ra, vui lòng thử lại.");
      }

      currentHtml = data.html;
      codeContent.textContent = currentHtml;
      previewFrame.srcdoc = currentHtml;

      showState("result");
      renderActiveTab();
      [copyBtn, newtabBtn, downloadBtn].forEach((b) => (b.disabled = false));
    } catch (err) {
      errorText.textContent = err.message || String(err);
      showState("error");
    } finally {
      stopLoadingMessages();
      generateBtn.disabled = false;
      generateBtn.classList.remove("is-loading");
    }
  });

  // ---- copy code ----
  copyBtn.addEventListener("click", async () => {
    if (!currentHtml) return;
    try {
      await navigator.clipboard.writeText(currentHtml);
      const original = copyBtn.textContent;
      copyBtn.textContent = "Đã sao chép!";
      setTimeout(() => (copyBtn.textContent = original), 1500);
    } catch {
      alert("Không thể sao chép tự động, vui lòng chọn thủ công trong tab Mã HTML.");
    }
  });

  // ---- open in new tab ----
  newtabBtn.addEventListener("click", () => {
    if (!currentHtml) return;
    const blob = new Blob([currentHtml], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  });

  // ---- download ----
  downloadBtn.addEventListener("click", () => {
    if (!currentHtml) return;
    const blob = new Blob([currentHtml], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "landing-page.html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
})();