import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../services/api";
import ProductCard from "../components/ProductCard";
import { ProductCardSkeleton } from "../components/common/Skeleton";
import { ArrowRight, ShieldCheck, Zap, Award, Flame, Clock } from "lucide-react";
import { useToast } from "../components/common/Toast";
import { useState, useEffect } from "react";

export default function Home() {
  const toast = useToast();
  const [emailInput, setEmailInput] = useState("");

  // Live countdown timer state for Hero featured drop
  const [timeLeft, setTimeLeft] = useState({ hours: 14, minutes: 32, seconds: 45, ms: 8 });

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.seconds > 0) return { ...prev, seconds: prev.seconds - 1 };
        if (prev.minutes > 0) return { ...prev, minutes: 59, seconds: 59 };
        if (prev.hours > 0) return { ...prev, hours: prev.hours - 1, minutes: 59, seconds: 59 };
        return { hours: 24, minutes: 0, seconds: 0, ms: 0 };
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Retrieve products list
  const { data: products, isLoading, isError } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await api.get("/products");
      return res.data;
    }
  });

  const handleSubscribe = (e) => {
    e.preventDefault();
    if (!emailInput || !emailInput.includes("@")) {
      toast.error("Please enter a valid email address");
      return;
    }
    toast.success("ACCESS GRANTED! We will alert you on shock drops.");
    setEmailInput("");
  };

  const [catalogFilter, setCatalogFilter] = useState("all");

  const filteredCatalog = products ? products.filter(p => {
    if (catalogFilter === "buyable") return !p.is_reserved_for_drop;
    if (catalogFilter === "reserved") return p.is_reserved_for_drop;
    return true;
  }) : [];

  return (
    <div style={{ backgroundColor: "var(--bg-main)", color: "var(--text-primary)" }}>
      
      {/* 1. TICKER BANNER */}
      <div className="ticker-wrap">
        <div className="ticker-move">
          OFFICIAL SNEAKDROP RELEASES &nbsp;///&nbsp; 100% BOT FREE DRAW SYSTEM &nbsp;///&nbsp; SHOCK DROPS LIVE NOW &nbsp;///&nbsp; VERIFIED RETAIL GUARANTEE &nbsp;///&nbsp; OFFICIAL SNEAKDROP RELEASES &nbsp;///&nbsp; 100% BOT FREE DRAW SYSTEM &nbsp;///&nbsp; SHOCK DROPS LIVE NOW &nbsp;///&nbsp; VERIFIED RETAIL GUARANTEE &nbsp;///&nbsp;
        </div>
      </div>

      {/* 2. NIKE SNKRS STYLE HERO BANNER */}
      <section style={heroSectionStyle}>
        <div className="container" style={heroContainerStyle}>
          <div style={heroContentStyle}>
            <div style={heroTagContainer}>
              <span className="badge badge-neon" style={{ gap: "6px", padding: "6px 12px", background: "var(--accent-red)", color: "#FFF" }}>
                <Flame size={14} fill="#FFF" /> SHOCK DROP LIVE
              </span>
              <span style={{ fontSize: "12px", fontWeight: "700", letterSpacing: "0.1em", color: "var(--accent-volt)" }}>
                LIMITED ALLOCATION
              </span>
            </div>

            <h1 style={heroHeadlineStyle}>
              AIR JORDAN 1 RETRO HIGH OG
            </h1>
            
            <p style={heroSubStyle}>
              Skip the bots. Step into the drop circle. Verified raffle entries end strictly when timer expires.
            </p>

            {/* SNKRS Countdown Clock */}
            <div style={timerWrapStyle}>
              <div style={timerHeaderStyle}>
                <Clock size={15} style={{ color: "var(--accent-red)" }} />
                <span>RAFFLE CLOSES IN:</span>
              </div>
              <div style={{ display: "flex", gap: "10px" }}>
                <div className="timer-box">
                  <div className="timer-num">{String(timeLeft.hours).padStart(2, '0')}</div>
                  <div className="timer-label">HOURS</div>
                </div>
                <div className="timer-box">
                  <div className="timer-num">{String(timeLeft.minutes).padStart(2, '0')}</div>
                  <div className="timer-label">MINS</div>
                </div>
                <div className="timer-box">
                  <div className="timer-num">{String(timeLeft.seconds).padStart(2, '0')}</div>
                  <div className="timer-label">SECS</div>
                </div>
              </div>
            </div>

            <div style={heroCtaRowStyle}>
              <Link to="/drops" className="btn btn-accent" style={{ padding: "18px 40px", fontSize: "14px", fontWeight: "900", letterSpacing: "0.1em" }}>
                ENTER RAFFLE NOW
              </Link>
              <a href="#latest-catalog" className="btn btn-outline" style={{ padding: "18px 40px", fontSize: "14px", fontWeight: "900" }}>
                BROWSE CATALOG
              </a>
            </div>
          </div>

          <div style={heroImageContainerStyle}>
            <div className="hover-zoom" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <img
                src="/red-shoe-hero.png"
                alt="Featured Air Jordan Red Shoe Grail"
                style={heroImgStyle}
              />
            </div>
            {/* Glowing Accent Ring */}
            <div style={heroGlowStyle} />
          </div>
        </div>
      </section>

      {/* 3. VALUE PROPOSITIONS */}
      <section style={valueSectionStyle}>
        <div className="container" style={valueContainerStyle}>
          <div style={valueCardStyle}>
            <ShieldCheck size={32} style={{ color: "var(--accent-red)" }} />
            <h3 style={valueTitleStyle}>100% BOT FREE</h3>
            <p style={valueTextStyle}>Verified user credentials keep releases 100% fair for real sneakerheads.</p>
          </div>
          <div style={valueCardStyle}>
            <Zap size={32} style={{ color: "var(--accent-volt)" }} />
            <h3 style={valueTitleStyle}>LIVE COUNTDOWNS</h3>
            <p style={valueTextStyle}>Real-time draw verification and instant notification on winning allocations.</p>
          </div>
          <div style={valueCardStyle}>
            <Award size={32} style={{ color: "var(--accent-red)" }} />
            <h3 style={valueTitleStyle}>AUTHENTIC GUARANTEE</h3>
            <p style={valueTextStyle}>Every sneaker sourced directly from official brand partners with retail invoices.</p>
          </div>
        </div>
      </section>

      {/* 4. LATEST RELEASES CATALOG */}
      <section id="latest-catalog" style={catalogSectionStyle}>
        <div className="container">
          <div style={sectionHeaderStyle}>
            <div>
              <span style={sectionSubTitleStyle}>SNEAKDROP EXCLUSIVES</span>
              <h2 style={sectionTitleStyle}>CURRENT HEAT & DROPS</h2>
            </div>
            <Link to="/drops" style={sectionLinkStyle}>
              View All Active Raffles <ArrowRight size={18} />
            </Link>
          </div>

          {/* Catalog Filter Controls */}
          <div style={{ display: "flex", gap: "10px", marginBottom: "24px", flexWrap: "wrap" }}>
            <button 
              onClick={() => setCatalogFilter("all")} 
              className={catalogFilter === "all" ? "btn btn-accent" : "btn btn-outline"} 
              style={{ padding: "8px 16px", fontSize: "12px" }}
            >
              ALL RELEASES ({products?.length || 0})
            </button>
            <button 
              onClick={() => setCatalogFilter("buyable")} 
              className={catalogFilter === "buyable" ? "btn btn-accent" : "btn btn-outline"} 
              style={{ padding: "8px 16px", fontSize: "12px" }}
            >
              AVAILABLE NOW ({products?.filter(p => !p.is_reserved_for_drop).length || 0})
            </button>
            <button 
              onClick={() => setCatalogFilter("reserved")} 
              className={catalogFilter === "reserved" ? "btn btn-accent" : "btn btn-outline"} 
              style={{ padding: "8px 16px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "4px" }}
            >
              <Flame size={14} /> DROP PREVIEWS ({products?.filter(p => p.is_reserved_for_drop).length || 0})
            </button>
          </div>

          {isLoading ? (
            <div className="grid-cols-4">
              <ProductCardSkeleton />
              <ProductCardSkeleton />
              <ProductCardSkeleton />
              <ProductCardSkeleton />
            </div>
          ) : isError ? (
            <div style={errorContainerStyle}>
              <p>Failed to retrieve current drops catalog. Check server status.</p>
            </div>
          ) : filteredCatalog && filteredCatalog.length === 0 ? (
            <div style={emptyContainerStyle}>
              <p>No products match the selected catalog filter.</p>
            </div>
          ) : (
            <div className="grid-cols-4">
              {filteredCatalog.slice(0, 8).map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* 5. NEWSLETTER / SHOCK DROP ALERTS */}
      <section style={newsletterSectionStyle}>
        <div className="container" style={newsContainerStyle}>
          <div style={newsHeaderStyle}>
            <span style={{ color: "var(--accent-red)", fontWeight: "900", letterSpacing: "0.15em", fontSize: "12px" }}>
              VIP ACCESS LIST
            </span>
            <h2 style={newsTitleStyle}>NEVER MISS A SHOCK DROP</h2>
            <p style={newsSubStyle}>Join our early access roster to receive instant SMS & email alerts for unannounced draws.</p>
          </div>
          <form onSubmit={handleSubscribe} style={newsFormStyle}>
            <input
              type="email"
              placeholder="ENTER YOUR EMAIL FOR EARLY ACCESS"
              style={newsInputStyle}
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
            />
            <button type="submit" className="btn btn-accent" style={newsBtnStyle}>
              JOIN ROSTER
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}

// Inline styling specs for Nike Streetwear aesthetics
const heroSectionStyle = {
  backgroundColor: "#0F0F11",
  padding: "60px 0 80px 0",
  borderBottom: "1px solid var(--border-color)",
};

const heroContainerStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
  gap: "48px",
  alignItems: "center",
  minHeight: "480px",
};

const heroContentStyle = {
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
};

const heroTagContainer = {
  display: "flex",
  alignItems: "center",
  gap: "14px",
  marginBottom: "20px",
};

const heroHeadlineStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "clamp(42px, 6vw, 72px)",
  fontWeight: "900",
  color: "#FFFFFF",
  lineHeight: "0.95",
  letterSpacing: "0.02em",
  marginBottom: "18px",
  textTransform: "uppercase",
};

const heroSubStyle = {
  fontSize: "16px",
  color: "var(--text-muted)",
  marginBottom: "28px",
  maxWidth: "500px",
  lineHeight: "1.6",
};

const timerWrapStyle = {
  marginBottom: "32px",
  padding: "16px 20px",
  background: "#18181C",
  border: "1px solid var(--border-color)",
  display: "inline-flex",
  flexDirection: "column",
  gap: "10px",
  width: "fit-content"
};

const timerHeaderStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  fontSize: "11px",
  fontWeight: "800",
  letterSpacing: "0.1em",
  color: "#FFFFFF"
};

const heroCtaRowStyle = {
  display: "flex",
  gap: "16px",
  flexWrap: "wrap",
};

const heroImageContainerStyle = {
  position: "relative",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const heroImgStyle = {
  maxWidth: "115%",
  maxHeight: "504px",
  objectFit: "contain",
  zIndex: 2,
  transform: "rotate(-14deg) scale(1.2)",
  filter: "drop-shadow(0 25px 35px rgba(255, 42, 0, 0.25))",
};

const heroGlowStyle = {
  position: "absolute",
  width: "384px",
  height: "384px",
  borderRadius: "50%",
  background: "radial-gradient(circle, rgba(255,42,0,0.2) 0%, rgba(0,0,0,0) 70%)",
  zIndex: 1,
};

const valueSectionStyle = {
  backgroundColor: "#141417",
  padding: "48px 0",
  borderBottom: "1px solid var(--border-color)",
};

const valueContainerStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
  gap: "32px",
};

const valueCardStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  textAlign: "center",
  padding: "24px",
  background: "#1A1A1E",
  border: "1px solid var(--border-color)"
};

const valueTitleStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "18px",
  fontWeight: "900",
  letterSpacing: "0.08em",
  color: "#FFFFFF",
  marginTop: "16px",
  marginBottom: "8px",
};

const valueTextStyle = {
  fontSize: "13px",
  color: "var(--text-muted)",
  lineHeight: "1.5",
};

const catalogSectionStyle = {
  padding: "80px 0",
};

const sectionHeaderStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-end",
  marginBottom: "40px",
};

const sectionSubTitleStyle = {
  fontSize: "11px",
  fontWeight: "900",
  color: "var(--accent-red)",
  letterSpacing: "0.15em",
  display: "block",
  marginBottom: "4px",
};

const sectionTitleStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "36px",
  fontWeight: "900",
  color: "#FFFFFF",
  letterSpacing: "0.04em"
};

const sectionLinkStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  fontFamily: "var(--font-display)",
  fontSize: "16px",
  fontWeight: "800",
  letterSpacing: "0.08em",
  color: "var(--accent-red)",
  paddingBottom: "4px",
};

const errorContainerStyle = {
  textAlign: "center",
  padding: "48px 0",
  color: "var(--error)",
};

const emptyContainerStyle = {
  textAlign: "center",
  padding: "48px 0",
  color: "var(--text-muted)",
};

const newsletterSectionStyle = {
  backgroundColor: "#0F0F11",
  color: "#FFFFFF",
  padding: "80px 0",
  textAlign: "center",
  borderTop: "1px solid var(--border-color)",
};

const newsContainerStyle = {
  maxWidth: "640px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "24px",
  margin: "0 auto"
};

const newsHeaderStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const newsTitleStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "42px",
  fontWeight: "900",
  letterSpacing: "0.04em",
  color: "#FFFFFF",
};

const newsSubStyle = {
  fontSize: "15px",
  color: "var(--text-muted)",
};

const newsFormStyle = {
  display: "flex",
  width: "100%",
  maxWidth: "520px",
  gap: "12px",
};

const newsInputStyle = {
  flex: 1,
  padding: "16px 20px",
  backgroundColor: "#18181C",
  border: "1px solid var(--border-color)",
  color: "#FFFFFF",
  fontSize: "12px",
  fontWeight: "700",
  letterSpacing: "0.05em",
};

const newsBtnStyle = {
  padding: "16px 32px",
  fontSize: "13px",
  fontWeight: "900",
  letterSpacing: "0.08em"
};