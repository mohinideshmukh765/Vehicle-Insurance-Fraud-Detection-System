import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, LogOut, User as UserIcon } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar glass-panel" style={{ borderRadius: '0', borderLeft: 'none', borderRight: 'none', borderTop: 'none' }}>
      <Link to="/" className="logo" style={{ textDecoration: 'none' }}>
        <Shield size={28} />
        <span>FraudGuard</span>
      </Link>
      
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/predict">New Claim</Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: '1rem', color: 'var(--text-main)' }}>
              <UserIcon size={18} />
              <span>{user.username}</span>
              <button onClick={handleLogout} className="btn-icon" style={{ background: 'transparent', color: 'var(--text-dim)' }}>
                <LogOut size={18} />
              </button>
            </div>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
