import { useContext, useState, useEffect } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { ShoppingCart, LogOut, User, Calendar, ClipboardList, ShieldAlert, Menu, X, Flame } from "lucide-react";
import api from "../services/api";
import SneakDropLogo from "./common/SneakDropLogo";

export default function Navbar() {
  const { isLoggedIn, user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [cartCount, setCartCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Poll shopping cart item quantity if the user session is active
  useEffect(() => {
    if (!isLoggedIn) return;

    const fetchCartCount = async () => {
      try {
        const res = await api.get("/cart");
        const count = res.data.reduce((acc, item) => acc + item.quantity, 0);
        setCartCount(count);
      } catch (err) {
        console.error("Failed to fetch cart for navbar count", err);
      }
    };

    fetchCartCount();
    const interval = setInterval(fetchCartCount, 10000);
    return () => clearInterval(interval);
  }, [isLoggedIn]);

  const handleLogout = () => {
    logout();
    setCartCount(0);
    setMobileMenuOpen(false);
    navigate("/login");
  };

  return (
    <header className="navbar-header">
      <div className="container navbar-container">
        {/* Brand Logo & Icon */}
        <Link to="/" className="navbar-logo" onClick={() => setMobileMenuOpen(false)}>
          <SneakDropLogo size="md" />
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="nav-desktop">
          <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Shop
          </NavLink>
          {/* Drops are now publicly accessible */}
          <NavLink to="/drops" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            <Calendar size={15} /> Drops
          </NavLink>
          
          {isLoggedIn && (
            <>
              <NavLink to="/cart" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
                <div style={{ position: "relative", display: "inline-flex" }}>
                  <ShoppingCart size={15} />
                  {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
                </div>
                Cart
              </NavLink>
              <NavLink to="/orders" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
                <ClipboardList size={15} /> Orders
              </NavLink>
              <NavLink to="/profile" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
                <User size={15} /> Profile
              </NavLink>
              {user?.role === "admin" && (
                <NavLink to="/admin" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
                  <ShieldAlert size={15} /> Admin
                </NavLink>
              )}
            </>
          )}
        </nav>

        {/* Desktop Actions Panel */}
        <div className="nav-actions">
          {isLoggedIn ? (
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div className="user-pill" style={{ cursor: "default" }}>
                <div className={`role-dot role-dot-${user?.role}`} />
                <span>{user?.username} ({user?.role})</span>
              </div>
              <button onClick={handleLogout} className="logout-btn" title="Logout">
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", gap: "10px" }}>
              <Link to="/login" className="btn btn-outline" style={{ padding: "8px 16px", fontSize: "12px" }}>
                Login
              </Link>
              <Link to="/signup" className="btn btn-primary" style={{ padding: "8px 16px", fontSize: "12px" }}>
                Register
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Toggle Button */}
        <button className="mobile-trigger" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-drawer">
          <NavLink to="/" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`} onClick={() => setMobileMenuOpen(false)}>
            Shop Catalog
          </NavLink>
          <NavLink to="/drops" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`} onClick={() => setMobileMenuOpen(false)}>
            Raffle Drops
          </NavLink>
          {isLoggedIn ? (
            <>
              <NavLink to="/cart" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`} onClick={() => setMobileMenuOpen(false)}>
                Cart ({cartCount})
              </NavLink>
              <NavLink to="/orders" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`} onClick={() => setMobileMenuOpen(false)}>
                My Orders
              </NavLink>
              <NavLink to="/profile" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`} onClick={() => setMobileMenuOpen(false)}>
                My Profile
              </NavLink>
              {user?.role === "admin" && (
                <NavLink to="/admin" className={({ isActive }) => `mobile-nav-link ${isActive ? "active" : ""}`} onClick={() => setMobileMenuOpen(false)}>
                  Admin Panel
                </NavLink>
              )}
              <div style={{ borderTop: "1px solid var(--border-color)", padding: "16px 0", marginTop: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <div className="user-pill" style={{ cursor: "default" }}>
                    <div className={`role-dot role-dot-${user?.role}`} />
                    <span>{user?.username} ({user?.role})</span>
                  </div>
                </div>
                <button onClick={handleLogout} className="btn btn-danger" style={{ width: "100%", gap: "8px" }}>
                  <LogOut size={16} /> Logout
                </button>
              </div>
            </>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "16px" }}>
              <Link to="/login" className="btn btn-outline" onClick={() => setMobileMenuOpen(false)}>
                Login
              </Link>
              <Link to="/signup" className="btn btn-primary" onClick={() => setMobileMenuOpen(false)}>
                Join Us
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}