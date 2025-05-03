document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminSidebar = document.getElementById('adminSidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    
    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', function() {
            adminSidebar.classList.toggle('show');
            if (sidebarBackdrop) {
                sidebarBackdrop.classList.toggle('show');
            }
        });
        
        if (sidebarBackdrop) {
            sidebarBackdrop.addEventListener('click', function() {
                adminSidebar.classList.remove('show');
                sidebarBackdrop.classList.remove('show');
            });
        }
    }
    
    // Course progress tracking
    const progressButtons = document.querySelectorAll('.mark-complete-btn');
    progressButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const moduleId = this.dataset.moduleId;
            const courseSlug = this.dataset.courseSlug;
            
            fetch(`/courses/${courseSlug}/modules/${moduleId}/complete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    this.innerHTML = '<i class="bi bi-check-circle"></i> Completed';
                    updateProgress();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    // Quiz submission
    const quizForm = document.getElementById('quizForm');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const quizId = this.dataset.quizId;
            const formData = new FormData(this);
            
            fetch(`/quiz/${quizId}/submit/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.score !== undefined) {
                    showQuizResults(data);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Helper function to update progress indicators
    function updateProgress() {
        const progressBar = document.querySelector('.course-progress');
        if (progressBar) {
            const completed = document.querySelectorAll('.btn-success').length;
            const total = document.querySelectorAll('.mark-complete-btn').length;
            const percentage = (completed / total) * 100;
            
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            
            const progressText = document.querySelector('.progress-text');
            if (progressText) {
                progressText.textContent = `${Math.round(percentage)}% Complete`;
            }
        }
    }
    
    // Helper function to show quiz results
    function showQuizResults(data) {
        const resultsDiv = document.createElement('div');
        resultsDiv.className = 'quiz-results mt-4';
        resultsDiv.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h4 class="card-title">Quiz Results</h4>
                    <p class="card-text">Your score: ${data.score}%</p>
                    <div class="progress">
                        <div class="progress-bar ${data.score >= 70 ? 'bg-success' : 'bg-danger'}" 
                             role="progressbar" 
                             style="width: ${data.score}%" 
                             aria-valuenow="${data.score}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                    <p class="mt-3">
                        ${data.score >= 70 ? 
                            '<i class="bi bi-check-circle-fill text-success"></i> Congratulations! You passed the quiz.' :
                            '<i class="bi bi-x-circle-fill text-danger"></i> You did not pass. Please review the material and try again.'}
                    </p>
                </div>
            </div>
        `;
        
        const quizForm = document.getElementById('quizForm');
        quizForm.style.display = 'none';
        quizForm.parentNode.insertBefore(resultsDiv, quizForm.nextSibling);
    }
}); 