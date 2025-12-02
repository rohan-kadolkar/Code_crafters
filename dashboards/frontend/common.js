/**
 * ============================================
 * STUDENT DROPOUT PREDICTION SYSTEM
 * Common JavaScript Utilities
 * Version: 1.0.0
 * ============================================
 */

// ============================================
// Configuration
// ============================================
const CONFIG = {
  API_BASE: 'http://localhost:5000/api',
  TOKEN_KEY: 'auth_token',
  USER_KEY: 'user_data',
  ROLE_KEY: 'user_role',
  TIMEOUT: 30000, // 30 seconds
};

// ============================================
// Authentication Utilities
// ============================================
const Auth = {
  /**
   * Save authentication token
   * @param {string} token - JWT token
   */
  setToken(token) {
    try {
      localStorage.setItem(CONFIG.TOKEN_KEY, token);
      console.log('✅ Token saved');
    } catch (e) {
      console.error('❌ Failed to save token:', e);
    }
  },

  /**
   * Get authentication token
   * @returns {string|null} - Token or null
   */
  getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
  },

  /**
   * Save user data
   * @param {object} userData - User information
   */
  setUser(userData) {
    try {
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(userData));
      console.log('✅ User data saved');
    } catch (e) {
      console.error('❌ Failed to save user data:', e);
    }
  },

  /**
   * Get user data
   * @returns {object|null} - User data or null
   */
  getUser() {
    try {
      const data = localStorage.getItem(CONFIG.USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      console.error('❌ Failed to parse user data:', e);
      return null;
    }
  },

  /**
   * Save user role
   * @param {string} role - User role (teacher, student, parent, admin)
   */
  setRole(role) {
    localStorage.setItem(CONFIG.ROLE_KEY, role);
  },

  /**
   * Get user role
   * @returns {string|null} - Role or null
   */
  getRole() {
    return localStorage.getItem(CONFIG.ROLE_KEY);
  },

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.getToken();
  },

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
    localStorage.removeItem(CONFIG.ROLE_KEY);
    console.log('✅ User logged out');
    window.location.href = 'login.html';
  },

  /**
   * Redirect to appropriate dashboard based on role
   */
  redirectToDashboard() {
    const role = this.getRole();
    const dashboards = {
      teacher: 'index.html',
      student: 'student.html',
      parent: 'parent.html',
      admin: 'admin.html'
    };
    window.location.href = dashboards[role] || 'login.html';
  },

  /**
   * Check authentication and redirect if not logged in
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      console.warn('⚠️ User not authenticated, redirecting to login');
      window.location.href = 'login.html';
      return false;
    }
    return true;
  }
};

// ============================================
// API Utilities
// ============================================
const API = {
  /**
   * Generic fetch wrapper with error handling
   * @param {string} endpoint - API endpoint
   * @param {object} options - Fetch options
   * @returns {Promise<object>} - Response data
   */
  async request(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE}${endpoint}`;
    const token = Auth.getToken();
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      timeout: CONFIG.TIMEOUT
    };

    const mergedOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers
      }
    };

    try {
      showLoading();
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);
      
      const response = await fetch(url, {
        ...mergedOptions,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      hideLoading();

      // Parse response
      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      // Handle non-OK responses
      if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
      }

      console.log(`✅ API Success: ${endpoint}`);
      return data;
      
    } catch (error) {
      hideLoading();
      
      if (error.name === 'AbortError') {
        console.error('❌ Request timeout');
        showError('Request timeout. Please try again.');
      } else {
        console.error('❌ API Error:', error);
        showError(error.message || 'An error occurred');
      }
      
      throw error;
    }
  },

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<object>}
   */
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {object} data - Request body
   * @returns {Promise<object>}
   */
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {object} data - Request body
   * @returns {Promise<object>}
   */
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<object>}
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

// ============================================
// UI Utilities
// ============================================
const UI = {
  /**
   * Show loading spinner
   */
  showLoading() {
    let spinner = document.getElementById('loading-spinner');
    if (!spinner) {
      spinner = document.createElement('div');
      spinner.id = 'loading-spinner';
      spinner.className = 'spinner-overlay';
      spinner.innerHTML = '<div class="spinner-border-custom"></div>';
      document.body.appendChild(spinner);
    }
    spinner.style.display = 'flex';
  },

  /**
   * Hide loading spinner
   */
  hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
      spinner.style.display = 'none';
    }
  },

  /**
   * Show error message
   * @param {string} message - Error message
   * @param {string} containerId - Container ID
   */
  showError(message, containerId = 'error') {
    const container = document.getElementById(containerId);
    if (container) {
      container.textContent = message;
      container.classList.remove('d-none');
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        container.classList.add('d-none');
      }, 5000);
    } else {
      // Fallback to console and alert
      console.error('Error:', message);
      alert(`Error: ${message}`);
    }
  },

  /**
   * Show success message
   * @param {string} message - Success message
   * @param {string} containerId - Container ID
   */
  showSuccess(message, containerId = 'success') {
    const container = document.getElementById(containerId);
    if (container) {
      container.textContent = message;
      container.classList.remove('d-none');
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        container.classList.add('d-none');
      }, 3000);
    } else {
      console.log('Success:', message);
    }
  },

  /**
   * Clear error message
   * @param {string} containerId - Container ID
   */
  clearError(containerId = 'error') {
    const container = document.getElementById(containerId);
    if (container) {
      container.classList.add('d-none');
      container.textContent = '';
    }
  },

  /**
   * Show toast notification
   * @param {string} message - Toast message
   * @param {string} type - Type (success, error, warning, info)
   */
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
};

// ============================================
// Risk Level Utilities
// ============================================
const RiskUtils = {
  /**
   * Get risk badge class
   * @param {string} risk - Risk level
   * @returns {string} - Bootstrap class
   */
  getBadgeClass(risk) {
    const classes = {
      'High Risk': 'bg-danger',
      'Medium Risk': 'bg-warning text-dark',
      'Low Risk': 'bg-success',
      'Unknown': 'bg-secondary'
    };
    return classes[risk] || 'bg-secondary';
  },

  /**
   * Get risk card border class
   * @param {string} risk - Risk level
   * @returns {string} - CSS class
   */
  getCardClass(risk) {
    const classes = {
      'High Risk': 'risk-high',
      'Medium Risk': 'risk-medium',
      'Low Risk': 'risk-low'
    };
    return classes[risk] || '';
  },

  /**
   * Get risk color
   * @param {string} risk - Risk level
   * @returns {string} - Hex color
   */
  getColor(risk) {
    const colors = {
      'High Risk': '#dc3545',
      'Medium Risk': '#ffc107',
      'Low Risk': '#28a745',
      'Unknown': '#6c757d'
    };
    return colors[risk] || '#6c757d';
  },

  /**
   * Format risk score
   * @param {number|string} score - Risk score
   * @returns {string} - Formatted score
   */
  formatScore(score) {
    if (score == null || score === '-' || score === '') return '-';
    const numScore = typeof score === 'number' ? score : parseFloat(score);
    return isNaN(numScore) ? '-' : numScore.toFixed(2);
  },

  /**
   * Get risk icon
   * @param {string} risk - Risk level
   * @returns {string} - Emoji icon
   */
  getIcon(risk) {
    const icons = {
      'High Risk': '🔴',
      'Medium Risk': '🟠',
      'Low Risk': '🟢',
      'Unknown': '⚪'
    };
    return icons[risk] || '⚪';
  }
};

// ============================================
// Data Formatting Utilities
// ============================================
const Format = {
  /**
   * Format date
   * @param {string} dateString - Date string
   * @returns {string} - Formatted date
   */
  date(dateString) {
    if (!dateString) return '-';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (e) {
      return '-';
    }
  },

  /**
   * Format number
   * @param {number} num - Number to format
   * @param {number} decimals - Decimal places
   * @returns {string} - Formatted number
   */
  number(num, decimals = 2) {
    if (num == null || num === '') return '-';
    const parsed = typeof num === 'number' ? num : parseFloat(num);
    return isNaN(parsed) ? '-' : parsed.toFixed(decimals);
  },

  /**
   * Format percentage
   * @param {number} value - Percentage value
   * @returns {string} - Formatted percentage
   */
  percentage(value) {
    if (value == null || value === '') return '-';
    const parsed = typeof value === 'number' ? value : parseFloat(value);
    return isNaN(parsed) ? '-' : `${parsed.toFixed(1)}%`;
  },

  /**
   * Format currency (INR)
   * @param {number} amount - Amount
   * @returns {string} - Formatted currency
   */
  currency(amount) {
    if (amount == null) return '-';
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }).format(amount);
    } catch (e) {
      return `₹${amount}`;
    }
  },

  /**
   * Format large numbers (1000 -> 1K)
   * @param {number} num - Number
   * @returns {string} - Formatted number
   */
  compactNumber(num) {
    if (num == null) return '-';
    if (num < 1000) return num.toString();
    if (num < 1000000) return (num / 1000).toFixed(1) + 'K';
    return (num / 1000000).toFixed(1) + 'M';
  },

  /**
   * Truncate text
   * @param {string} text - Text to truncate
   * @param {number} length - Max length
   * @returns {string} - Truncated text
   */
  truncate(text, length = 50) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
  }
};

// ============================================
// Recommendations Parser
// ============================================
const RecommendationUtils = {
  /**
   * Parse recommendations (handle string or array)
   * @param {string|array} recommendations - Recommendations data
   * @returns {array} - Array of recommendations
   */
  parse(recommendations) {
    if (!recommendations) return [];
    
    // Already an array
    if (Array.isArray(recommendations)) {
      return recommendations.filter(r => r && r.trim());
    }
    
    // String that might be JSON
    if (typeof recommendations === 'string') {
      // Try to parse as JSON
      try {
        const parsed = JSON.parse(recommendations);
        if (Array.isArray(parsed)) {
          return parsed.filter(r => r && r.trim());
        }
        return [String(parsed)];
      } catch (e) {
        // Not JSON, treat as plain string
        // Split by common delimiters
        if (recommendations.includes('\\n')) {
          return recommendations.split('\\n').filter(r => r && r.trim());
        }
        if (recommendations.includes('\n')) {
          return recommendations.split('\n').filter(r => r && r.trim());
        }
        if (recommendations.includes('|')) {
          return recommendations.split('|').filter(r => r && r.trim());
        }
        // Single recommendation
        return [recommendations.trim()];
      }
    }
    
    // Fallback
    return [String(recommendations)];
  },

  /**
   * Render recommendations as list
   * @param {string|array} recommendations - Recommendations
   * @param {string} containerId - Container ID
   */
  renderList(recommendations, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.warn(`Container #${containerId} not found`);
      return;
    }

    const recs = this.parse(recommendations);
    container.innerHTML = '';

    if (recs.length === 0) {
      container.innerHTML = '<li class="text-muted">No recommendations available at this time.</li>';
      return;
    }

    recs.forEach(rec => {
      const li = document.createElement('li');
      li.textContent = rec;
      li.className = 'mb-2';
      container.appendChild(li);
    });
  },

  /**
   * Get recommendation priority
   * @param {string} recommendation - Recommendation text
   * @returns {string} - Priority level
   */
  getPriority(recommendation) {
    const urgent = ['urgent', 'immediate', 'critical', 'asap'];
    const high = ['high', 'important', 'significant'];
    
    const lowerRec = recommendation.toLowerCase();
    
    if (urgent.some(word => lowerRec.includes(word))) return 'urgent';
    if (high.some(word => lowerRec.includes(word))) return 'high';
    return 'normal';
  }
};

// ============================================
// Validation Utilities
// ============================================
const Validator = {
  /**
   * Validate email
   * @param {string} email - Email address
   * @returns {boolean}
   */
  email(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  /**
   * Validate phone number (Indian)
   * @param {string} phone - Phone number
   * @returns {boolean}
   */
  phone(phone) {
    const re = /^[6-9]\d{9}$/;
    return re.test(phone.replace(/\s/g, ''));
  },

  /**
   * Validate required field
   * @param {*} value - Field value
   * @returns {boolean}
   */
  required(value) {
    return value !== null && value !== undefined && value !== '';
  },

  /**
   * Validate number range
   * @param {number} value - Value
   * @param {number} min - Minimum
   * @param {number} max - Maximum
   * @returns {boolean}
   */
  range(value, min, max) {
    const num = parseFloat(value);
    return !isNaN(num) && num >= min && num <= max;
  }
};

// ============================================
// Storage Utilities
// ============================================
const Storage = {
  /**
   * Save data to localStorage
   * @param {string} key - Storage key
   * @param {*} value - Value to store
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.error('Storage error:', e);
    }
  },

  /**
   * Get data from localStorage
   * @param {string} key - Storage key
   * @returns {*} - Stored value
   */
  get(key) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (e) {
      console.error('Storage error:', e);
      return null;
    }
  },

  /**
   * Remove data from localStorage
   * @param {string} key - Storage key
   */
  remove(key) {
    localStorage.removeItem(key);
  },

  /**
   * Clear all localStorage
   */
  clear() {
    localStorage.clear();
  }
};

// ============================================
// Global Functions (for backward compatibility)
// ============================================

function showLoading() {
  UI.showLoading();
}

function hideLoading() {
  UI.hideLoading();
}

function showError(message) {
  UI.showError(message);
}

function showSuccess(message) {
  UI.showSuccess(message);
}

function logout() {
  Auth.logout();
}

// ============================================
// Page Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Student Dropout Prediction System - Initialized');
  
  // Add smooth scrolling
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

  // Add loading state to all forms
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
      }
    });
  });

  // Check authentication on protected pages
  const publicPages = ['login.html', 'index.html'];
  const currentPage = window.location.pathname.split('/').pop();
  
  if (!publicPages.includes(currentPage) && currentPage) {
    Auth.requireAuth();
  }
});

// ============================================
// Error Handling
// ============================================

window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

// ============================================
// Export for ES6 Modules (optional)
// ============================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CONFIG,
    Auth,
    API,
    UI,
    RiskUtils,
    Format,
    RecommendationUtils,
    Validator,
    Storage
  };
}

// ============================================
// Console Welcome Message
// ============================================

console.log('%c🎓 Student Dropout Prediction System', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cVersion 1.0.0 | Built with ❤️', 'color: #764ba2; font-size: 12px;');
console.log('%cAPI Base:', 'font-weight: bold;', CONFIG.API_BASE);