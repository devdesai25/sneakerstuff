/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

import { Link } from "react-router-dom";
import { AlertTriangle } from "lucide-react";

export default function NotFound() {
  return (
    <div style={containerStyle} className="animate-fade-in">
      <div className="premium-panel" style={cardStyle}>
        <AlertTriangle size={64} style={{ color: "var(--accent-red)", marginBottom: "20px" }} />
        <h1 style={titleStyle}>404 - LOST IN TRANSIT</h1>
        <p style={descStyle}>
          The sneaker details or page you are looking for has been moved, deleted, or is temporarily out of stock.
        </p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: "12px" }}>
          RETURN TO HOME
        </Link>
      </div>
    </div>
  );
}

// Styles
const containerStyle = {
  minHeight: "calc(100vh - 160px)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "48px 24px",
};

const cardStyle = {
  maxWidth: "500px",
  width: "100%",
  padding: "40px",
  textAlign: "center",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  boxShadow: "var(--shadow-lg)",
};

const titleStyle = {
  fontSize: "24px",
  fontWeight: "900",
  fontFamily: "var(--font-display)",
  marginBottom: "12px",
};

const descStyle = {
  color: "var(--text-muted)",
  fontSize: "14px",
  lineHeight: "1.6",
  marginBottom: "24px",
};
