/**
 * AJAX Form Validation Utility
 * Provides real-time form validation using Django's form validation
 */

class FormValidator {
    constructor(formId, validationUrl, options = {}) {
        this.form = document.getElementById(formId);
        this.validationUrl = validationUrl;
        this.options = {
            validateOnBlur: true,
            validateOnChange: false,
            showSuccessIndicator: true,
            debounceDelay: 500,
            ...options
        };
        
        if (!this.form) {
            console.error(`Form with id "${formId}" not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        // Add validation listeners to all form fields
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            if (this.options.validateOnBlur) {
                field.addEventListener('blur', () => this.validateField(field));
            }
            
            if (this.options.validateOnChange) {
                field.addEventListener('input', this.debounce(() => {
                    this.validateField(field);
                }, this.options.debounceDelay));
            }
        });
        
        // Validate entire form on submit
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.validateForm();
        });
    }
    
    async validateField(field) {
        const fieldName = field.name;
        if (!fieldName) return;
        
        const formData = new FormData();
        formData.append('field_name', fieldName);
        formData.append('field_value', field.value);
        
        // Add all form data for context-dependent validation
        const allFormData = new FormData(this.form);
        for (let [key, value] of allFormData.entries()) {
            formData.append(key, value);
        }
        
        try {
            const response = await fetch(this.validationUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            const data = await response.json();
            
            if (data.valid) {
                this.showFieldSuccess(field);
            } else {
                // Handle different error formats
                let errorMessage = 'Invalid value';
                
                // Debug logging
                console.log('Field:', fieldName);
                console.log('Data errors:', data.errors);
                console.log('Field error exists:', !!(data.errors && data.errors[fieldName]));
                
                if (data.errors && data.errors[fieldName]) {
                    errorMessage = Array.isArray(data.errors[fieldName]) 
                        ? data.errors[fieldName][0] 
                        : data.errors[fieldName];
                    console.log('Using specific error:', errorMessage);
                } else {
                    // Try to find any error that contains the field name
                    for (let [errorField, errorValue] of Object.entries(data.errors || {})) {
                        if (errorField.toLowerCase().includes(fieldName.toLowerCase()) || 
                            fieldName.toLowerCase().includes(errorField.toLowerCase())) {
                            errorMessage = Array.isArray(errorValue) ? errorValue[0] : errorValue;
                            console.log('Found matching error:', errorMessage);
                            break;
                        }
                    }
                }
                
                this.showFieldError(field, errorMessage);
            }
        } catch (error) {
            console.error('Validation error:', error);
        }
    }
    
    async validateForm() {
        const formData = new FormData(this.form);
        
        try {
            const response = await fetch(this.validationUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            const data = await response.json();
            
            if (data.valid) {
                // All validation passed, submit the form
                this.clearAllErrors();
                this.form.submit();
            } else {
                // Show all errors
                this.clearAllErrors();
                for (let [fieldName, errors] of Object.entries(data.errors)) {
                    const field = this.form.querySelector(`[name="${fieldName}"]`);
                    if (field) {
                        // Handle different error formats
                        let errorMessage = Array.isArray(errors) ? errors[0] : errors;
                        this.showFieldError(field, errorMessage);
                    }
                }
                
                // Scroll to first error
                const firstError = this.form.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        } catch (error) {
            console.error('Form validation error:', error);
            // If validation fails, allow normal form submission
            this.form.submit();
        }
    }
    
    showFieldError(field, errors) {
        // Remove existing validation classes
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Remove existing error messages
        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = Array.isArray(errors) ? errors[0] : errors;
        field.parentElement.appendChild(errorDiv);
    }
    
    showFieldSuccess(field) {
        if (!this.options.showSuccessIndicator) return;
        
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Remove error messages
        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
    
    clearFieldValidation(field) {
        field.classList.remove('is-valid', 'is-invalid');
        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
    
    clearAllErrors() {
        const fields = this.form.querySelectorAll('.is-invalid, .is-valid');
        fields.forEach(field => this.clearFieldValidation(field));
    }
    
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Auto-initialize forms with data-validate attribute
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('[data-validate]');
    forms.forEach(form => {
        const validationUrl = form.getAttribute('data-validate-url');
        if (validationUrl) {
            new FormValidator(form.id, validationUrl, {
                validateOnBlur: form.getAttribute('data-validate-on-blur') !== 'false',
                validateOnChange: form.getAttribute('data-validate-on-change') === 'true',
                showSuccessIndicator: form.getAttribute('data-show-success') !== 'false'
            });
        }
    });
});
