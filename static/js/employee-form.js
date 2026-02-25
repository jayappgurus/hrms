document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('id_department');
    const designationSelect = document.getElementById('id_designation');
    const departmentHeadInput = document.getElementById('departmentHead');
    
    // Get all departments and designations from global variables
    let allDepartments = [];
    let allDesignations = [];
    
    // Try to get data from global variables (passed from Django template)
    if (typeof departmentsData !== 'undefined') {
        allDepartments = departmentsData;
    }
    if (typeof designationsData !== 'undefined') {
        allDesignations = designationsData;
    }
    
    /**
     * Load designations based on selected department
     */
    function loadDesignations(departmentId, preserveValue = null) {
        // Store current value if not explicitly provided
        const currentValue = preserveValue !== null ? preserveValue : designationSelect.value;
        
        // Clear current options
        designationSelect.innerHTML = '<option value="">Select Designation...</option>';
        
        if (!departmentId) {
            // If no department selected, disable designation
            designationSelect.disabled = true;
            departmentHeadInput.value = '';
            return;
        }
        
        // Filter designations by department
        const filteredDesignations = allDesignations.filter(function(designation) {
            return designation.department_id == departmentId;
        });
        
        if (filteredDesignations.length === 0) {
            designationSelect.innerHTML = '<option value="">No designations available</option>';
            designationSelect.disabled = true;
            return;
        }
        
        // Add filtered designations to dropdown
        filteredDesignations.forEach(function(designation) {
            const option = document.createElement('option');
            option.value = designation.id;
            option.textContent = designation.name;
            
            // Restore previously selected value if it matches
            if (currentValue && designation.id == currentValue) {
                option.selected = true;
            }
            
            designationSelect.appendChild(option);
        });
        
        designationSelect.disabled = false;
        
        // Update department head
        updateDepartmentHead(departmentId);
    }
    
    /**
     * Update department head based on selected department
     */
    function updateDepartmentHead(departmentId) {
        const department = allDepartments.find(function(dept) {
            return dept.id == departmentId;
        });
        
        if (department && department.head__full_name) {
            departmentHeadInput.value = department.head__full_name;
        } else {
            departmentHeadInput.value = '';
        }
    }
    
    // Event listeners
    if (departmentSelect) {
        departmentSelect.addEventListener('change', function() {
            const selectedDesignation = designationSelect.value;
            loadDesignations(this.value, selectedDesignation);
        });
        
        // Initialize on page load
        const initialDepartmentId = departmentSelect.value;
        const initialDesignationId = designationSelect.getAttribute('data-initial-value') || designationSelect.value;
        
        if (initialDepartmentId) {
            loadDesignations(initialDepartmentId, initialDesignationId);
        } else {
            designationSelect.disabled = true;
        }
    }
    
    // Form validation enhancement
    const form = document.getElementById('employeeForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validate department/designation relationship
            const departmentValue = departmentSelect.value;
            const designationValue = designationSelect.value;
            
            if (departmentValue && !designationValue) {
                e.preventDefault();
                alert('Please select a designation for the chosen department.');
                designationSelect.focus();
                return false;
            }
            
            // Validate designation belongs to department
            if (departmentValue && designationValue) {
                const designation = allDesignations.find(function(d) {
                    return d.id == designationValue;
                });
                
                if (designation && designation.department_id != departmentValue) {
                    e.preventDefault();
                    alert('Selected designation does not belong to the selected department. Please select a valid designation.');
                    designationSelect.focus();
                    return false;
                }
            }
            
            return true;
        });
    }
    
    // AJAX form validation (if enabled)
    const validateUrl = form.getAttribute('data-validate-url');
    if (validateUrl) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    }
    
    /**
     * Validate individual field via AJAX
     */
    function validateField(field) {
        const formData = new FormData(form);
        const fieldName = field.name;
        
        // Only validate if field has value and is not empty
        if (!field.value.trim()) {
            return;
        }
        
        fetch(validateUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.errors && data.errors[fieldName]) {
                showFieldError(field, data.errors[fieldName][0]);
            } else {
                clearFieldError(field);
            }
        })
        .catch(error => {
            console.error('Validation error:', error);
        });
    }
    
    /**
     * Show field error message
     */
    function showFieldError(field, message) {
        clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-danger small mt-1 field-error';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
        field.classList.add('is-invalid');
    }
    
    /**
     * Clear field error message
     */
    function clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.classList.remove('is-invalid');
    }
    
    /**
     * Get CSRF token from cookies
     */
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
});
