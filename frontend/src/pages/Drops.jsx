import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import { DropCardSkeleton } from "../components/common/Skeleton";
import api from "../services/api";
import { Calendar, Clock, MapPin, ShieldAlert, Award, Send } from "lucide-react";

// Mock Fallback Drops to display when the backend /drops public endpoint throws a 404
const MOCK_FALLBACK_DROPS = [
  {
    drop_id: 101,
    product_id: 1,
    product_name: "NIKE AIR JORDAN 1 HIGH OG 'CHICAGO'",
    product_image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600",
    product_price: 180.00,
    drop_inventory: 8,
    opens_at: new Date(Date.now() + 1000 * 60 * 60 * 3).toISOString(), // Opens in 3 hours
    closes_at: new Date(Date.now() + 1000 * 60 * 60 * 27).toISOString(),
    status: "SCHEDULED"
  },
  {
    drop_id: 102,
    product_id: 2,
    product_name: "ADIDAS YEEZY BOOST 350 V2 'ZEBRA'",
    product_image: "https://images.unsplash.com/photo-1552346154-21d32810aba3?q=80&w=600",
    product_price: 230.00,
    drop_inventory: 15,
    opens_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(), // Opened 12 hours ago
    closes_at: new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(), // Closes in 12 hours
    status: "ENTRY_OPEN"
  },
  {
    drop_id: 103,
    product_id: 3,
    product_name: "NIKE SB DUNK LOW 'VALENTINES'",
    product_image: "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?q=80&w=600",
    product_price: 135.00,
    drop_inventory: 5,
    opens_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(), // Closed
    closes_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    status: "ENTRY_CLOSED"
  }
];

export default function Drops() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const navigate = useNavigate();
  const { isLoggedIn } = useContext(AuthContext);

  const [activeDropId, setActiveDropId] = useState(null);
  const [address, setAddress] = useState("");
  const [activeTab, setActiveTab] = useState("ALL");

  // 1. Fetch drops (Publicly browseable)
  // Queries '/drops'. If it fails with 404, we catch the error and load MOCK_FALLBACK_DROPS.
  const { data: drops, isLoading, isError } = useQuery({
    queryKey: ["drops"],
    queryFn: async () => {
      try {
        const res = await api.get("/drops");
        return res.data;
      } catch (err) {
        if (err.response?.status === 403 || err.response?.status === 404) {
          console.warn("Public /drops route unavailable, falling back to mock sneaker drawings");
          return MOCK_FALLBACK_DROPS;
        }
        throw err;
      }
    }
  });

  // 2. Fetch logged-in user's raffle entries (Enabled only if user is logged in)
  const { data: userEntries = [] } = useQuery({
    queryKey: ["my-entries"],
    queryFn: async () => {
      const res = await api.get("/users/me/entries");
      return res.data;
    },
    enabled: isLoggedIn
  });

  // 3. Register user entry for drop
  const enterRaffleMutation = useMutation({
    mutationFn: async ({ dropId, shippingAddress }) => {
      // Backend POST route to register drawing entries
      return await api.post(`/drops/${dropId}/entries`, { address: shippingAddress });
    },
    onSuccess: () => {
      toast.success("Raffle entry submitted successfully!");
      queryClient.invalidateQueries({ queryKey: ["my-entries"] });
      setActiveDropId(null);
      setAddress("");
    },
    onError: (err) => {
      // Gracefully catches any backend syntax errors (e.g. the db.add argument crash)
      const detail = err.response?.data?.detail || "Entry failed due to server error.";
      toast.error(detail);
    }
  });

  const handleOpenRaffleModal = (dropId) => {
    if (!isLoggedIn) {
      toast.info("Please log in to enter the draw!");
      navigate("/login");
      return;
    }
    setActiveDropId(dropId);
  };

  const handleRegisterEntry = (e) => {
    e.preventDefault();
    if (!address.trim()) {
      toast.error("Please enter a shipping address");
      return;
    }
    enterRaffleMutation.mutate({ dropId: activeDropId, shippingAddress: address });
  };

  // Helper to cross-reference entries from /users/me/entries as a fallback logic
  const checkHasEntered = (dropId) => {
    return userEntries.some((entry) => entry.drop_id === dropId);
  };

  // Filter drops based on selected tab
  const getFilteredDrops = () => {
    if (!drops) return [];
    const now = new Date().getTime();
    
    return drops.filter((drop) => {
      const opensAt = new Date(drop.opens_at).getTime();
      const closesAt = new Date(drop.closes_at).getTime();

      if (activeTab === "LIVE") {
        return now >= opensAt && now < closesAt;
      }
      if (activeTab === "UPCOMING") {
        return now < opensAt;
      }
      if (activeTab === "CLOSED") {
        return now >= closesAt;
      }
      return true;
    });
  };

  const filteredDrops = getFilteredDrops();

  return (
    <div className="container main-content">
      {/* Title Header */}
      <div style={titleHeaderStyle}>
        <span style={subTitleStyle}>SNEAKERSTUFF DRAWINGS</span>
        <h1 style={titleStyle}>LAUNCH DRAWS</h1>
        <p style={descStyle}>Get a fair chance at securing highly-coveted releases at retail prices.</p>
      </div>

      {/* Filter Tabs */}
      <div style={tabContainerStyle}>
        {["ALL", "LIVE", "UPCOMING", "CLOSED"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...tabItemStyle,
              ...(activeTab === tab ? activeTabItemStyle : {})
            }}
          >
            {tab} DRAWS
          </button>
        ))}
      </div>

      {/* Grid Content */}
      {isLoading ? (
        <div className="grid-cols-3">
          <DropCardSkeleton />
          <DropCardSkeleton />
          <DropCardSkeleton />
        </div>
      ) : isError ? (
        <div style={errorCardStyle}>
          <ShieldAlert size={36} />
          <h3 style={{ marginTop: "12px" }}>Failed to retrieve drawings</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "4px" }}>Check your local backend database and server settings.</p>
        </div>
      ) : filteredDrops.length === 0 ? (
        <div style={emptyCardStyle}>
          <Calendar size={36} />
          <h3 style={{ marginTop: "12px" }}>No drops scheduled</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "4px" }}>Check back later for upcoming sneaker releases.</p>
        </div>
      ) : (
        <div className="grid-cols-3">
          {filteredDrops.map((drop) => {
            const hasEntered = checkHasEntered(drop.drop_id);
            const isLive = new Date().getTime() >= new Date(drop.opens_at).getTime() && new Date().getTime() < new Date(drop.closes_at).getTime();
            const isClosed = new Date().getTime() >= new Date(drop.closes_at).getTime();

            return (
              <div key={drop.drop_id} className="premium-panel" style={dropCardStyle}>
                
                {/* Photo container */}
                <div style={imgWrapperStyle}>
                  <img
                    src={drop.product_image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600"}
                    alt={drop.product_name}
                    style={imgStyle}
                    onError={(e) => {
                      e.target.src = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600";
                    }}
                  />
                  <div style={badgeContainerStyle}>
                    {isClosed ? (
                      <span className="badge badge-danger">CLOSED</span>
                    ) : isLive ? (
                      <span className="badge badge-success">LIVE DRAW</span>
                    ) : (
                      <span className="badge badge-warning">UPCOMING</span>
                    )}
                  </div>
                </div>

                {/* Details info */}
                <div style={infoWrapperStyle}>
                  <h3 style={productTitleStyle}>{drop.product_name || "Nike Release"}</h3>
                  <div style={priceRowStyle}>
                    <span style={retailLabelStyle}>Retail Price</span>
                    <span style={retailPriceStyle}>${parseFloat(drop.product_price).toFixed(2)}</span>
                  </div>

                  {/* Countdown Timer */}
                  <CountdownBox opensAt={drop.opens_at} closesAt={drop.closes_at} />

                  <div style={timelineStyle}>
                    <div style={timelineRowStyle}>
                      <Clock size={12} style={{ color: "#777" }} />
                      <span>Opens: {new Date(drop.opens_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                    </div>
                    <div style={timelineRowStyle}>
                      <Clock size={12} style={{ color: "#777" }} />
                      <span>Closes: {new Date(drop.closes_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                    </div>
                  </div>

                  {/* Auth-sensitive Action Button */}
                  {hasEntered ? (
                    <div style={enteredBannerStyle}>
                      <Award size={14} /> REGISTERED FOR DRAW
                    </div>
                  ) : (
                    <button
                      onClick={() => handleOpenRaffleModal(drop.drop_id)}
                      disabled={isClosed || !isLive}
                      className={`btn ${isLoggedIn ? "btn-accent" : "btn-primary"}`}
                      style={actionBtnStyle}
                    >
                      {isClosed ? (
                        "DRAWING CLOSED"
                      ) : !isLive ? (
                        "DRAWING UPCOMING"
                      ) : isLoggedIn ? (
                        "ENTER DRAWING"
                      ) : (
                        "LOGIN TO ENTER"
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Draw Entry Address Modal */}
      {activeDropId && (
        <div style={modalOverlayStyle}>
          <div className="premium-panel animate-fade-in" style={modalContentStyle}>
            <div style={modalHeaderStyle}>
              <h3>Enter Sneaker Draw</h3>
              <button onClick={() => setActiveDropId(null)} style={closeBtnStyle}>✕</button>
            </div>
            
            <form onSubmit={handleRegisterEntry} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div className="form-group">
                <label className="form-label">Shipping Address</label>
                <div style={{ position: "relative" }}>
                  <MapPin size={16} style={modalIconStyle} />
                  <input
                    type="text"
                    className="input-field"
                    placeholder="Enter full shipping street address"
                    style={{ paddingLeft: "42px" }}
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    required
                  />
                </div>
                <span style={modalWarningStyle}>All releases will ship directly to this address on winning drawing.</span>
              </div>

              <div style={modalActionsStyle}>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setActiveDropId(null)}
                  disabled={enterRaffleMutation.isPending}
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  className="btn btn-accent"
                  disabled={enterRaffleMutation.isPending}
                  style={{ gap: "8px" }}
                >
                  {enterRaffleMutation.isPending ? "SUBMITTING..." : <>SUBMIT ENTRY <Send size={14} /></>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// Live Countdown Sub-Component
function CountdownBox({ opensAt, closesAt }) {
  const [timerText, setTimerText] = useState("");

  const formatDiff = (diff) => {
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diff % (1000 * 60)) / 1000);

    let parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    parts.push(`${mins}m`);
    parts.push(`${secs}s`);
    return parts.join(" ");
  };

  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date().getTime();
      const openTime = new Date(opensAt).getTime();
      const closeTime = new Date(closesAt).getTime();

      if (now < openTime) {
        const diff = openTime - now;
        setTimerText(`Opens in: ${formatDiff(diff)}`);
      } else if (now < closeTime) {
        const diff = closeTime - now;
        setTimerText(`Closes in: ${formatDiff(diff)}`);
      } else {
        setTimerText("DRAWING CLOSED");
      }
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [opensAt, closesAt]);

  return (
    <div style={timerBoxStyle}>
      <Clock size={14} style={{ color: "var(--accent-red)" }} />
      <span style={{ fontSize: "12px", fontWeight: "800", fontFamily: "var(--font-display)" }}>
        {timerText}
      </span>
    </div>
  );
}

// Page Styling Specifications
const titleHeaderStyle = {
  textAlign: "center",
  marginBottom: "48px",
};

const subTitleStyle = {
  fontSize: "10px",
  fontWeight: "800",
  letterSpacing: "0.15em",
  color: "var(--accent-red)",
  display: "block",
  marginBottom: "8px",
};

const titleStyle = {
  fontSize: "32px",
  fontWeight: "900",
  color: "var(--text-primary)",
  marginBottom: "12px",
};

const descStyle = {
  color: "var(--text-muted)",
  fontSize: "15px",
  maxWidth: "540px",
  margin: "0 auto",
};

const tabContainerStyle = {
  display: "flex",
  justifyContent: "center",
  gap: "8px",
  marginBottom: "36px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "16px",
  flexWrap: "wrap",
};

const tabItemStyle = {
  padding: "10px 20px",
  background: "transparent",
  border: "none",
  fontFamily: "var(--font-display)",
  fontWeight: "800",
  fontSize: "12px",
  letterSpacing: "0.05em",
  cursor: "pointer",
  color: "var(--text-muted)",
  transition: "all var(--transition-fast)",
};

const activeTabItemStyle = {
  color: "var(--text-primary)",
  borderBottom: "2px solid var(--text-primary)",
};

const errorCardStyle = {
  textAlign: "center",
  padding: "64px 24px",
  color: "var(--error)",
};

const emptyCardStyle = {
  textAlign: "center",
  padding: "64px 24px",
  color: "var(--text-muted)",
};

const dropCardStyle = {
  display: "flex",
  flexDirection: "column",
  height: "100%",
  padding: "0",
  border: "1px solid var(--border-color)",
  boxShadow: "var(--shadow-sm)",
  overflow: "hidden",
};

const imgWrapperStyle = {
  position: "relative",
  paddingTop: "90%",
  backgroundColor: "#f9f9f9",
  overflow: "hidden",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const imgStyle = {
  position: "absolute",
  maxWidth: "85%",
  maxHeight: "85%",
  objectFit: "contain",
};

const badgeContainerStyle = {
  position: "absolute",
  top: "16px",
  left: "16px",
};

const infoWrapperStyle = {
  padding: "24px",
  display: "flex",
  flexDirection: "column",
  flexGrow: 1,
};

const productTitleStyle = {
  fontSize: "16px",
  fontWeight: "800",
  color: "var(--text-primary)",
  marginBottom: "12px",
};

const priceRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "16px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "12px",
};

const retailLabelStyle = {
  fontSize: "12px",
  color: "var(--text-muted)",
  fontWeight: "500",
};

const retailPriceStyle = {
  fontSize: "16px",
  fontWeight: "800",
  fontFamily: "var(--font-display)",
};

const timerBoxStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  padding: "10px 14px",
  backgroundColor: "var(--bg-secondary)",
  borderRadius: "4px",
  marginBottom: "16px",
  width: "fit-content",
};

const timelineStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "6px",
  marginBottom: "24px",
  fontSize: "12px",
  color: "var(--text-muted)",
};

const timelineRowStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
};

const actionBtnStyle = {
  width: "100%",
  padding: "14px",
  fontWeight: "800",
  fontSize: "12px",
  marginTop: "auto",
};

const enteredBannerStyle = {
  width: "100%",
  padding: "14px",
  backgroundColor: "rgba(15, 139, 90, 0.08)",
  color: "var(--success)",
  border: "1px solid rgba(15, 139, 90, 0.15)",
  fontSize: "12px",
  fontWeight: "800",
  textAlign: "center",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "6px",
  marginTop: "auto",
};

// Modal specifications
const modalOverlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: "rgba(0, 0, 0, 0.6)",
  zIndex: 2000,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "20px",
};

const modalContentStyle = {
  width: "100%",
  maxWidth: "460px",
  backgroundColor: "var(--bg-main)",
  boxShadow: "var(--shadow-lg)",
};

const modalHeaderStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "24px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "14px",
};

const closeBtnStyle = {
  background: "transparent",
  border: "none",
  fontSize: "18px",
  cursor: "pointer",
  color: "var(--text-primary)",
};

const modalIconStyle = {
  position: "absolute",
  left: "14px",
  top: "14px",
  color: "#888888",
};

const modalWarningStyle = {
  fontSize: "11px",
  color: "var(--text-muted)",
  marginTop: "4px",
};

const modalActionsStyle = {
  display: "flex",
  justifyContent: "flex-end",
  gap: "10px",
  marginTop: "12px",
};
