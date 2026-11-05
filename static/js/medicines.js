/**
 * MediMitra – Medicines Management JavaScript
 * Client-side search and dynamic interaction helpers.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMedicineSearch();
    highlightExpiries();
});

function initMedicineSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    const tableBody = document.querySelector('tbody');
    if (!searchInput || !tableBody) return;

    // Real-time client-side filter in addition to server query
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const rows = tableBody.querySelectorAll('tr');
        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    });
}

function highlightExpiries() {
    const today = new Date();
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const expiryCell = row.children[3];
        if (!expiryCell) return;
        const text = expiryCell.innerText.trim();
        if (text && text !== 'Not recorded') {
            const exp = new Date(text);
            if (!isNaN(exp.getTime())) {
                if (exp < today) {
                    expiryCell.innerHTML = `<span class="tag tag-danger" title="Expired">${text}</span>`;
                } else if ((exp - today) / (1000 * 60 * 60 * 24) < 30) {
                    expiryCell.innerHTML = `<span class="tag tag-warning" title="Expiring within 30 days">${text}</span>`;
                }
            }
        }
    });
}
