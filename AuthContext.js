/**
 * AuthContext - React Authentication Context for ServEase
 *
 * This React Context provides authentication state management and utilities
 * for the ServEase JWT authentication system.
 *
 * Features:
 * - User authentication state management
 * - Login/logout/register functions
 * - Automatic token handling
 * - Loading states
 * - Error handling
 * - Persistent authentication across page reloads
 *
 * Usage:
 *   import { AuthProvider, useAuth } from './AuthContext';
 *
 *   // Wrap your app with AuthProvider
 *   <AuthProvider>
 *     <App />
 *   </AuthProvider>
 *
 *   // Use in components
 *   const { user, login, logout, loading } = useAuth();
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import TokenManager from "./TokenManager";

// Create the authentication context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

// Authentication Provider Component
export const AuthProvider = ({
  children,
  baseURL = "http://localhost/api/v1",
}) => {
  // State management
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize TokenManager
  const [tokenManager] = useState(() => new TokenManager(baseURL));

  // Clear error after a delay
  const clearError = useCallback(() => {
    setTimeout(() => setError(null), 5000);
  }, []);

  // Initialize authentication state on component mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setLoading(true);

        // Check if user has stored tokens
        if (tokenManager.isAuthenticated()) {
          const storedUser = tokenManager.getCurrentUser();

          if (storedUser) {
            // Validate the stored token
            const isValid = await tokenManager.validateToken();

            if (isValid) {
              setUser(storedUser);
            } else {
              // Token is invalid, clear storage
              tokenManager.clearTokens();
            }
          }
        }
      } catch (error) {
        console.error("Auth initialization failed:", error);
        tokenManager.clearTokens();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, [tokenManager]);

  // Login function
  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);

      const result = await tokenManager.login(email, password);

      if (result.success) {
        const userData = {
          id: result.user.id,
          email: result.user.email,
          first_name: result.user.first_name,
          last_name: result.user.last_name,
          user_role: result.user.user_role,
          phone_number: result.user.phone_number,
          is_active: result.user.is_active,
        };

        setUser(userData);
        return { success: true, message: "Login successful" };
      } else {
        setError(result.error);
        clearError();
        return { success: false, error: result.error };
      }
    } catch (error) {
      const errorMessage = "Login failed. Please try again.";
      setError(errorMessage);
      clearError();
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Registration function
  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);

      const result = await tokenManager.register(userData);

      if (result.success) {
        const newUser = {
          id: result.user.id,
          email: result.user.email,
          first_name: result.user.first_name,
          last_name: result.user.last_name,
          user_role: result.user.user_role,
          phone_number: result.user.phone_number,
        };

        setUser(newUser);
        return { success: true, message: "Registration successful" };
      } else {
        setError(result.error);
        clearError();
        return { success: false, error: result.error };
      }
    } catch (error) {
      const errorMessage = "Registration failed. Please try again.";
      setError(errorMessage);
      clearError();
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setLoading(true);
      await tokenManager.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      setError(null);
      setLoading(false);
    }
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await tokenManager.authenticatedRequest(
        "/auth/profile/update/",
        {
          method: "POST",
          body: JSON.stringify(profileData),
        }
      );

      if (response.ok) {
        const updatedUser = await response.json();
        const userData = {
          ...user,
          ...updatedUser,
        };

        setUser(userData);

        // Update stored user data
        localStorage.setItem("user_data", JSON.stringify(userData));

        return { success: true, message: "Profile updated successfully" };
      } else {
        const error = await response.json();
        setError("Profile update failed");
        clearError();
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage = "Profile update failed. Please try again.";
      setError(errorMessage);
      clearError();
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Get user's customer profile
  const getCustomerProfile = async () => {
    try {
      const response = await tokenManager.authenticatedRequest(
        "/customers/profile/"
      );

      if (response.ok) {
        return await response.json();
      } else if (response.status === 404) {
        return null; // No customer profile exists
      } else {
        throw new Error("Failed to fetch customer profile");
      }
    } catch (error) {
      console.error("Get customer profile error:", error);
      throw error;
    }
  };

  // Create customer profile
  const createCustomerProfile = async (profileData) => {
    try {
      const response = await tokenManager.authenticatedRequest(
        "/customers/profile/create/",
        {
          method: "POST",
          body: JSON.stringify(profileData),
        }
      );

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create customer profile");
      }
    } catch (error) {
      console.error("Create customer profile error:", error);
      throw error;
    }
  };

  // Update customer profile
  const updateCustomerProfile = async (profileData) => {
    try {
      const response = await tokenManager.authenticatedRequest(
        "/customers/profile/update/",
        {
          method: "POST",
          body: JSON.stringify(profileData),
        }
      );

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update customer profile");
      }
    } catch (error) {
      console.error("Update customer profile error:", error);
      throw error;
    }
  };

  // Make authenticated API requests
  const apiRequest = async (url, options = {}) => {
    try {
      return await tokenManager.authenticatedRequest(url, options);
    } catch (error) {
      if (error.message.includes("Please log in again")) {
        // Auto logout on authentication failure
        logout();
      }
      throw error;
    }
  };

  // Check if user is authenticated
  const isAuthenticated = () => {
    return user !== null && tokenManager.isAuthenticated();
  };

  // Check if user has specific role
  const hasRole = (role) => {
    return user && user.user_role === role;
  };

  // Get user's full name
  const getUserFullName = () => {
    if (!user) return "";
    return `${user.first_name} ${user.last_name}`.trim();
  };

  // Context value
  const contextValue = {
    // State
    user,
    loading,
    error,

    // Authentication methods
    login,
    register,
    logout,

    // Profile methods
    updateProfile,
    getCustomerProfile,
    createCustomerProfile,
    updateCustomerProfile,

    // Utility methods
    apiRequest,
    isAuthenticated,
    hasRole,
    getUserFullName,

    // Direct access to token manager for advanced use cases
    tokenManager,

    // Utility functions
    clearError: () => setError(null),
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

// Higher-order component for protecting routes
export const withAuth = (Component) => {
  return function AuthenticatedComponent(props) {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
      return <div className="auth-loading">Loading...</div>;
    }

    if (!isAuthenticated()) {
      return (
        <div className="auth-error">Please log in to access this page.</div>
      );
    }

    return <Component {...props} />;
  };
};

// Hook for handling authentication redirects
export const useAuthRedirect = (redirectTo = "/login") => {
  const { isAuthenticated, loading } = useAuth();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    if (!loading && !isAuthenticated()) {
      setShouldRedirect(true);
    }
  }, [isAuthenticated, loading]);

  return { shouldRedirect, redirectTo };
};

// Protected Route component for React Router
export const ProtectedRoute = ({
  children,
  fallback = <div>Please log in to access this page.</div>,
  loadingComponent = <div>Loading...</div>,
  requiredRole = null,
}) => {
  const { user, loading, hasRole } = useAuth();

  if (loading) {
    return loadingComponent;
  }

  if (!user) {
    return fallback;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <div>You don't have permission to access this page.</div>;
  }

  return children;
};

// Error Boundary for authentication errors
export class AuthErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Auth Error Boundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="auth-error-boundary">
          <h2>Authentication Error</h2>
          <p>
            Something went wrong with authentication. Please refresh the page or
            log in again.
          </p>
          <button onClick={() => window.location.reload()}>Refresh Page</button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default AuthContext;
