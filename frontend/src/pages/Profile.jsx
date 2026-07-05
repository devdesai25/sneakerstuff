/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../services/api";
import { User, ClipboardList, Calendar, Award, MapPin } from "lucide-react";

export default function Profile() {
  const { user } = useContext(AuthContext);

  // Fetch orders (to show count/summaries)
  const { data: orders = [] } = useQuery({
    queryKey: ["orders"],
    queryFn: async () => {
      const res = await api.get("/orders");
      return res.data;
    },
    retry: false, // 404 indicates no orders
  });

  // Fetch user entries
  const { data: entries = [] } = useQuery({
    queryKey: ["userEntries"],
    queryFn: async () => {
      const res = await api.get("/users/me/entries");
      return res.data;
    },
    retry: false, // 404 indicates no entries
  });

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: "64px", maxWidth: "800px" }}>
      <h1 style={titleStyle}>MY ACCOUNT</h1>

      {/* Profile Overview Card */}
      <div className="premium-panel" style={profileCardStyle}>
        <div style={avatarStyle}>
          <User size={32} style={{ color: "var(--bg-main)" }} />
        </div>
        <div style={infoStyle}>
          <h2 style={usernameStyle}>{user?.username}</h2>
          {user?.email && <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px", textTransform: "lowercase" }}>{user.email}</p>}
          <div style={metaRowStyle}>
            <span className={user?.role === "admin" ? "badge badge-warning" : "badge badge-neon"}>
              ROLE: {user?.role.toUpperCase()}
            </span>
            <span style={userIdStyle}>USER ID: #{user?.id}</span>
          </div>
        </div>
      </div>

      {/* Stats Quick Grid */}
      <div style={statsGridStyle}>
        <div className="premium-panel" style={statCardStyle}>
          <ClipboardList size={22} style={{ color: "var(--text-primary)", marginBottom: "8px" }} />
          <span style={statValStyle}>{orders.length}</span>
          <span style={statLabelStyle}>ORDERS PLACED</span>
        </div>

        <div className="premium-panel" style={statCardStyle}>
          <Calendar size={22} style={{ color: "var(--text-primary)", marginBottom: "8px" }} />
          <span style={statValStyle}>{entries.length}</span>
          <span style={statLabelStyle}>RAFFLES ENTERED</span>
        </div>
      </div>

      {/* Raffle Entries History */}
      <h3 style={sectionTitleStyle}>MY DRAWINGS ENTRY HISTORY</h3>
      {entries.length === 0 ? (
        <div className="premium-panel" style={{ padding: "32px", textAlign: "center" }}>
          <p style={{ color: "var(--text-muted)", marginBottom: "16px" }}>You haven't entered any sneaker raffle drops yet.</p>
          <Link to="/drops" className="btn btn-primary">VIEW ACTIVE DROPS</Link>
        </div>
      ) : (
        <div style={entriesContainerStyle}>
          {entries.map((entry) => (
            <div key={entry.entry_id} className="premium-panel animate-fade-in" style={entryRowStyle}>
              <div>
                <h4 style={{ fontSize: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Award size={16} style={{ color: "var(--text-primary)" }} /> 
                  Drop Raffle ID #{entry.drop_id}
                </h4>
                <div style={entryMetaStyle}>
                  <span>Entry ID: #{entry.entry_id}</span>
                  <span>&bull;</span>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                    <MapPin size={11} /> {entry.address}
                  </span>
                </div>
              </div>

              <div>
                {entry.ranking ? (
                  <span className="badge badge-success">Ranked #{entry.ranking}</span>
                ) : (
                  <span className="badge badge-warning">Awaiting Draw</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Styles
const titleStyle = {
  fontSize: "36px",
  margin: "32px 0 24px 0",
};

const profileCardStyle = {
  display: "flex",
  alignItems: "center",
  gap: "24px",
  padding: "32px",
  marginBottom: "32px",
};

const avatarStyle = {
  width: "64px",
  height: "64px",
  borderRadius: "50%",
  backgroundColor: "var(--text-primary)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const infoStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "6px",
};

const usernameStyle = {
  fontSize: "24px",
  fontWeight: "800",
};

const metaRowStyle = {
  display: "flex",
  alignItems: "center",
  gap: "16px",
};

const userIdStyle = {
  color: "var(--text-muted)",
  fontSize: "12px",
  fontWeight: "700",
  fontFamily: "var(--font-display)",
};

const statsGridStyle = {
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: "20px",
  marginBottom: "48px",
};

const statCardStyle = {
  padding: "24px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  textAlign: "center",
};

const statValStyle = {
  fontSize: "32px",
  fontWeight: "900",
  fontFamily: "var(--font-display)",
  color: "var(--text-primary)",
  lineHeight: "1.2",
};

const statLabelStyle = {
  fontSize: "11px",
  color: "var(--text-muted)",
  fontWeight: "700",
  letterSpacing: "0.15em",
  fontFamily: "var(--font-display)",
  marginTop: "4px",
};

const sectionTitleStyle = {
  fontSize: "20px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "12px",
  marginBottom: "20px",
};

const entriesContainerStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const entryRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "20px",
};

const entryMetaStyle = {
  display: "flex",
  gap: "12px",
  color: "var(--text-muted)",
  fontSize: "13px",
  marginTop: "4px",
  flexWrap: "wrap",
};
