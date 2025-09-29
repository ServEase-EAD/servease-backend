/**
 * Complete Frontend Integration Example for ServEase Customer Authentication
 * This file demonstrates how to integrate token-based authentication in a React application
 */

import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth, CustomerProtectedRoute } from './AuthContext';
import tokenManager from './TokenManager';

// Login Component
const LoginForm = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { login, isAuthenticated, error, clearError } = useAuth();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Clear error when user starts typing
        if (error) {
            clearError();
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const result = await login(formData.email, formData.password);

            if (result.success) {
                // Redirect to dashboard or home page
                window.location.href = '/dashboard';
            }
        } catch (error) {
            console.error('Login error:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    // Redirect if already authenticated
    if (isAuthenticated) {
        window.location.href = '/dashboard';
        return null;
    }

    return (
        <div className="login-container">
            <h2>Customer Login</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                {error && (
                    <div className="error-message">
                        {typeof error === 'string' ? error : 'Login failed. Please try again.'}
                    </div>
                )}

                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Logging in...' : 'Login'}
                </button>
            </form>
        </div>
    );
};

// Registration Component
const RegisterForm = () => {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        phone_number: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { register, isAuthenticated, error, clearError } = useAuth();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        if (error) {
            clearError();
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const result = await register(formData);

            if (result.success) {
                // Redirect to profile creation or dashboard
                window.location.href = '/profile/create';
            }
        } catch (error) {
            console.error('Registration error:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isAuthenticated) {
        window.location.href = '/dashboard';
        return null;
    }

    return (
        <div className="register-container">
            <h2>Customer Registration</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="first_name">First Name:</label>
                    <input
                        type="text"
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="last_name">Last Name:</label>
                    <input
                        type="text"
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="phone_number">Phone Number:</label>
                    <input
                        type="tel"
                        id="phone_number"
                        name="phone_number"
                        value={formData.phone_number}
                        onChange={handleChange}
                        disabled={isSubmitting}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        disabled={isSubmitting}
                    />
                </div>

                {error && (
                    <div className="error-message">
                        {typeof error === 'string' ? error : 'Registration failed. Please try again.'}
                    </div>
                )}

                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Creating Account...' : 'Register'}
                </button>
            </form>
        </div>
    );
};

// Customer Profile Component
const CustomerProfile = () => {
    const [profile, setProfile] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState(null);

    const { getCustomerProfile, updateCustomerProfile, user } = useAuth();

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const result = await getCustomerProfile();

            if (result.success) {
                setProfile(result.data);
                setEditData(result.data);
            } else {
                setError(result.error?.message || 'Failed to load profile');
            }
        } catch (error) {
            setError('Network error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    const handleEditToggle = () => {
        setIsEditing(!isEditing);
        if (!isEditing) {
            setEditData({ ...profile });
        }
        setError(null);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setEditData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSave = async () => {
        setIsSaving(true);
        setError(null);

        try {
            const result = await updateCustomerProfile(editData);

            if (result.success) {
                setProfile(result.data);
                setIsEditing(false);
            } else {
                setError(result.error?.message || 'Failed to update profile');
            }
        } catch (error) {
            setError('Network error occurred');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return <div className="loading">Loading profile...</div>;
    }

    if (!profile) {
        return (
            <div className="profile-error">
                <h3>Profile not found</h3>
                <p>Please complete your profile setup.</p>
                <button onClick={() => window.location.href = '/profile/create'}>
                    Create Profile
                </button>
            </div>
        );
    }

    return (
        <div className="customer-profile">
            <div className="profile-header">
                <h2>Customer Profile</h2>
                <button onClick={handleEditToggle}>
                    {isEditing ? 'Cancel' : 'Edit Profile'}
                </button>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            <div className="profile-content">
                <div className="profile-field">
                    <label>First Name:</label>
                    {isEditing ? (
                        <input
                            type="text"
                            name="first_name"
                            value={editData.first_name || ''}
                            onChange={handleInputChange}
                        />
                    ) : (
                        <span>{profile.first_name}</span>
                    )}
                </div>

                <div className="profile-field">
                    <label>Last Name:</label>
                    {isEditing ? (
                        <input
                            type="text"
                            name="last_name"
                            value={editData.last_name || ''}
                            onChange={handleInputChange}
                        />
                    ) : (
                        <span>{profile.last_name}</span>
                    )}
                </div>

                <div className="profile-field">
                    <label>Email:</label>
                    <span>{profile.email}</span>
                </div>

                <div className="profile-field">
                    <label>Phone:</label>
                    {isEditing ? (
                        <input
                            type="tel"
                            name="phone"
                            value={editData.phone || ''}
                            onChange={handleInputChange}
                        />
                    ) : (
                        <span>{profile.phone || 'Not provided'}</span>
                    )}
                </div>

                <div className="profile-field">
                    <label>Address:</label>
                    {isEditing ? (
                        <textarea
                            name="address"
                            value={editData.address || ''}
                            onChange={handleInputChange}
                            rows="3"
                        />
                    ) : (
                        <span>{profile.address || 'Not provided'}</span>
                    )}
                </div>

                <div className="profile-field">
                    <label>Company Name:</label>
                    {isEditing ? (
                        <input
                            type="text"
                            name="company_name"
                            value={editData.company_name || ''}
                            onChange={handleInputChange}
                        />
                    ) : (
                        <span>{profile.company_name || 'Not provided'}</span>
                    )}
                </div>

                <div className="profile-field">
                    <label>Member Since:</label>
                    <span>{new Date(profile.customer_since).toLocaleDateString()}</span>
                </div>

                <div className="profile-field">
                    <label>Status:</label>
                    <span className={`status ${profile.is_verified ? 'verified' : 'unverified'}`}>
                        {profile.is_verified ? 'Verified' : 'Unverified'}
                    </span>
                </div>

                {isEditing && (
                    <div className="profile-actions">
                        <button onClick={handleSave} disabled={isSaving}>
                            {isSaving ? 'Saving...' : 'Save Changes'}
                        </button>
                        <button onClick={handleEditToggle} disabled={isSaving}>
                            Cancel
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

// Protected Dashboard Component
const CustomerDashboard = () => {
    const { user, logout } = useAuth();

    const handleLogout = async () => {
        await logout();
        window.location.href = '/login';
    };

    return (
        <div className="customer-dashboard">
            <header className="dashboard-header">
                <h1>Welcome, {user?.first_name}!</h1>
                <button onClick={handleLogout}>Logout</button>
            </header>

            <nav className="dashboard-nav">
                <a href="/profile">My Profile</a>
                <a href="/appointments">Appointments</a>
                <a href="/vehicles">My Vehicles</a>
                <a href="/history">Service History</a>
            </nav>

            <main className="dashboard-content">
                {/* Dashboard content */}
                <CustomerProfile />
            </main>
        </div>
    );
};

// Main App Component
const App = () => {
    return (
        <AuthProvider>
            <div className="app">
                {/* Example routing logic */}
                <Routes />
            </div>
        </AuthProvider>
    );
};

// Simple routing component for demonstration
const Routes = () => {
    const { isAuthenticated, isLoading } = useAuth();
    const currentPath = window.location.pathname;

    if (isLoading) {
        return <div className="loading">Loading...</div>;
    }

    // Route logic
    switch (currentPath) {
        case '/login':
            return <LoginForm />;
        case '/register':
            return <RegisterForm />;
        case '/dashboard':
            return (
                <CustomerProtectedRoute>
                    <CustomerDashboard />
                </CustomerProtectedRoute>
            );
        case '/profile':
            return (
                <CustomerProtectedRoute>
                    <CustomerProfile />
                </CustomerProtectedRoute>
            );
        default:
            if (isAuthenticated) {
                return (
                    <CustomerProtectedRoute>
                        <CustomerDashboard />
                    </CustomerProtectedRoute>
                );
            } else {
                return <LoginForm />;
            }
    }
};

// Utility function to make authenticated API calls from any component
export const makeAuthenticatedRequest = async (endpoint, options = {}) => {
    const fullUrl = `${process.env.REACT_APP_API_URL || 'http://localhost'}${endpoint}`;
    return tokenManager.authenticatedFetch(fullUrl, options);
};

// Example usage in other components
export const ExampleApiCall = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await makeAuthenticatedRequest('/api/v1/customers/profile/');

                if (response.ok) {
                    const result = await response.json();
                    setData(result);
                }
            } catch (error) {
                console.error('API call failed:', error);
            }
        };

        fetchData();
    }, []);

    return data ? <div>{JSON.stringify(data)}</div> : <div>Loading...</div>;
};

export default App;