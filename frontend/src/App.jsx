import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

// Pages
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ProductDetails from "./pages/ProductDetails";
import Cart from "./pages/Cart";
import Orders from "./pages/Orders";
import Drops from "./pages/Drops";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

// Layout & Global Components
import Navbar from "./components/Navbar";
import Footer from "./components/layout/Footer";
import ErrorBoundary from "./components/common/ErrorBoundary";

// Protected Route Component
function ProtectedRoute({ children, reqAdmin = false }) {
  const { isLoggedIn, user, isLoading } = useContext(AuthContext);

  if (isLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <h3>Loading your session...</h3>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  if (reqAdmin && user?.role !== "admin") {
    // If not admin, redirect to normal drops page where they see the 403 restricted warning and sandbox toggle tip.
    return <Navigate to="/drops" replace />;
  }

  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
          {/* Header/Sticky Navbar */}
          <Navbar />

          {/* Main Layout Container */}
          <main className="main-content" style={{ flexGrow: 1 }}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/product/:id" element={<ProductDetails />} />
              <Route path="/drops" element={<Drops />} />

              {/* Protected User Routes */}
              <Route
                path="/cart"
                element={
                  <ProtectedRoute>
                    <Cart />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders"
                element={
                  <ProtectedRoute>
                    <Orders />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />

              {/* Protected Admin Routes */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute reqAdmin={true}>
                    <Admin />
                  </ProtectedRoute>
                }
              />

              {/* Catch-all 404 Route */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>

          {/* Footer Section */}
          <Footer />
        </div>
      </ErrorBoundary>
    </BrowserRouter>
  );
}