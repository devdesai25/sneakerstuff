import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import { DropCardSkeleton } from "../components/common/Skeleton";
import api from "../services/api";
import TurnstileWidget from "../components/TurnstileWidget";
import { getVisitorId } from "../helpers/fingerprint";
import { useDropRealtime } from "../hooks/useDropRealtime";
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

  // Subscribe to real-time WebSockets & SSE live updates
  useDropRealtime(0);

  const [activeDropId, setActiveDropId] = useState(null);
  const [address, setAddress] = useState("");
  const [selectedSize, setSelectedSize] = useState("");
  const [activeTab, setActiveTab] = useState("ALL");
  const [captchaToken, setCaptchaToken] = useState(null);
  const [captchaResetKey, setCaptchaResetKey] = useState(0);

  const STANDARD_SIZES = ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 11.5", "US 12"];

  const resetModalState = () => {
    setActiveDropId(null);
    setAddress("");
    setSelectedSize("");
    setCaptchaToken(null);
    setCaptchaResetKey((prev) => prev + 1);
  };

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
    mutationFn: async ({ dropId, shippingAddress, size, captchaToken }) => {
      const deviceFingerprint = await getVisitorId();
      // Backend POST route to register drawing entries
      return await api.post(`/drops/${dropId}/entries`, { 
        address: shippingAddress, 
        size,
        captcha_token: captchaToken,
        device_fingerprint: deviceFingerprint
      });
    },
    onSuccess: () => {
      toast.success("Raffle entry submitted successfully!");
      queryClient.invalidateQueries({ queryKey: ["my-entries"] });
      resetModalState();
    },
    onError: (err) => {
      // Gracefully catches any backend syntax errors (e.g. the db.add argument crash)
      const detail = err.response?.data?.detail || "Entry failed due to server error.";
      toast.error(detail);
      setCaptchaToken(null);
      setCaptchaResetKey((prev) => prev + 1);
    }
  });

  const handleOpenRaffleModal = (dropId) => {
    if (!isLoggedIn) {
      toast.info("Please log in to enter the draw!");
      navigate("/login");
      return;
    }
    setCaptchaToken(null);
    setCaptchaResetKey((prev) => prev + 1);
    setActiveDropId(dropId);
  };

  const handleRegisterEntry = (e) => {
    e.preventDefault();
    if (!address.trim()) {
      toast.error("Please enter a shipping address");
      return;
    }
    if (!selectedSize) {
      toast.error("Please select your shoe size");
      return;
    }
    if (!captchaToken) {
      toast.error("Please complete the CAPTCHA verification");
      return;
    }
    enterRaffleMutation.mutate({ 
      dropId: activeDropId, 
      shippingAddress: address, 
      size: selectedSize,
      captchaToken 
    });
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
            const userEntry = userEntries.find((entry) => entry.drop_id === drop.drop_id);
            const hasEntered = !!userEntry;
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
                    {drop.status === "COMPLETED" || (isClosed && drop.status !== "CLAIMING" && drop.status !== "PAUSED" && drop.status !== "CANCELLED") ? (
                      <span className="badge badge-outline" style={{ color: "var(--accent-neon-green)", borderColor: "var(--accent-neon-green)" }}>COMPLETED</span>
                    ) : drop.status === "PAUSED" ? (
                      <span className="badge badge-warning">PAUSED</span>
                    ) : drop.status === "CANCELLED" ? (
                      <span className="badge badge-danger">CANCELLED</span>
                    ) : drop.status === "CLAIMING" ? (
                      <span className="badge badge-success">WINNERS CLAIMING</span>
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
                    <span style={retailPriceStyle}>₹{parseFloat(drop.product_price).toFixed(2)}</span>
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

                  {/* Auth-sensitive Action Button & Drawing Status */}
                  {hasEntered ? (
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "auto" }}>
                      {userEntry?.reservation?.order_status === "PAID" ? (
                        <div style={{ ...enteredBannerStyle, backgroundColor: "rgba(15, 139, 90, 0.15)", color: "var(--accent-neon-green)", borderColor: "var(--accent-neon-green)", padding: "12px" }}>
                          <Award size={16} /> ✓ ORDER PAID &amp; SECURED (#{userEntry.reservation.order_id})
                        </div>
                      ) : userEntry?.reservation?.order_status === "CANCELLED" || userEntry?.reservation?.order_status === "EXPIRED" ? (
                        <div style={{ ...enteredBannerStyle, backgroundColor: "rgba(220, 53, 69, 0.1)", color: "var(--error)", borderColor: "var(--error)", padding: "12px" }}>
                          <Award size={16} /> ✕ RAFFLE ORDER CANCELLED / FORFEITED
                        </div>
                      ) : userEntry?.reservation ? (
                        <>
                          <div style={{ ...enteredBannerStyle, backgroundColor: "rgba(15, 139, 90, 0.15)", color: "var(--accent-neon-green)", borderColor: "var(--accent-neon-green)" }}>
                            <Award size={16} /> 🎉 YOU WON THIS RAFFLE! (Rank #{userEntry.ranking})
                          </div>
                          <button
                            onClick={() => navigate("/orders")}
                            className="btn btn-accent"
                            style={{ width: "100%", padding: "10px", fontSize: "12px", fontWeight: "800" }}
                          >
                            CLAIM &amp; PAY ORDER (#{userEntry.reservation.order_id})
                          </button>
                        </>
                      ) : isClosed || drop.status === "ENTRY_CLOSED" || drop.status === "SELECTING" || drop.status === "CLAIMING" || drop.status === "COMPLETED" ? (
                        userEntry?.ranking ? (
                          <div style={{ ...enteredBannerStyle, backgroundColor: "rgba(255, 153, 0, 0.08)", color: "#ff9900", borderColor: "#ff9900", flexDirection: "column", gap: "2px" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                              <Award size={14} /> QUEUE RANK #{userEntry.ranking} (Waitlist)
                            </div>
                            <span style={{ fontSize: "10px", color: "var(--text-muted)", fontWeight: "500" }}>
                              Next in line if a winner forfeits.
                            </span>
                          </div>
                        ) : (
                          <div style={enteredBannerStyle}>
                            <Award size={14} /> REGISTERED &bull; DRAW COMPLETED
                          </div>
                        )
                      ) : (
                        <div style={enteredBannerStyle}>
                          <Award size={14} /> REGISTERED FOR DRAW (Size: {userEntry?.size || "Selected"})
                        </div>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => handleOpenRaffleModal(drop.drop_id)}
                      disabled={isClosed || !isLive || drop.status === "PAUSED" || drop.status === "COMPLETED" || drop.status === "CANCELLED"}
                      className={`btn ${isLoggedIn ? "btn-accent" : "btn-primary"}`}
                      style={actionBtnStyle}
                    >
                      {drop.status === "COMPLETED" || isClosed ? (
                        "DRAWING COMPLETED"
                      ) : drop.status === "PAUSED" ? (
                        "DRAWING PAUSED"
                      ) : drop.status === "CANCELLED" ? (
                        "DRAWING CANCELLED"
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
              <button onClick={resetModalState} style={closeBtnStyle}>✕</button>
            </div>
            
            <form onSubmit={handleRegisterEntry} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div className="form-group">
                <label className="form-label">Select Size</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {STANDARD_SIZES.map(sz => (
                    <button
                      key={sz}
                      type="button"
                      onClick={() => setSelectedSize(sz)}
                      style={{
                        width: '50px',
                        padding: '8px 0',
                        textAlign: 'center',
                        border: selectedSize === sz ? '2px solid var(--accent-red)' : '1px solid var(--border-color)',
                        backgroundColor: selectedSize === sz ? 'rgba(227, 6, 19, 0.1)' : 'var(--bg-input)',
                        color: 'var(--text-primary)',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontFamily: 'var(--font-display)',
                        fontWeight: selectedSize === sz ? '800' : '500',
                        fontSize: '11px',
                      }}
                    >
                      {sz}
                    </button>
                  ))}
                </div>
              </div>

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

              <div className="form-group">
                <label className="form-label">Bot Protection (Cloudflare CAPTCHA)</label>
                <TurnstileWidget 
                  onVerify={(token) => setCaptchaToken(token)}
                  onError={() => setCaptchaToken(null)}
                  resetKey={captchaResetKey}
                />
              </div>

              <div style={modalActionsStyle}>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={resetModalState}
                  disabled={enterRaffleMutation.isPending}
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  className="btn btn-accent"
                  disabled={enterRaffleMutation.isPending || !selectedSize || !captchaToken}
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
  height: "220px",
  backgroundColor: "#f9f9f9",
  overflow: "hidden",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "16px",
};

const imgStyle = {
  maxWidth: "90%",
  maxHeight: "90%",
  width: "auto",
  height: "auto",
  objectFit: "contain",
  objectPosition: "center center",
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
