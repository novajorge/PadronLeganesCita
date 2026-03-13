/**
 * Cita Previa Padrón Leganés - Frontend Application
 * Handles form validation and API submission
 */

(function() {
    'use strict';

    // Configuration - auto-detect API URL
    const API_BASE = window.location.origin;
    const API_URL = API_BASE + '/api/usuarios';
    const API_CITAS = API_BASE + '/api/citas';
    const API_ESTADISTICAS = API_BASE + '/api/citas/estadisticas';

    // DOM Elements
    const form = document.getElementById('registration-form');
    const submitBtn = document.getElementById('submit-btn');
    const successMessage = document.getElementById('success-message');
    const registerAnotherBtn = document.getElementById('register-another');
    const telegramHelpBtn = document.getElementById('telegram-help-btn');
    const telegramModal = document.getElementById('telegram-modal');
    const modalCloseButtons = document.querySelectorAll('[data-close-modal]');

    // Form fields
    const nombreInput = document.getElementById('nombre');
    const emailInput = document.getElementById('email');
    const telefonoInput = document.getElementById('telefono');
    const telegramInput = document.getElementById('telegram');
    const notifEmail = document.getElementById('notif-email');
    const notifTelegram = document.getElementById('notif-telegram');
    const notifWhatsapp = document.getElementById('notif-whatsapp');

    // Error elements
    const nombreError = document.getElementById('nombre-error');
    const emailError = document.getElementById('email-error');
    const telefonoError = document.getElementById('telefono-error');
    const telegramError = document.getElementById('telegram-error');
    const channelsError = document.getElementById('channels-error');

    /**
     * Validation functions
     */
    const validators = {
        nombre: {
            validate: (value) => {
                if (!value || value.trim().length < 2) {
                    return 'El nombre debe tener al menos 2 caracteres';
                }
                return null;
            }
        },
        email: {
            validate: (value) => {
                if (!value || !value.trim()) {
                    return 'El email es obligatorio';
                }
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    return 'Por favor, introduce un email válido';
                }
                return null;
            }
        },
        telefono: {
            validate: (value) => {
                if (!value || !value.trim()) {
                    return 'El teléfono es obligatorio';
                }
                const phoneRegex = /^\+34[0-9]{9}$/;
                if (!phoneRegex.test(value)) {
                    return 'Formato válido: +34 seguido de 9 dígitos (ej: +34612345678)';
                }
                return null;
            }
        },
        telegram: {
            validate: (value) => {
                // Optional field, but if provided, validate format
                if (value && value.trim()) {
                    const telegramRegex = /^[0-9]{5,15}$/;
                    if (!telegramRegex.test(value.trim())) {
                        return 'El Chat ID debe ser un número';
                    }
                }
                return null;
            }
        }
    };

    /**
     * Show error message for a field
     */
    function showError(inputElement, errorElement, message) {
        if (message) {
            inputElement.classList.add('error');
            errorElement.textContent = message;
        } else {
            clearError(inputElement, errorElement);
        }
    }

    /**
     * Clear error for a field
     */
    function clearError(inputElement, errorElement) {
        inputElement.classList.remove('error');
        errorElement.textContent = '';
    }

    /**
     * Validate notification channels
     */
    function validateChannels() {
        const channels = [
            notifEmail.checked,
            notifTelegram.checked,
            notifWhatsapp.checked
        ];

        if (!channels.some(Boolean)) {
            return 'Selecciona al menos un canal de notificación';
        }

        // If Telegram is selected but no Chat ID provided
        if (notifTelegram.checked && !telegramInput.value.trim()) {
            return 'Necesitas tu Chat ID de Telegram para recibir notificaciones';
        }

        return null;
    }

    /**
     * Validate entire form
     */
    function validateForm() {
        let isValid = true;
        let firstErrorField = null;

        // Validate nombre
        const nombreErrorMsg = validators.nombre.validate(nombreInput.value);
        if (nombreErrorMsg) {
            showError(nombreInput, nombreError, nombreErrorMsg);
            isValid = false;
            firstErrorField = firstErrorField || nombreInput;
        } else {
            clearError(nombreInput, nombreError);
        }

        // Validate email
        const emailErrorMsg = validators.email.validate(emailInput.value);
        if (emailErrorMsg) {
            showError(emailInput, emailError, emailErrorMsg);
            isValid = false;
            firstErrorField = firstErrorField || emailInput;
        } else {
            clearError(emailInput, emailError);
        }

        // Validate telefono
        const telefonoErrorMsg = validators.telefono.validate(telefonoInput.value);
        if (telefonoErrorMsg) {
            showError(telefonoInput, telefonoError, telefonoErrorMsg);
            isValid = false;
            firstErrorField = firstErrorField || telefonoInput;
        } else {
            clearError(telefonoInput, telefonoError);
        }

        // Validate telegram
        const telegramErrorMsg = validators.telegram.validate(telegramInput.value);
        if (telegramErrorMsg) {
            showError(telegramInput, telegramError, telegramErrorMsg);
            isValid = false;
            firstErrorField = firstErrorField || telegramInput;
        } else {
            clearError(telegramInput, telegramError);
        }

        // Validate channels
        const channelsErrorMsg = validateChannels();
        if (channelsErrorMsg) {
            channelsError.textContent = channelsErrorMsg;
            isValid = false;
            firstErrorField = firstErrorField || notifEmail;
        } else {
            channelsError.textContent = '';
        }

        // Focus first error field
        if (firstErrorField) {
            firstErrorField.focus();
        }

        return isValid;
    }

    /**
     * Get form data as JSON
     */
    function getFormData() {
        return {
            name: nombreInput.value.trim(),
            email: emailInput.value.trim(),
            phone: telefonoInput.value.trim(),
            telegram_chat_id: telegramInput.value.trim() || null,
            notification_channels: {
                email: notifEmail.checked,
                telegram: notifTelegram.checked,
                whatsapp: notifWhatsapp.checked
            }
        };
    }

    /**
     * Show loading state
     */
    function showLoading() {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
    }

    /**
     * Hide loading state
     */
    function hideLoading() {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }

    /**
     * Show success message
     */
    function showSuccess() {
        form.style.display = 'none';
        successMessage.hidden = false;
        successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Reset form to initial state
     */
    function resetForm() {
        form.reset();
        form.style.display = 'block';
        successMessage.hidden = true;

        // Clear all errors
        clearError(nombreInput, nombreError);
        clearError(emailInput, emailError);
        clearError(telefonoInput, telefonoError);
        clearError(telegramInput, telegramError);
        channelsError.textContent = '';

        // Set email checkbox as checked by default
        notifEmail.checked = true;
    }

    /**
     * Submit form to API
     */
    async function submitForm() {
        if (!validateForm()) {
            return;
        }

        showLoading();

        const data = getFormData();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                showSuccess();
            } else {
                // Handle API errors
                const errorMessage = result.detail || result.message || 'Error al registrar. Por favor, inténtalo de nuevo.';
                alert(errorMessage);
                hideLoading();
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Error de conexión. Por favor, inténtalo de nuevo más tarde.');
            hideLoading();
        }
    }

    /**
     * Modal functions
     */
    function openModal() {
        telegramModal.hidden = false;
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        telegramModal.hidden = true;
        document.body.style.overflow = '';
    }

    /**
     * Event Listeners
     */

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitForm();
    });

    // Real-time validation on blur
    nombreInput.addEventListener('blur', function() {
        const error = validators.nombre.validate(this.value);
        showError(this, nombreError, error);
    });

    emailInput.addEventListener('blur', function() {
        const error = validators.email.validate(this.value);
        showError(this, emailError, error);
    });

    telefonoInput.addEventListener('blur', function() {
        const error = validators.telefono.validate(this.value);
        showError(this, telefonoError, error);
    });

    telegramInput.addEventListener('blur', function() {
        const error = validators.telegram.validate(this.value);
        showError(this, telegramError, error);
    });

    // Clear error on input
    nombreInput.addEventListener('input', function() {
        clearError(this, nombreError);
    });

    emailInput.addEventListener('input', function() {
        clearError(this, emailError);
    });

    telefonoInput.addEventListener('input', function() {
        clearError(this, telefonoError);
    });

    telegramInput.addEventListener('input', function() {
        clearError(this, telegramError);
    });

    // Telegram help modal
    telegramHelpBtn.addEventListener('click', function() {
        openModal();
    });

    modalCloseButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            closeModal();
        });
    });

    // Close modal on overlay click
    telegramModal.addEventListener('click', function(e) {
        if (e.target === telegramModal) {
            closeModal();
        }
    });

    // Close modal on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !telegramModal.hidden) {
            closeModal();
        }
    });

    // Register another
    registerAnotherBtn.addEventListener('click', function() {
        resetForm();
    });

    // Smooth scroll for hero CTA
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ========================================
    // Calendario functionality
    // ========================================

    const calendarioList = document.getElementById('calendario-list');
    const calendarioLoading = document.getElementById('calendario-loading');
    const calendarioEmpty = document.getElementById('calendario-empty');
    const citasList = document.getElementById('citas-list');
    const refreshBtn = document.getElementById('refresh-calendar');

    // Elements for stats
    const totalChecksEl = document.getElementById('total-checks');
    const citasEncontradasEl = document.getElementById('citas-encontradas');
    const ultimaActualizacionEl = document.getElementById('ultima-actualizacion');

    /**
     * Format date for display
     */
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Generate calendar grid for a month
     */
    function generateCalendarGrid(year, month, citasMap) {
        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        const dayNames = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Adjust for Monday start (0 = Monday, 6 = Sunday)
        const startDay = firstDay === 0 ? 6 : firstDay - 1;

        let html = '<div class="calendar-month">';
        html += '<div class="calendar-header">';
        html += '<h3 class="calendar-title">' + monthNames[month] + ' ' + year + '</h3>';
        html += '</div>';

        // Day names
        html += '<div class="calendar-weekdays">';
        dayNames.forEach(function(day) {
            html += '<div class="calendar-weekday">' + day + '</div>';
        });
        html += '</div>';

        // Calendar grid
        html += '<div class="calendar-grid">';

        // Empty cells before first day
        for (let i = 0; i < startDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }

        // Days
        for (let day = 1; day <= daysInMonth; day++) {
            const dateKey = day + '/' + (month + 1) + '/' + year;
            const citasDia = citasMap[dateKey] || [];
            const tieneCitas = citasDia.length > 0;
            const esHoy = false; // Could check if it's today

            html += '<div class="calendar-day' + (tieneCitas ? ' has-citas' : '') + (esHoy ? ' today' : '') + '">';
            html += '<span class="day-number">' + day + '</span>';

            if (tieneCitas) {
                html += '<div class="day-citas">';
                // Show up to 3 hours
                citasDia.slice(0, 3).forEach(function(cita) {
                    html += '<span class="cita-hour">' + cita.hora + '</span>';
                });
                if (citasDia.length > 3) {
                    html += '<span class="cita-more">+' + (citasDia.length - 3) + '</span>';
                }
                html += '</div>';
            } else {
                html += '<span class="no-citas">-</span>';
            }

            html += '</div>';
        }

        html += '</div>'; // calendar-grid
        html += '</div>'; // calendar-month

        return html;
    }

    /**
     * Load citas from API
     */
    async function loadCitas() {
        if (!calendarioList) return;

        try {
            // Load stats
            const statsResponse = await fetch(API_ESTADISTICAS);
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                totalChecksEl.textContent = stats.total_comprobaciones || 0;
                citasEncontradasEl.textContent = stats.citas_encontradas || 0;

                if (stats.ultima_actualizacion) {
                    ultimaActualizacionEl.textContent = formatDate(stats.ultima_actualizacion);
                }
            }

            // Load citas
            const response = await fetch(API_CITAS);
            if (!response.ok) {
                throw new Error('Error loading citas');
            }

            const citas = await response.json();

            calendarioLoading.hidden = true;

            if (!citas || citas.length === 0) {
                calendarioEmpty.hidden = false;
                return;
            }

            // Show calendar
            citasList.hidden = false;

            // Group citas by date
            const citasMap = {};
            citas.forEach(function(cita) {
                if (cita.hay_citas && cita.detalles) {
                    // Parse details like "16/04/2026 08:00 - Padrón 1"
                    const match = cita.detalles.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{2}:\d{2})/);
                    if (match) {
                        const fecha = match[1] + '/' + match[2] + '/' + match[3];
                        const hora = match[4];
                        const unidad = cita.detalles.split(' - ')[1] || 'Padrón';

                        if (!citasMap[fecha]) {
                            citasMap[fecha] = [];
                        }
                        citasMap[fecha].push({ hora: hora, unidad: unidad });
                    }
                }
            });

            // Generate calendar for current and next month
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth();

            let calendarHtml = '';

            // Current month
            calendarHtml += generateCalendarGrid(currentYear, currentMonth, citasMap);

            // Next month
            const nextMonth = currentMonth + 1;
            const nextYear = currentMonth === 11 ? currentYear + 1 : currentYear;
            const actualNextMonth = currentMonth === 11 ? 0 : nextMonth;
            calendarHtml += generateCalendarGrid(nextYear, actualNextMonth, citasMap);

            citasList.innerHTML = '<div class="calendarios-container">' + calendarHtml + '</div>';

        } catch (error) {
            console.error('Error loading citas:', error);
            calendarioLoading.hidden = true;
            calendarioEmpty.hidden = false;
        }
    }

    // Load citas on page load if element exists
    if (calendarioList) {
        loadCitas();

        // Refresh button
        if (refreshBtn) {
            refreshBtn.addEventListener('click', function() {
                calendarioLoading.hidden = false;
                calendarioEmpty.hidden = true;
                citasList.hidden = true;
                loadCitas();
            });
        }
    }

})();
