import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import { ProductDetailsSkeleton } from "../components/common/Skeleton";
import api from "../services/api";
import { ShoppingCart, ChevronLeft, ShieldCheck, Truck, RefreshCw } from "lucide-react";

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isLoggedIn } = useContext(AuthContext);

  const [quantity, setQuantity] = useState(1);
  const [selectedSize, setSelectedSize] = useState("");

  const STANDARD_SIZES = ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 11.5", "US 12"];

  // Fetch all products to find details by ID locally (FastAPI lacks GET /products/{id})
  const { 
    data: products = [], 
    isLoading, 
    isError, 
    error 
  } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await api.get("/products");
      return res.data;
    }
  });

  // Filter to find the target product
  const product = products.find(p => p.product_id === parseInt(id, 10));

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: async ({ productId, qty, size }) => {
      if (!isLoggedIn) {
        throw new Error("unauthorized");
      }
      return await api.post("/cart", {
        product_id: productId,
        quantity: qty,
        size: size,
      });
    },
    onSuccess: () => {
      toast.success(`${product.name} added to cart successfully!`);
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (err) => {
      if (err.message === "unauthorized") {
        toast.warning("Please login to add items to your cart");
        navigate("/login");
      } else {
        const detail = err.response?.data?.detail || "Insufficient stock to fulfill request.";
        toast.error(detail);
      }
    }
  });

  const handleAddToCart = () => {
    if (!product) return;
    addToCartMutation.mutate({ productId: product.product_id, qty: quantity, size: selectedSize });
  };

  if (isLoading) {
    return (
      <div className="container animate-fade-in" style={{ padding: "40px 24px" }}>
        <ProductDetailsSkeleton />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container" style={centerPanelStyle}>
        <h3 style={{ color: "var(--error)" }}>FAILED TO LOAD CATALOG</h3>
        <p style={{ color: "var(--text-muted)", margin: "12px 0 24px 0" }}>{error.message}</p>
        <Link to="/" className="btn btn-primary">GO HOME</Link>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="container" style={centerPanelStyle}>
        <h3>PRODUCT NOT FOUND</h3>
        <p style={{ color: "var(--text-muted)", margin: "12px 0 24px 0" }}>The product ID #{id} does not exist in our system.</p>
        <Link to="/" className="btn btn-primary">BACK TO CATALOG</Link>
      </div>
    );
  }

  const isOutOfStock = product.stock <= 0;
  const imageUrl = product.images 
    ? product.images.split(",")[0] 
    : "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop";

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: "64px" }}>
      {/* Back button */}
      <Link to="/" style={backLinkStyle}>
        <ChevronLeft size={16} /> BACK TO SHOP
      </Link>

      <div style={gridStyle}>
        {/* Gallery Panel */}
        <div style={galleryPanelStyle}>
          <div className="premium-panel" style={imgCardStyle}>
            <img src={imageUrl} alt={product.name} style={imgStyle} />
          </div>
        </div>

        {/* Buying Actions Panel */}
        <div style={buyPanelStyle}>
          {/* Badge & Title */}
          <div>
            {isOutOfStock ? (
              <span className="badge badge-danger">OUT OF STOCK</span>
            ) : product.stock < 5 ? (
              <span className="badge badge-warning">ONLY {product.stock} PAIRS LEFT</span>
            ) : (
              <span className="badge badge-neon">EXCLUSIVELY IN STOCK</span>
            )}
            <h1 style={titleStyle}>{product.name}</h1>
            <span style={priceStyle}>${Number(product.price).toFixed(2)}</span>
          </div>

          {/* Description */}
          <div>
            <h4 style={subHeadingStyle}>DESCRIPTION</h4>
            <p style={descriptionStyle}>
              {product.description || "Premium sneakers built with durability and comfort. Features high-grade leather paneling, custom insoles, and signature sneakerstuff details. Cop your pair today."}
            </p>
          </div>

          {/* Size Selector */}
          {!isOutOfStock && (
            <div>
              <h4 style={subHeadingStyle}>SELECT SIZE</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '24px' }}>
                {STANDARD_SIZES.map(sz => {
                  let isEnabled = true;
                  if (product.sizes && Array.isArray(product.sizes) && product.sizes.length > 0) {
                    const sizeObj = product.sizes.find(s => s.size === sz);
                    isEnabled = sizeObj && sizeObj.stock > 0;
                  }
                  return (
                    <button
                      key={sz}
                      onClick={() => isEnabled && setSelectedSize(sz)}
                      disabled={!isEnabled}
                      style={{
                        width: '60px',
                        padding: '12px 0',
                        textAlign: 'center',
                        border: selectedSize === sz ? '2px solid var(--accent-red)' : '1px solid var(--border-color)',
                        backgroundColor: selectedSize === sz ? 'rgba(227, 6, 19, 0.1)' : 'var(--bg-input)',
                        color: isEnabled ? 'var(--text-primary)' : 'var(--text-muted)',
                        borderRadius: '4px',
                        cursor: isEnabled ? 'pointer' : 'not-allowed',
                        opacity: isEnabled ? 1 : 0.5,
                        textDecoration: isEnabled ? 'none' : 'line-through',
                        fontFamily: 'var(--font-display)',
                        fontWeight: selectedSize === sz ? '800' : '500',
                        fontSize: '12px',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {sz}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Quantity selector & Add to cart */}
          {!isOutOfStock && (
            <div style={controlsRowStyle}>
              <div style={qtySelectorStyle}>
                <button 
                  onClick={() => setQuantity(q => Math.max(1, q - 1))} 
                  style={qtyBtnStyle}
                  disabled={quantity <= 1}
                >
                  -
                </button>
                <span style={qtyValueStyle}>{quantity}</span>
                <button 
                  onClick={() => setQuantity(q => Math.min(product.stock, q + 1))} 
                  style={qtyBtnStyle}
                  disabled={quantity >= product.stock}
                >
                  +
                </button>
              </div>

              <button 
                onClick={handleAddToCart} 
                className="btn btn-accent" 
                style={addCartBtnStyle}
                disabled={addToCartMutation.isPending || !selectedSize}
              >
                {addToCartMutation.isPending ? "ADDING..." : <>ADD TO CART <ShoppingCart size={18} /></>}
              </button>
            </div>
          )}

          {/* Guarantees */}
          <div style={guaranteesPanelStyle}>
            <div style={guaranteeItemStyle}>
              <ShieldCheck size={18} style={{ color: "var(--text-primary)" }} />
              <div>
                <h5 style={guaranteeTitleStyle}>100% Authentic Guarantee</h5>
                <p style={guaranteeDescStyle}>Every sneaker sold here is fully authenticated.</p>
              </div>
            </div>

            <div style={guaranteeItemStyle}>
              <Truck size={18} style={{ color: "var(--text-primary)" }} />
              <div>
                <h5 style={guaranteeTitleStyle}>Expedited Shipping</h5>
                <p style={guaranteeDescStyle}>Fast delivery to your address inside double boxes.</p>
              </div>
            </div>

            <div style={guaranteeItemStyle}>
              <RefreshCw size={18} style={{ color: "var(--text-primary)" }} />
              <div>
                <h5 style={guaranteeTitleStyle}>Raffle-Proof Policy</h5>
                <p style={guaranteeDescStyle}>Raffle winners receive priority checkout windows.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Styles
const backLinkStyle = {
  display: "inline-flex",
  alignItems: "center",
  gap: "6px",
  color: "var(--text-muted)",
  fontSize: "14px",
  fontWeight: "700",
  fontFamily: "var(--font-display)",
  margin: "24px 0",
  transition: "color var(--transition-fast)",
};

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: "48px",
};

// Responsiveness handled inside JS style configuration or standard media rules
if (typeof window !== "undefined" && window.innerWidth >= 1024) {
  gridStyle.gridTemplateColumns = "1.2fr 1fr";
}

const galleryPanelStyle = {
  display: "flex",
  flexDirection: "column",
};

const imgCardStyle = {
  padding: "32px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
  aspectRatio: "1.2",
};

const imgStyle = {
  width: "100%",
  height: "100%",
  objectFit: "contain",
};

const buyPanelStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "32px",
};

const titleStyle = {
  fontSize: "36px",
  color: "var(--text-primary)",
  marginTop: "12px",
  lineHeight: "1.2",
};

const priceStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "28px",
  fontWeight: "900",
  color: "var(--text-primary)",
  display: "block",
  marginTop: "8px",
};

const subHeadingStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "12px",
  color: "var(--text-muted)",
  letterSpacing: "0.15em",
  marginBottom: "12px",
};

const descriptionStyle = {
  color: "var(--text-muted)",
  fontSize: "15px",
  lineHeight: "1.6",
};

const controlsRowStyle = {
  display: "flex",
  gap: "16px",
  alignItems: "center",
};

const qtySelectorStyle = {
  display: "inline-flex",
  alignItems: "center",
  backgroundColor: "var(--bg-input)",
  border: "1px solid var(--border-color)",
  borderRadius: "var(--border-radius-md)",
  padding: "4px",
};

const qtyBtnStyle = {
  width: "40px",
  height: "40px",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontWeight: "700",
  fontSize: "18px",
};

const qtyValueStyle = {
  fontFamily: "var(--font-display)",
  fontWeight: "700",
  width: "36px",
  textAlign: "center",
};

const addCartBtnStyle = {
  flexGrow: 1,
  padding: "16px",
};

const guaranteesPanelStyle = {
  borderTop: "1px solid var(--border-color)",
  paddingTop: "24px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const guaranteeItemStyle = {
  display: "flex",
  gap: "16px",
};

const guaranteeTitleStyle = {
  fontSize: "14px",
  color: "var(--text-primary)",
};

const guaranteeDescStyle = {
  fontSize: "12px",
  color: "var(--text-muted)",
};

const centerPanelStyle = {
  textAlign: "center",
  padding: "80px 24px",
};
