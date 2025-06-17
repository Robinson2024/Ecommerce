/**
 * Scripts modernos para lazy loading y optimizaciones de performance
 */

// ================================
// LAZY LOADING DE IMÁGENES
// ================================
class LazyImageLoader {
    constructor() {
        this.init();
    }

    init() {
        // Verificar soporte de Intersection Observer
        if ('IntersectionObserver' in window) {
            this.setupIntersectionObserver();
        } else {
            // Fallback para navegadores antiguos
            this.loadAllImages();
        }
    }

    setupIntersectionObserver() {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    this.loadImage(img);
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px', // Cargar 50px antes de que sea visible
            threshold: 0.1
        });

        // Observar todas las imágenes lazy
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    loadImage(img) {
        // Mostrar skeleton loader
        img.classList.add('loading');
        
        const tempImg = new Image();
        tempImg.onload = () => {
            // Imagen cargada exitosamente
            img.src = img.dataset.src;
            img.classList.remove('loading');
            img.classList.add('loaded');
            
            // Remover data-src
            delete img.dataset.src;
        };
        
        tempImg.onerror = () => {
            // Error cargando imagen
            img.classList.remove('loading');
            img.classList.add('error');
            img.src = '/static/images/placeholder-error.png'; // Imagen de error
        };
        
        tempImg.src = img.dataset.src;
    }

    loadAllImages() {
        // Fallback: cargar todas las imágenes inmediatamente
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
            delete img.dataset.src;
        });
    }
}

// ================================
// SISTEMA DE NOTIFICACIONES TOAST
// ================================
class ToastNotification {
    constructor() {
        this.container = this.createContainer();
        this.init();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    init() {
        // Escuchar eventos personalizados
        document.addEventListener('showToast', (e) => {
            this.show(e.detail);
        });
    }

    show(options = {}) {
        const {
            message = 'Notificación',
            type = 'info', // success, error, warning, info
            duration = 5000,
            closable = true
        } = options;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type} toast-enter`;
        
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">
                    ${this.getIcon(type)}
                </div>
                <div class="toast-message">${message}</div>
                ${closable ? '<button class="toast-close">&times;</button>' : ''}
            </div>
            <div class="toast-progress"></div>
        `;

        // Añadir al container
        this.container.appendChild(toast);

        // Animación de entrada
        setTimeout(() => {
            toast.classList.remove('toast-enter');
            toast.classList.add('toast-show');
        }, 10);

        // Manejar cierre
        if (closable) {
            const closeBtn = toast.querySelector('.toast-close');
            closeBtn.addEventListener('click', () => this.hide(toast));
        }

        // Auto-hide
        if (duration > 0) {
            const progressBar = toast.querySelector('.toast-progress');
            progressBar.style.animation = `toast-progress ${duration}ms linear`;
            
            setTimeout(() => {
                this.hide(toast);
            }, duration);
        }

        return toast;
    }

    hide(toast) {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-exit');
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    getIcon(type) {
        const icons = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-x-circle-fill"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>'
        };
        return icons[type] || icons.info;
    }
}

// ================================
// LOADING STATES Y SPINNERS
// ================================
class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.init();
    }

    init() {
        // Crear overlay global
        this.createGlobalOverlay();
        
        // Interceptar formularios
        this.setupFormInterception();
        
        // Interceptar HTMX requests
        this.setupHTMXInterception();
    }

    createGlobalOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'global-loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-text">Cargando...</div>
            </div>
        `;
        document.body.appendChild(overlay);
        this.globalOverlay = overlay;
    }

    show(target = null, text = 'Cargando...') {
        if (target) {
            // Loading específico para un elemento
            const loaderId = 'loader-' + Date.now();
            const loader = document.createElement('div');
            loader.id = loaderId;
            loader.className = 'local-loading';
            loader.innerHTML = `
                <div class="loading-spinner-small"></div>
                <span>${text}</span>
            `;
            
            target.style.position = 'relative';
            target.appendChild(loader);
            this.activeLoaders.add(loaderId);
            
            return () => this.hide(loaderId);
        } else {
            // Loading global
            this.globalOverlay.querySelector('.loading-text').textContent = text;
            this.globalOverlay.classList.add('active');
            document.body.classList.add('loading-active');
        }
    }

    hide(loaderId = null) {
        if (loaderId) {
            // Ocultar loader específico
            const loader = document.getElementById(loaderId);
            if (loader) {
                loader.classList.add('fade-out');
                setTimeout(() => {
                    loader.remove();
                    this.activeLoaders.delete(loaderId);
                }, 300);
            }
        } else {
            // Ocultar loader global
            this.globalOverlay.classList.remove('active');
            document.body.classList.remove('loading-active');
        }
    }

    setupFormInterception() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('no-loading')) return;
            
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Procesando...';
                
                // Restaurar después de 10 segundos como fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }, 10000);
            }
        });
    }

    setupHTMXInterception() {
        // Eventos HTMX
        document.addEventListener('htmx:beforeRequest', (e) => {
            const target = e.target;
            if (!target.classList.contains('no-loading')) {
                this.show(target, 'Actualizando...');
            }
        });

        document.addEventListener('htmx:afterRequest', (e) => {
            // Ocultar todos los loaders después de request HTMX
            this.activeLoaders.forEach(loaderId => this.hide(loaderId));
        });
    }
}

// ================================
// OPTIMIZACIONES DE PERFORMANCE
// ================================
class PerformanceOptimizer {
    constructor() {
        this.init();
    }

    init() {
        // Debounce para búsquedas
        this.setupSearchDebounce();
        
        // Prefetch para links importantes
        this.setupLinkPrefetch();
        
        // Optimización de imágenes
        this.setupImageOptimization();
        
        // Service Worker (si está disponible)
        this.setupServiceWorker();
    }

    setupSearchDebounce() {
        const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
        
        searchInputs.forEach(input => {
            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    // Disparar evento de búsqueda
                    const event = new CustomEvent('debouncedSearch', {
                        detail: { query: e.target.value, input: e.target }
                    });
                    document.dispatchEvent(event);
                }, 300);
            });
        });
    }

    setupLinkPrefetch() {
        // Prefetch automático para links importantes
        const importantLinks = document.querySelectorAll('a[data-prefetch]');
        
        const prefetchObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const link = entry.target;
                    this.prefetchLink(link.href);
                    prefetchObserver.unobserve(link);
                }
            });
        });

        importantLinks.forEach(link => {
            prefetchObserver.observe(link);
        });
    }

    prefetchLink(url) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }

    setupImageOptimization() {
        // Convertir imágenes a WebP si es soportado
        if (this.supportsWebP()) {
            document.querySelectorAll('img[data-webp]').forEach(img => {
                img.src = img.dataset.webp;
            });
        }
    }

    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registrado:', registration);
                })
                .catch(error => {
                    console.log('Error registrando Service Worker:', error);
                });
        }
    }
}

// ================================
// ANALYTICS Y TRACKING
// ================================
class AnalyticsTracker {
    constructor() {
        this.events = [];
        this.init();
    }

    init() {
        // Tracking de scroll
        this.setupScrollTracking();
        
        // Tracking de clicks
        this.setupClickTracking();
        
        // Tracking de tiempo en página
        this.setupTimeTracking();
        
        // Enviar datos periódicamente
        this.setupBatchSending();
    }

    track(event, data = {}) {
        const trackingData = {
            event: event,
            data: data,
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };

        this.events.push(trackingData);
        
        // Log para desarrollo
        console.log('📊 Analytics:', trackingData);
    }

    setupScrollTracking() {
        let maxScroll = 0;
        let scrollTimer;

        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round(
                (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
            );
            
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
                
                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(() => {
                    this.track('scroll_depth', { percent: maxScroll });
                }, 1000);
            }
        });
    }

    setupClickTracking() {
        document.addEventListener('click', (e) => {
            const target = e.target;
            
            // Tracking de botones importantes
            if (target.matches('[data-track]')) {
                this.track('click', {
                    element: target.dataset.track,
                    text: target.textContent.trim(),
                    href: target.href || null
                });
            }
        });
    }

    setupTimeTracking() {
        const startTime = Date.now();
        
        window.addEventListener('beforeunload', () => {
            const timeSpent = Date.now() - startTime;
            this.track('time_on_page', { duration: timeSpent });
            this.sendBatch(); // Enviar datos antes de salir
        });
    }

    setupBatchSending() {
        // Enviar datos cada 30 segundos
        setInterval(() => {
            this.sendBatch();
        }, 30000);
    }

    sendBatch() {
        if (this.events.length === 0) return;

        // Simular envío a servidor
        fetch('/analytics/track/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ events: this.events })
        })
        .then(() => {
            this.events = []; // Limpiar eventos enviados
        })
        .catch(error => {
            console.error('Error enviando analytics:', error);
        });
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// ================================
// INICIALIZACIÓN
// ================================
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar todos los módulos
    new LazyImageLoader();
    new ToastNotification();
    new LoadingManager();
    new PerformanceOptimizer();
    new AnalyticsTracker();
    
    console.log('🚀 Scripts modernos inicializados');
    
    // Ejemplo de uso de toast
    setTimeout(() => {
        document.dispatchEvent(new CustomEvent('showToast', {
            detail: {
                message: '¡Bienvenido a Tech Ecommerce!',
                type: 'success',
                duration: 3000
            }
        }));
    }, 1000);
});

// ================================
// UTILIDADES GLOBALES
// ================================
window.TechEcommerce = {
    showToast: (message, type = 'info', duration = 5000) => {
        document.dispatchEvent(new CustomEvent('showToast', {
            detail: { message, type, duration }
        }));
    },
    
    showLoading: (text = 'Cargando...') => {
        const loader = new LoadingManager();
        loader.show(null, text);
        return () => loader.hide();
    },
    
    track: (event, data = {}) => {
        // Acceso global al tracking
        const tracker = new AnalyticsTracker();
        tracker.track(event, data);
    }
};
