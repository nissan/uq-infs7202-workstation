// Toggle sidebar on mobile
document.getElementById('filterToggle')?.addEventListener('click', function() {
    document.getElementById('filterSidebar').classList.add('show');
});

document.getElementById('filterClose')?.addEventListener('click', function() {
    document.getElementById('filterSidebar').classList.remove('show');
});

// Filter section toggle
const toggleIcons = document.querySelectorAll('.toggle-icon');
toggleIcons.forEach(icon => {
    icon.addEventListener('click', function() {
        const content = this.parentElement.nextElementSibling;
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
        this.classList.toggle('bi-chevron-up');
        this.classList.toggle('bi-chevron-down');
    });
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('filterSidebar');
    const filterToggle = document.getElementById('filterToggle');
    
    if (!sidebar.contains(event.target) && event.target !== filterToggle && window.innerWidth < 992) {
        sidebar.classList.remove('show');
    }
});

// Handle filter reset
document.getElementById('resetFilters')?.addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('.filter-sidebar input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
});

// Handle filter application
document.getElementById('applyFilters')?.addEventListener('click', function() {
    const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
        .map(cb => cb.value);
    const selectedDifficulties = Array.from(document.querySelectorAll('input[name="difficulty"]:checked'))
        .map(cb => cb.value);
    
    // Build query string
    const params = new URLSearchParams();
    if (selectedCategories.length) params.append('categories', selectedCategories.join(','));
    if (selectedDifficulties.length) params.append('difficulties', selectedDifficulties.join(','));
    
    // Redirect with filters
    window.location.href = `${window.location.pathname}?${params.toString()}`;
});

// Handle search
let searchTimeout;
document.getElementById('courseSearch')?.addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const searchTerm = e.target.value.trim();
        if (searchTerm) {
            window.location.href = `${window.location.pathname}?search=${encodeURIComponent(searchTerm)}`;
        }
    }, 500);
});

// Handle sorting
document.querySelectorAll('.sort-dropdown .dropdown-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const sortBy = this.dataset.sort;
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('sort', sortBy);
        window.location.href = currentUrl.toString();
    });
}); 