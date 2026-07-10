(function () {
  "use strict";

  const searchInput = document.getElementById("search-input");
  const layoutFilter = document.getElementById("layout-filter");
  const sortSelect = document.getElementById("sort-select");
  const galleryGrid = document.getElementById("gallery-grid");

  let allCards = Array.from(document.querySelectorAll(".page-card"));

  // Search and filter
  function filterAndSort() {
    const searchTerm = searchInput.value.toLowerCase();
    const layoutValue = layoutFilter.value;
    const sortValue = sortSelect.value;

    // Filter
    let visibleCards = allCards.filter((card) => {
      const title = card.dataset.title.toLowerCase();
      const prompt = card.dataset.prompt.toLowerCase();
      const industry = card.dataset.industry.toLowerCase();
      const layout = card.dataset.layout;

      const matchesSearch =
        !searchTerm ||
        title.includes(searchTerm) ||
        prompt.includes(searchTerm) ||
        industry.includes(searchTerm);

      const matchesLayout = !layoutValue || layout === layoutValue;

      return matchesSearch && matchesLayout;
    });

    // Sort
    visibleCards.sort((a, b) => {
      if (sortValue === "title") {
        return a.dataset.title.localeCompare(b.dataset.title);
      }
      // newest/oldest based on DOM order (newest first by default)
      return sortValue === "oldest" ? 1 : -1;
    });

    // Hide all
    allCards.forEach((card) => (card.style.display = "none"));

    // Show filtered and sorted
    visibleCards.forEach((card) => {
      card.style.display = "block";
      galleryGrid.appendChild(card); // Re-append to reorder
    });
  }

  searchInput?.addEventListener("input", filterAndSort);
  layoutFilter?.addEventListener("change", filterAndSort);
  sortSelect?.addEventListener("change", filterAndSort);

  // Global functions for inline onclick
  window.viewPage = async function (id) {
    try {
      const res = await fetch(`/api/pages/${id}`);
      const data = await res.json();

      if (res.ok) {
        // Open in new tab instead of modal
        const blob = new Blob([data.html_content], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const newWindow = window.open(url, "_blank");
        
        // Clean up the URL after a short delay
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        
        if (!newWindow) {
          alert("Popup bị chặn! Vui lòng cho phép popup cho trang này.");
        }
      } else {
        alert("Không thể tải trang: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      alert("Lỗi khi tải trang: " + err.message);
    }
  };

  window.downloadPage = async function (id) {
    try {
      const res = await fetch(`/api/pages/${id}`);
      const data = await res.json();

      if (res.ok) {
        const blob = new Blob([data.html_content], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${data.title.replace(/[^a-z0-9]/gi, "-").toLowerCase()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        alert("Không thể tải file: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      alert("Lỗi khi tải file: " + err.message);
    }
  };

  window.deletePage = async function (id) {
    if (!confirm("Bạn có chắc muốn xóa landing page này?")) return;

    try {
      const res = await fetch(`/api/pages/${id}`, {
        method: "DELETE",
      });

      if (res.ok) {
        // Remove card from DOM
        const card = document.querySelector(`.page-card[data-id="${id}"]`);
        if (card) {
          card.style.opacity = "0";
          card.style.transform = "scale(0.9)";
          setTimeout(() => {
            card.remove();
            allCards = Array.from(document.querySelectorAll(".page-card"));
            
            // Update total count
            const totalEl = document.getElementById("total-pages");
            if (totalEl) {
              totalEl.textContent = allCards.length;
            }
            
            // Show empty state if no cards
            if (allCards.length === 0) {
              galleryGrid.innerHTML = `
                <div class="empty-gallery">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  <h3>Chưa có landing page nào</h3>
                  <p>Hãy tạo landing page đầu tiên của bạn!</p>
                  <a href="/" class="btn-create">Tạo ngay</a>
                </div>
              `;
            }
          }, 250);
        }
      } else {
        const data = await res.json();
        alert("Không thể xóa: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      alert("Lỗi khi xóa: " + err.message);
    }
  };

  window.closeModal = function () {
    // Not used anymore - kept for compatibility
  };

  // Close modal on Escape - not used anymore
  document.addEventListener("keydown", (e) => {
    // Removed
  });
})();
