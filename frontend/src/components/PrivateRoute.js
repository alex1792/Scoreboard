import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// requires login to access the page
export const PrivateRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();
    
    if (loading) {
        return <div>Loading...</div>;
    }
    
    return isAuthenticated ? children : <Navigate to='/login' />;
};

// requires user role to be admin to access the page
export const AdminRoute = ({ children }) => {
    const { isAuthenticated, currentUser, loading } = useAuth();
    
    if (loading) {
        return <div>Loading...</div>;
    }
    
    if (!isAuthenticated) {
        console.log('Not authenticated, redirecting to login');
        return <Navigate to="/login" />;
    }
    
    if (currentUser?.role !== 'admin') {
        console.log('Not admin, redirecting to home');
        return <Navigate to='/' />;
    }
    
    return children;
};

// requires user role to be umpire to access the page
export const UmpireRoute = ({ children }) => {
    const { isAuthenticated, currentUser, loading } = useAuth();
    
    if (loading) {
        return <div>Loading...</div>;
    }
    
    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }
    
    if (currentUser?.role !== 'umpire') {
        return <Navigate to='/' />;
    }
    
    return children;
};

// requires user role to be host to access the page
export const HostRoute = ({ children}) => {
    const { isAuthenticated, currentUser, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    if (currentUser?.role !== 'host' && currentUser?.role !== 'admin') {
        return <Navigate to='/' />;
    }

    return children;
};

// requires user role to be either admin, host or umpire to access the page
export const HostOrUmpireRoute = ({ children }) => {
    const { isAuthenticated, currentUser, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    if (!['admin', 'host', 'umpire'].includes(currentUser?.role)) {
        return <Navigate to='/' />;
    }
    
    return children;
};