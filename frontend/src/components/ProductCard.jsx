import { Link } from "react-router-dom";
import { Heart, ShoppingBag, Eye, Flame } from "lucide-react";
import { useState } from "react";

export default function ProductCard({ product, onAddToCart }) {
  const [isWishlisted, setIsWishlisted] = useState(false);

  // Helper to split brand from title (e.g. "Nike Air Max" -> Brand: "NIKE", Model: "AIR MAX")
  const getBrandAndName = (fullName) => {
    if (!fullName) return { brand: "SNEAKDROP", name: "Limited Edition" };
    const parts = fullName.split(" ");
    if (parts.length > 1) {
      return {
        brand: parts[0].toUpperCase(),
        name: parts.slice(1).join(" ")
      };
    }
    return { brand: "SNEAKDROP", name: fullName };
  };

  const { brand, name } = getBrandAndName(product.name);

  // Format currency
  const formatPrice = (price) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2
    }).format(price);
  };

  const isReserved = product.is_reserved_for_drop;

  return (
    <div className="snkrs-card" style={cardStyle}>
      {/* Product Image Panel */}
      <div className="hover-zoom" style={imgContainerStyle}>
        <Link to={`/product/${product.product_id}`} style={imgLinkStyle}>
          <img
            src={product.images || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600"}
            alt={product.name}
            style={imgStyle}
            onError={(e) => {
              e.target.src = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600";
            }}
          />
        </Link>

        {/* Wishlist Heart Toggle */}
        <button 
          onClick={() => setIsWishlisted(!isWishlisted)}
          style={wishlistBtnStyle}
          aria-label="Add to Wishlist"
        >
          <Heart size={16} fill={isWishlisted ? "var(--accent-red)" : "none"} stroke={isWishlisted ? "var(--accent-red)" : "currentColor"} />
        </button>

        {/* Stock / Drop Reserved status badge overlay */}
        {isReserved ? (
          <span className="badge" style={{ ...badgeOverlayStyle, backgroundColor: "#E30613", color: "#FFFFFF", gap: "4px" }}>
            <Flame size={12} fill="#FFF" /> RESERVED FOR DROP
          </span>
        ) : product.stock <= 0 ? (
          <span className="badge badge-danger" style={badgeOverlayStyle}>SOLD OUT</span>
        ) : product.stock <= 5 ? (
          <span className="badge badge-warning" style={badgeOverlayStyle}>ONLY {product.stock} LEFT</span>
        ) : null}
      </div>

      {/* Product Info Panel */}
      <div style={infoStyle}>
        <div style={brandStyle}>{brand}</div>
        <Link to={`/product/${product.product_id}`}>
          <h3 style={titleStyle}>{name}</h3>
        </Link>
        <div style={priceRowStyle}>
          <span style={priceStyle}>{formatPrice(product.price)}</span>
        </div>
      </div>

      {/* Action Buttons Footer */}
      <div style={actionsContainerStyle}>
        <Link to={`/product/${product.product_id}`} className="btn btn-outline" style={{ flex: 1, padding: "10px", fontSize: "11px", gap: "4px" }}>
          <Eye size={13} /> DETAILS
        </Link>
        {isReserved ? (
          <Link
            to={`/product/${product.product_id}`}
            className="btn btn-outline"
            style={{ flex: 1.2, padding: "10px", fontSize: "11px", gap: "4px", color: "var(--accent-red)", borderColor: "var(--accent-red)", display: "inline-flex", alignItems: "center", justifyContent: "center" }}
          >
            <Flame size={13} /> DROP PREVIEW
          </Link>
        ) : onAddToCart !== false && (
          <Link
            to={`/product/${product.product_id}`}
            className="btn btn-primary"
            style={{ flex: 1.2, padding: "10px", fontSize: "11px", gap: "4px", display: "inline-flex", alignItems: "center", justifyContent: "center" }}
          >
            <ShoppingBag size={13} /> SELECT SIZE
          </Link>
        )}
      </div>
    </div>
  );
}

// Card Style Specifications
const cardStyle = {
  backgroundColor: "var(--bg-card)",
  border: "1px solid var(--border-color)",
  borderRadius: "var(--border-radius-sm)",
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
  transition: "transform var(--transition-normal), box-shadow var(--transition-normal)",
  height: "100%",
  ":hover": {
    transform: "translateY(-4px)",
    boxShadow: "var(--shadow-md)"
  }
};

const imgContainerStyle = {
  position: "relative",
  paddingTop: "100%", /* 1:1 Aspect Ratio square box */
  backgroundColor: "#f9f9f9",
  overflow: "hidden",
};

const imgLinkStyle = {
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const imgStyle = {
  maxWidth: "90%",
  maxHeight: "90%",
  objectFit: "contain",
  transition: "transform 0.4s ease",
};

const wishlistBtnStyle = {
  position: "absolute",
  top: "14px",
  right: "14px",
  width: "36px",
  height: "36px",
  borderRadius: "50%",
  backgroundColor: "var(--bg-main)",
  border: "1px solid var(--border-color)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
  color: "var(--text-primary)",
  transition: "all var(--transition-fast)",
  boxShadow: "0 2px 6px rgba(0,0,0,0.04)"
};

const badgeOverlayStyle = {
  position: "absolute",
  bottom: "14px",
  left: "14px",
  boxShadow: "var(--shadow-sm)",
};

const infoStyle = {
  padding: "20px 20px 12px 20px",
  display: "flex",
  flexDirection: "column",
  flexGrow: 1,
};

const brandStyle = {
  fontSize: "11px",
  fontWeight: "800",
  color: "var(--accent-red)",
  letterSpacing: "0.08em",
  marginBottom: "4px",
};

const titleStyle = {
  fontSize: "15px",
  fontWeight: "800",
  lineHeight: "1.3",
  color: "var(--text-primary)",
  marginBottom: "8px",
  whiteSpace: "nowrap",
  overflow: "hidden",
  textOverflow: "ellipsis",
};

const priceRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginTop: "auto",
};

const priceStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "16px",
  fontWeight: "800",
  color: "var(--text-primary)",
};

const actionsContainerStyle = {
  display: "flex",
  gap: "8px",
  padding: "0 20px 20px 20px",
  marginTop: "auto",
};
