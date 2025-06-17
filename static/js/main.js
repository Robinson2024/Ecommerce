/**
 * Script principal para Tech Ecommerce
 * Maneja funcionalidades básicas del sitio
 */

(function() {
    'use strict';

    // Configuración global
    const Config = {
        CSRF_TOKEN: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
        API_BASE_URL: '/api/v1/',
        TOAST_DURATION: 5000,
        DEBOUNCE_DELAY: 300
    };

    // Utilidades
    const Utils = {
        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Mostrar toast notification
        showToast: function(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type} show`;
            toast.innerHTML = `
                <div class="toast-header">
                    <i class="bi bi-${this.getToastIcon(type)} me-2"></i>
                    <strong class="me-auto">${this.getToastTitle(type)}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">${message}</div>
            `;

            // Agregar al contenedor
            const container = document.querySelector('.toast-container') || this.createToastContainer();
            container.appendChild(toast);

            // Auto-remove después de 5 segundos
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, Config.TOAST_DURATION);
        },

        getToastIcon: function(type) {
            const icons = {
                'success': 'check-circle',
                'error': 'x-circle',
                'warning': 'exclamation-triangle',
                'info': 'info-circle'
            };
            return icons[type] || 'info-circle';
        },

        getToastTitle: function(type) {
            const titles = {
                'success': 'Éxito',
                'error': 'Error',
                'warning': 'Advertencia',
                'info': 'Información'
            };
            return titles[type] || 'Información';
        },

        createToastContainer: function() {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
            return container;
        },

        // Loading state para botones
        setButtonLoading: function(button, loading = true) {
            if (loading) {
                button.disabled = true;
                button.dataset.originalText = button.innerHTML;
                button.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Cargando...
                `;
            } else {
                button.disabled = false;
                button.innerHTML = button.dataset.originalText || button.innerHTML;
            }
        },

        // Hacer request AJAX
        makeRequest: function(url, options = {}) {
            const defaults = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Config.CSRF_TOKEN
                }
            };

            const config = { ...defaults, ...options };
            
            return fetch(url, config)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('Request failed:', error);
                    this.showToast('Error en la conexión', 'error');
                    throw error;
                });
        }
    };

    // Manejo del carrito
    const CartManager = {
        init: function() {
            this.bindEvents();
            this.updateCartBadge();
        },

        bindEvents: function() {
            // Agregar al carrito
            document.addEventListener('click', (e) => {
                if (e.target.matches('.add-to-cart, .add-to-cart *')) {
                    e.preventDefault();
                    const button = e.target.closest('.add-to-cart');
                    this.addToCart(button);
                }
            });

            // Actualizar cantidad
            document.addEventListener('change', (e) => {
                if (e.target.matches('.cart-quantity')) {
                    this.updateQuantity(e.target);
                }
            });

            // Remover del carrito
            document.addEventListener('click', (e) => {
                if (e.target.matches('.remove-from-cart, .remove-from-cart *')) {
                    e.preventDefault();
                    const button = e.target.closest('.remove-from-cart');
                    this.removeFromCart(button);
                }
            });
        },

        addToCart: function(button) {
            const productId = button.dataset.productId;
            const quantity = button.dataset.quantity || 1;

            Utils.setButtonLoading(button, true);

            Utils.makeRequest('/cart/add/', {
                method: 'POST',
                body: JSON.stringify({
                    product_id: productId,
                    quantity: parseInt(quantity)
                })
            })
            .then(data => {
                Utils.showToast('Producto agregado al carrito', 'success');
                this.updateCartBadge();
                this.updateMiniCart();
            })
            .catch(error => {
                Utils.showToast('Error al agregar producto', 'error');
            })
            .finally(() => {
                Utils.setButtonLoading(button, false);
            });
        },

        updateQuantity: function(input) {
            const itemId = input.dataset.itemId;
            const quantity = parseInt(input.value);

            if (quantity < 1) {
                input.value = 1;
                return;
            }

            const debounced = Utils.debounce(() => {
                Utils.makeRequest('/cart/update/', {
                    method: 'POST',
                    body: JSON.stringify({
                        item_id: itemId,
                        quantity: quantity
                    })
                })
                .then(data => {
                    this.updateCartTotals(data);
                    Utils.showToast('Cantidad actualizada', 'info');
                });
            }, Config.DEBOUNCE_DELAY);

            debounced();
        },

        removeFromCart: function(button) {
            const itemId = button.dataset.itemId;

            if (confirm('¿Estás seguro de que deseas eliminar este producto?')) {
                Utils.makeRequest('/cart/remove/', {
                    method: 'POST',
                    body: JSON.stringify({
                        item_id: itemId
                    })
                })
                .then(data => {
                    const itemRow = button.closest('.cart-item');
                    if (itemRow) {
                        itemRow.remove();
                    }
                    this.updateCartBadge();
                    this.updateCartTotals(data);
                    Utils.showToast('Producto eliminado', 'info');
                });
            }
        },

        updateCartBadge: function() {
            Utils.makeRequest('/cart/count/')
                .then(data => {
                    const badges = document.querySelectorAll('.cart-badge');
                    badges.forEach(badge => {
                        badge.textContent = data.count || 0;
                        badge.style.display = data.count > 0 ? 'inline' : 'none';
                    });
                });
        },

        updateMiniCart: function() {
            // Actualizar mini carrito si existe
            const miniCart = document.querySelector('.mini-cart');
            if (miniCart) {
                Utils.makeRequest('/cart/mini/')
                    .then(data => {
                        miniCart.innerHTML = data.html;
                    });
            }
        },

        updateCartTotals: function(data) {
            // Actualizar totales en la página del carrito
            if (data.subtotal !== undefined) {
                const subtotalElements = document.querySelectorAll('.cart-subtotal');
                subtotalElements.forEach(el => el.textContent = data.subtotal);
            }
            
            if (data.total !== undefined) {
                const totalElements = document.querySelectorAll('.cart-total');
                totalElements.forEach(el => el.textContent = data.total);
            }
        }
    };

    // Manejo de formularios
    const FormManager = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            // Validación en tiempo real
            document.addEventListener('input', (e) => {
                if (e.target.matches('input[required], textarea[required], select[required]')) {
                    this.validateField(e.target);
                }
            });

            // Submit de formularios AJAX
            document.addEventListener('submit', (e) => {
                if (e.target.matches('.ajax-form')) {
                    e.preventDefault();
                    this.submitAjaxForm(e.target);
                }
            });
        },

        validateField: function(field) {
            const isValid = field.checkValidity();
            
            // Remover clases anteriores
            field.classList.remove('is-valid', 'is-invalid');
            
            // Agregar clase según validación
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');

            // Mostrar mensaje de error personalizado
            const feedback = field.parentNode.querySelector('.invalid-feedback');
            if (feedback && !isValid) {
                feedback.textContent = this.getErrorMessage(field);
            }
        },

        getErrorMessage: function(field) {
            if (field.validity.valueMissing) {
                return 'Este campo es obligatorio';
            }
            if (field.validity.typeMismatch) {
                return 'Por favor ingresa un formato válido';
            }
            if (field.validity.tooShort) {
                return `Mínimo ${field.minLength} caracteres`;
            }
            if (field.validity.tooLong) {
                return `Máximo ${field.maxLength} caracteres`;
            }
            if (field.validity.patternMismatch) {
                return 'El formato no es válido';
            }
            return 'Valor inválido';
        },

        submitAjaxForm: function(form) {
            const submitButton = form.querySelector('button[type="submit"]');
            Utils.setButtonLoading(submitButton, true);

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            Utils.makeRequest(form.action, {
                method: form.method.toUpperCase(),
                body: JSON.stringify(data)
            })
            .then(response => {
                if (response.success) {
                    Utils.showToast(response.message || 'Operación exitosa', 'success');
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    }
                } else {
                    Utils.showToast(response.message || 'Error en el formulario', 'error');
                }
            })
            .catch(error => {
                Utils.showToast('Error al procesar el formulario', 'error');
            })
            .finally(() => {
                Utils.setButtonLoading(submitButton, false);
            });
        }
    };

    // Búsqueda en tiempo real
    const SearchManager = {
        init: function() {
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                this.bindSearchEvents(searchInput);
            }
        },

        bindSearchEvents: function(input) {
            const debouncedSearch = Utils.debounce((query) => {
                this.performSearch(query);
            }, Config.DEBOUNCE_DELAY);

            input.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                if (query.length >= 2) {
                    debouncedSearch(query);
                } else {
                    this.hideSearchResults();
                }
            });

            // Cerrar resultados al hacer clic fuera
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-container')) {
                    this.hideSearchResults();
                }
            });
        },

        performSearch: function(query) {
            Utils.makeRequest(`/api/search/?q=${encodeURIComponent(query)}`)
                .then(data => {
                    this.displaySearchResults(data.results);
                });
        },

        displaySearchResults: function(results) {
            let resultsContainer = document.querySelector('.search-results');
            
            if (!resultsContainer) {
                resultsContainer = this.createSearchResultsContainer();
            }

            if (results.length === 0) {
                resultsContainer.innerHTML = '<div class="p-3 text-muted">No se encontraron resultados</div>';
            } else {
                const html = results.map(item => `
                    <a href="${item.url}" class="search-result-item d-block p-3 text-decoration-none border-bottom">
                        <div class="d-flex align-items-center">
                            <img src="${item.image}" alt="${item.title}" class="search-result-image me-3">
                            <div>
                                <div class="fw-bold">${item.title}</div>
                                <div class="text-muted small">${item.price}</div>
                            </div>
                        </div>
                    </a>
                `).join('');
                
                resultsContainer.innerHTML = html;
            }

            resultsContainer.style.display = 'block';
        },

        createSearchResultsContainer: function() {
            const container = document.createElement('div');
            container.className = 'search-results position-absolute bg-white shadow-lg rounded border';
            container.style.top = '100%';
            container.style.left = '0';
            container.style.right = '0';
            container.style.zIndex = '1000';
            container.style.maxHeight = '400px';
            container.style.overflowY = 'auto';
            
            const searchContainer = document.querySelector('.search-container');
            if (searchContainer) {
                searchContainer.style.position = 'relative';
                searchContainer.appendChild(container);
            }
            
            return container;
        },

        hideSearchResults: function() {
            const resultsContainer = document.querySelector('.search-results');
            if (resultsContainer) {
                resultsContainer.style.display = 'none';
            }
        }
    };

    // Inicialización cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Tech Ecommerce JS initialized');
        
        // Inicializar módulos
        CartManager.init();
        FormManager.init();
        SearchManager.init();

        // Inicializar tooltips de Bootstrap si está disponible
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // Smooth scrolling para anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Lazy loading de imágenes si no hay soporte nativo
        if ('IntersectionObserver' in window) {
            const images = document.querySelectorAll('img[data-src]');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        }
    });    // Exponer utilidades globalmente para uso en templates
    window.TechEcommerce = {
        Utils,
        CartManager,
        FormManager,
        SearchManager
    };
    
    // Exponer showToast globalmente para compatibilidad
    window.showToast = Utils.showToast;

})();
