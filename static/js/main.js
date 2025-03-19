// Main JavaScript file for the Task Manager application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Task filter functionality
    const filterForm = document.getElementById('task-filter-form');
    if (filterForm) {
        filterForm.addEventListener('change', function() {
            this.submit();
        });
    }

    // Task search functionality
    const searchForm = document.getElementById('task-search-form');
    const searchInput = document.getElementById('search-input');
    if (searchForm && searchInput) {
        let typingTimer;
        const doneTypingInterval = 500; // ms

        searchInput.addEventListener('keyup', function() {
            clearTimeout(typingTimer);
            if (searchInput.value) {
                typingTimer = setTimeout(function() {
                    searchForm.submit();
                }, doneTypingInterval);
            }
        });
    }

    // Task status update via AJAX
    const statusButtons = document.querySelectorAll('.status-update-btn');
    if (statusButtons.length > 0) {
        statusButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const taskId = this.dataset.taskId;
                const newStatus = this.dataset.status;
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(`/api/tasks/${taskId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        status: newStatus
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Update UI
                    const statusBadge = document.getElementById(`status-badge-${taskId}`);
                    if (statusBadge) {
                        statusBadge.textContent = newStatus.replace('_', ' ').toUpperCase();
                        
                        // Remove old classes
                        statusBadge.classList.remove('bg-warning', 'bg-primary', 'bg-success', 'bg-danger');
                        
                        // Add the appropriate class based on the new status
                        switch(newStatus) {
                            case 'pending':
                                statusBadge.classList.add('bg-warning');
                                break;
                            case 'in_progress':
                                statusBadge.classList.add('bg-primary');
                                break;
                            case 'completed':
                                statusBadge.classList.add('bg-success');
                                break;
                            case 'cancelled':
                                statusBadge.classList.add('bg-danger');
                                break;
                        }
                    }
                    
                    // Show notification
                    showNotification('Task status updated successfully!', 'success');
                })
                .catch(error => {
                    console.error('Error updating task status:', error);
                    showNotification('Failed to update task status.', 'danger');
                });
            });
        });
    }

    // Profile picture preview
    const profileImageInput = document.getElementById('id_profile_picture');
    const profilePreview = document.getElementById('profile-preview');
    if (profileImageInput && profilePreview) {
        profileImageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Comment form submission via AJAX
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const taskId = this.dataset.taskId;
            const formData = new FormData(this);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/api/tasks/${taskId}/add_comment/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Create and append new comment
                const commentsContainer = document.getElementById('comments-container');
                const newComment = createCommentElement(data);
                commentsContainer.insertAdjacentHTML('beforeend', newComment);
                
                // Clear the comment form
                document.getElementById('id_content').value = '';
                
                // Show notification
                showNotification('Comment added successfully!', 'success');
            })
            .catch(error => {
                console.error('Error adding comment:', error);
                showNotification('Failed to add comment.', 'danger');
            });
        });
    }

    // Mark notification as read
    const notificationLinks = document.querySelectorAll('.notification-link');
    if (notificationLinks.length > 0) {
        notificationLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                // Don't prevent the link from working
                const notificationId = this.dataset.notificationId;
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Make AJAX request to mark as read
                fetch(`/api/notifications/${notificationId}/mark_read/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    
                    // Remove the unread class
                    this.closest('.notification').classList.remove('unread');
                    
                    // Update notification counter
                    const counter = document.getElementById('notification-counter');
                    if (counter) {
                        let count = parseInt(counter.textContent);
                        if (count > 0) {
                            count--;
                            counter.textContent = count;
                            if (count === 0) {
                                counter.style.display = 'none';
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Error marking notification as read:', error);
                });
            });
        });
    }

    // Helper function to create comment HTML
    function createCommentElement(comment) {
        const date = new Date(comment.created_at);
        const formattedDate = date.toLocaleString();
        
        return `
            <div class="comment">
                <div class="comment-header">
                    <span class="comment-author">${comment.user.username}</span>
                    <span class="comment-timestamp">${formattedDate}</span>
                </div>
                <div class="comment-content">
                    ${comment.content}
                </div>
            </div>
        `;
    }

    // Helper function to show notifications
    function showNotification(message, type) {
        const alertPlaceholder = document.getElementById('alert-container');
        if (!alertPlaceholder) return;
        
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertPlaceholder.append(wrapper);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = wrapper.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    // Due date validation
    const dueDateInput = document.getElementById('id_due_date');
    if (dueDateInput) {
        dueDateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const currentDate = new Date();
            
            if (selectedDate < currentDate) {
                this.classList.add('is-invalid');
                const feedbackElement = document.createElement('div');
                feedbackElement.classList.add('invalid-feedback');
                feedbackElement.textContent = 'Due date cannot be in the past';
                
                const existingFeedback = this.nextElementSibling;
                if (existingFeedback && existingFeedback.classList.contains('invalid-feedback')) {
                    existingFeedback.remove();
                }
                
                this.parentNode.appendChild(feedbackElement);
            } else {
                this.classList.remove('is-invalid');
                const existingFeedback = this.nextElementSibling;
                if (existingFeedback && existingFeedback.classList.contains('invalid-feedback')) {
                    existingFeedback.remove();
                }
            }
        });
    }
});
