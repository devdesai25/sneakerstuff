/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../services/api";
import ProductCard from "../components/ProductCard";
import { ProductCardSkeleton } from "../components/common/Skeleton";
import { ArrowRight, ShieldCheck, Zap, Award } from "lucide-react";
import { useToast } from "../components/common/Toast";
import { useState } from "react";

export default function Home() {
  const toast = useToast();
  const [emailInput, setEmailInput] = useState("");

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
    toast.success("Subscribed! We will alert you on the next drop.");
    setEmailInput("");
  };

  return (
    <div style={{ backgroundColor: "#ffffff" }}>
      {/* 1. HERO SECTION (Foot Locker Premium White/Black/Red Style) */}
      <section style={heroSectionStyle}>
        <div className="container" style={heroContainerStyle}>
          <div style={heroContentStyle}>
            <span style={heroTagStyle}>EXCLUSIVE RELEASES</span>
            <h1 style={heroHeadlineStyle}>
              Limited Releases.<br />
              Fair Raffles.
            </h1>
            <p style={heroSubStyle}>
              Skip the bots. Get access to the most anticipated sneaker releases of the season through our transparent draw system.
            </p>
            <div style={heroCtaRowStyle}>
              <Link to="/drops" className="btn btn-accent" style={{ padding: "16px 36px", fontSize: "13px" }}>
                EXPLORE DROPS
              </Link>
              <a href="#latest-catalog" className="btn btn-outline" style={{ padding: "16px 36px", fontSize: "13px" }}>
                BROWSE PRODUCTS
              </a>
            </div>
          </div>
          <div style={heroImageContainerStyle}>
            <img
              src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=800"
              alt="Featured Sneaker Grail"
              style={heroImgStyle}
            />
            {/* Minimal highlight circle */}
            <div style={heroBgDecorStyle} />
          </div>
        </div>
      </section>

      {/* 2. WHY SNEAKERSTUFF (Value Propositions) */}
      <section style={valueSectionStyle}>
        <div className="container" style={valueContainerStyle}>
          <div style={valueCardStyle}>
            <ShieldCheck size={28} style={{ color: "var(--accent-red)" }} />
            <h3 style={valueTitleStyle}>100% BOT FREE</h3>
            <p style={valueTextStyle}>Verified user accounts and double-entry filtering keeps releases fair for real collectors.</p>
          </div>
          <div style={valueCardStyle}>
            <Zap size={28} style={{ color: "var(--accent-red)" }} />
            <h3 style={valueTitleStyle}>LIVE COUNTDOWNS</h3>
            <p style={valueTextStyle}>Watch active clocks draw to a close and get notified immediately on winning allocations.</p>
          </div>
          <div style={valueCardStyle}>
            <Award size={28} style={{ color: "var(--accent-red)" }} />
            <h3 style={valueTitleStyle}>OFFICIAL RELEASES</h3>
            <p style={valueTextStyle}>All sneakers are sourced directly from brands and certified partners with retail guarantees.</p>
          </div>
        </div>
      </section>

      {/* 3. LATEST PRODUCTS CATALOG */}
      <section id="latest-catalog" style={catalogSectionStyle}>
        <div className="container">
          <div style={sectionHeaderStyle}>
            <div>
              <span style={sectionSubTitleStyle}>SNEAKERSTUFF HYPE SHEET</span>
              <h2 style={sectionTitleStyle}>LATEST RELEASES</h2>
            </div>
            <Link to="/drops" style={sectionLinkStyle}>
              View Active Raffles <ArrowRight size={16} />
            </Link>
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
              <p>Failed to retrieve latest catalog. Check your connection.</p>
            </div>
          ) : products && products.length === 0 ? (
            <div style={emptyContainerStyle}>
              <p>No products currently available in the catalog.</p>
            </div>
          ) : (
            <div className="grid-cols-4">
              {products.slice(0, 8).map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* 4. NEWSLETTER SUBSCRIPTION SECTION */}
      <section style={newsletterSectionStyle}>
        <div className="container" style={newsContainerStyle}>
          <div style={newsHeaderStyle}>
            <h2 style={newsTitleStyle}>NEVER MISS A RELEASE</h2>
            <p style={newsSubStyle}>Join our mailing list to receive notification alerts on upcoming shock drops and raffles.</p>
          </div>
          <form onSubmit={handleSubscribe} style={newsFormStyle}>
            <input
              type="email"
              placeholder="Enter your email address"
              style={newsInputStyle}
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" style={newsBtnStyle}>
              SUBSCRIBE
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}

// Styling specifications for Home Page
const heroSectionStyle = {
  backgroundColor: "#ffffff",
  padding: "80px 0 100px 0",
  borderBottom: "1px solid var(--border-color)",
};

const heroContainerStyle = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: "48px",
  alignItems: "center",
  minHeight: "440px",
  "@media (min-width: 1024px)": {
    gridTemplateColumns: "1.2fr 1fr",
  }
};

// Inline media query mock helper
if (window.innerWidth >= 1024) {
  heroContainerStyle.gridTemplateColumns = "1.2fr 1.1fr";
}

const heroContentStyle = {
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
};

const heroTagStyle = {
  fontSize: "11px",
  fontWeight: "800",
  letterSpacing: "0.15em",
  color: "var(--accent-red)",
  marginBottom: "16px",
};

const heroHeadlineStyle = {
  fontSize: "clamp(36px, 5vw, 54px)",
  fontWeight: "900",
  color: "var(--text-primary)",
  lineHeight: "1.05",
  marginBottom: "20px",
};

const heroSubStyle = {
  fontSize: "16px",
  color: "var(--text-muted)",
  marginBottom: "36px",
  maxWidth: "480px",
  lineHeight: "1.6",
};

const heroCtaRowStyle = {
  display: "flex",
  gap: "14px",
  flexWrap: "wrap",
};

const heroImageContainerStyle = {
  position: "relative",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const heroImgStyle = {
  maxWidth: "90%",
  maxHeight: "360px",
  objectFit: "contain",
  zIndex: 2,
  transform: "rotate(-12deg)",
  filter: "drop-shadow(0 20px 30px rgba(0,0,0,0.12))",
};

const heroBgDecorStyle = {
  position: "absolute",
  width: "280px",
  height: "280px",
  borderRadius: "50%",
  backgroundColor: "var(--bg-secondary)",
  zIndex: 1,
};

const valueSectionStyle = {
  backgroundColor: "#f6f6f6",
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
};

const valueTitleStyle = {
  fontSize: "13px",
  fontWeight: "800",
  letterSpacing: "0.08em",
  color: "var(--text-primary)",
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
  fontSize: "10px",
  fontWeight: "800",
  color: "var(--accent-red)",
  letterSpacing: "0.15em",
  display: "block",
  marginBottom: "6px",
};

const sectionTitleStyle = {
  fontSize: "24px",
  fontWeight: "900",
  color: "var(--text-primary)",
};

const sectionLinkStyle = {
  display: "flex",
  alignItems: "center",
  gap: "6px",
  fontSize: "13px",
  fontWeight: "700",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  color: "var(--text-primary)",
  borderBottom: "2px solid var(--text-primary)",
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
  backgroundColor: "#111111",
  color: "#ffffff",
  padding: "64px 0",
  textAlign: "center",
};

const newsContainerStyle = {
  maxWidth: "600px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "24px",
};

const newsHeaderStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const newsTitleStyle = {
  fontSize: "22px",
  fontWeight: "900",
  letterSpacing: "0.05em",
  color: "#ffffff",
};

const newsSubStyle = {
  fontSize: "14px",
  color: "#aaaaaa",
};

const newsFormStyle = {
  display: "flex",
  width: "100%",
  maxWidth: "480px",
  gap: "10px",
};

const newsInputStyle = {
  flex: 1,
  padding: "12px 18px",
  backgroundColor: "#222222",
  border: "1px solid #333333",
  color: "#ffffff",
  fontSize: "13px",
  borderRadius: "4px",
};

const newsBtnStyle = {
  padding: "12px 24px",
  fontSize: "12px",
  backgroundColor: "#ffffff",
  color: "#111111",
  fontWeight: "700",
  border: "1px solid #ffffff",
};