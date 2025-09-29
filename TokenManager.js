/**
 * TokenManager - JWT Token Management Utility
 *
 * This utility class handles JWT token storage, retrieval, and automatic refresh
 * for ServEase authentication system integration.
 *
 * Features:
 * - Automatic token storage in localStorage
 * - Token refresh handling
 * - Authenticated API requests
 * - Error handling for expired tokens
 *
 * Usage:
 *   const tokenManager = new TokenManager();
 *   await tokenManager.login(email, password);
 *   const response = await tokenManager.authenticatedRequest('/api/v1/customers/profile/');
 */

class TokenManager {
  constructor(baseURL = "http://localhost/api/v1") {
    this.baseURL = baseURL;
    this.refreshPromise = null; // Prevent multiple refresh requests
  }

  /**
   * Save JWT tokens to localStorage
   * @param {Object} tokens - Object containing access and refresh tokens
   * @param {string} tokens.access - JWT access token
   * @param {string} tokens.refresh - JWT refresh token
   */
  saveTokens(tokens) {
    if (tokens.access) {
      localStorage.setItem("access_token", tokens.access);
    }
    if (tokens.refresh) {
      localStorage.setItem("refresh_token", tokens.refresh);
    }
  }

  /**
   * Get access token from localStorage
   * @returns {string|null} Access token or null if not found
   */
  getAccessToken() {
    return localStorage.getItem("access_token");
  }

  /**
   * Get refresh token from localStorage
   * @returns {string|null} Refresh token or null if not found
   */
  getRefreshToken() {
    return localStorage.getItem("refresh_token");
  }

  /**
   * Check if user has valid tokens
   * @returns {boolean} True if tokens exist
   */
  isAuthenticated() {
    return !!(this.getAccessToken() && this.getRefreshToken());
  }

  /**
   * Clear all tokens from localStorage
   */
  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_data");
  }

  /**
   * Refresh access token using refresh token
   * @returns {Promise<string|null>} New access token or null if failed
   */
  async refreshToken() {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    this.refreshPromise = this._performRefresh(refreshToken);
    const result = await this.refreshPromise;
    this.refreshPromise = null;
    return result;
  }

  /**
   * Internal method to perform token refresh
   * @private
   */
  async _performRefresh(refreshToken) {
    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        const tokens = await response.json();
        this.saveTokens(tokens);
        return tokens.access;
      } else {
        // Refresh token is invalid, clear all tokens
        this.clearTokens();
        return null;
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      this.clearTokens();
      return null;
    }
  }

  /**
   * Perform user login
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Login result with success status and user data
   */
  async login(email, password) {
    try {
      const response = await fetch(`${this.baseURL}/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const userData = await response.json();
        this.saveTokens(userData.tokens);

        // Save user data for easy access
        localStorage.setItem(
          "user_data",
          JSON.stringify({
            id: userData.id,
            email: userData.email,
            first_name: userData.first_name,
            last_name: userData.last_name,
            user_role: userData.user_role,
          })
        );

        return {
          success: true,
          user: userData,
          message: "Login successful",
        };
      } else {
        const error = await response.json();
        return {
          success: false,
          error: error.detail || "Login failed",
          status: response.status,
        };
      }
    } catch (error) {
      console.error("Login request failed:", error);
      return {
        success: false,
        error: "Network error occurred",
        details: error.message,
      };
    }
  }

  /**
   * Perform user registration
   * @param {Object} userData - Registration data
   * @returns {Promise<Object>} Registration result
   */
  async register(userData) {
    try {
      const response = await fetch(`${this.baseURL}/auth/register/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const result = await response.json();
        this.saveTokens(result.tokens);

        // Save user data
        localStorage.setItem(
          "user_data",
          JSON.stringify({
            id: result.id,
            email: result.email,
            first_name: result.first_name,
            last_name: result.last_name,
            user_role: result.user_role,
          })
        );

        return {
          success: true,
          user: result,
          message: "Registration successful",
        };
      } else {
        const error = await response.json();
        return {
          success: false,
          error: error,
          status: response.status,
        };
      }
    } catch (error) {
      console.error("Registration request failed:", error);
      return {
        success: false,
        error: "Network error occurred",
        details: error.message,
      };
    }
  }

  /**
   * Perform authenticated logout
   * @returns {Promise<Object>} Logout result
   */
  async logout() {
    const refreshToken = this.getRefreshToken();

    if (refreshToken) {
      try {
        await fetch(`${this.baseURL}/auth/logout/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: refreshToken }),
        });
      } catch (error) {
        console.error("Logout request failed:", error);
      }
    }

    // Always clear tokens locally
    this.clearTokens();
    return { success: true, message: "Logged out successfully" };
  }

  /**
   * Get current user data from localStorage
   * @returns {Object|null} User data or null
   */
  getCurrentUser() {
    const userData = localStorage.getItem("user_data");
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Make authenticated API request with automatic token refresh
   * @param {string} url - API endpoint URL
   * @param {Object} options - Fetch options
   * @returns {Promise<Response>} Fetch response
   */
  async authenticatedRequest(url, options = {}) {
    const fullUrl = url.startsWith("http") ? url : `${this.baseURL}${url}`;
    let token = this.getAccessToken();

    const makeRequest = async (accessToken) => {
      const headers = {
        "Content-Type": "application/json",
        ...options.headers,
      };

      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }

      return fetch(fullUrl, {
        ...options,
        headers,
      });
    };

    // First attempt with current token
    let response = await makeRequest(token);

    // If unauthorized (401), try to refresh token and retry
    if (response.status === 401 && this.getRefreshToken()) {
      console.log("Access token expired, attempting refresh...");

      const newToken = await this.refreshToken();
      if (newToken) {
        console.log("Token refreshed successfully, retrying request...");
        response = await makeRequest(newToken);
      } else {
        console.log("Token refresh failed, user needs to log in again");
        // Could trigger a login redirect here
        throw new Error("Authentication failed. Please log in again.");
      }
    }

    return response;
  }

  /**
   * Validate current access token
   * @returns {Promise<boolean>} True if token is valid
   */
  async validateToken() {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/validate-token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token }),
      });

      return response.ok;
    } catch (error) {
      console.error("Token validation failed:", error);
      return false;
    }
  }

  /**
   * Decode JWT token payload (client-side only, for display purposes)
   * @param {string} token - JWT token to decode
   * @returns {Object|null} Decoded payload or null if invalid
   */
  decodeToken(token) {
    try {
      const payload = token.split(".")[1];
      const decoded = atob(payload);
      return JSON.parse(decoded);
    } catch (error) {
      console.error("Token decode failed:", error);
      return null;
    }
  }

  /**
   * Check if token is expired (client-side check)
   * @param {string} token - JWT token to check
   * @returns {boolean} True if token is expired
   */
  isTokenExpired(token) {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) return true;

    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  }
}

// Export for ES6 modules
export default TokenManager;

// Also support CommonJS
if (typeof module !== "undefined" && module.exports) {
  module.exports = TokenManager;
}

// Global export for script tag usage
if (typeof window !== "undefined") {
  window.TokenManager = TokenManager;
}
