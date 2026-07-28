import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, Link } from "react-router-dom";
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import api from "../services/api";
import { ShoppingBag, Trash2, Plus, Minus, CreditCard, ChevronRight } from "lucide-react";

export default function Cart() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const toast = useToast();
  const { isLoggedIn } = useContext(AuthContext);

  const [address, setAddress] = useState("");

  // Get cart query
  const { 
    data: cartItems = [], 
    isLoading, 
    isError, 
    error 
  } = useQuery({
    queryKey: ["cart"],
    queryFn: async () => {
      if (!isLoggedIn) return [];
      const res = await api.get("/cart");
      return res.data;
    },
    enabled: isLoggedIn,
  });

  const cartTotal = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  // Cart operations mutations
  const deleteItemMutation = useMutation({
    mutationFn: async (productId) => {
      return await api.delete(`/cart/${productId}`);
    },
    onSuccess: (data, productId) => {
      const item = cartItems.find(i => i.product_id === productId);
      toast.success(`${item?.name || "Item"} removed from cart.`);
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to remove item.");
    }
  });

  // Quantity change mutation (POST workaround for broken PATCH)
  const changeQuantityMutation = useMutation({
    mutationFn: async ({ productId, change }) => {
      // If decrementing and quantity is 1 (making it 0), delete the item
      const item = cartItems.find(i => i.product_id === productId);
      if (change === -1 && item.quantity <= 1) {
        return await api.delete(`/cart/${productId}`);
      }

      // Otherwise, post the delta (positive or negative) to /cart
      return await api.post("/cart", {
        product_id: productId,
        quantity: change,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to adjust item quantity.");
    }
  });

  // Order checkout mutation
  const checkoutMutation = useMutation({
    mutationFn: async (shippingAddress) => {
      // 1. Create order on backend (POST /orders)
      const res = await api.post("/orders", { address: shippingAddress });
      const order = res.data;

      // 2. Workaround: backend order_create doesn't clear the cart.
      // We clear the cart manually by deleting each item to match e-commerce standards.
      try {
        await Promise.all(
          cartItems.map((item) => api.delete(`/cart/${item.product_id}`))
        );
      } catch (e) {
        console.error("Failed to automatically clear cart items after checkout", e);
      }

      return order;
    },
    onSuccess: () => {
      toast.success("Checkout successful! Order created.");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      // Redirect to orders page so user can initiate payment
      navigate("/orders");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Checkout failed. Verify your stock limits.");
    }
  });

  const handleCheckout = (e) => {
    e.preventDefault();
    if (!address.trim()) {
      toast.error("Please enter a valid shipping address");
      return;
    }
    checkoutMutation.mutate(address);
  };

  if (!isLoggedIn) {
    return (
      <div className="container" style={centerPanelStyle}>
        <ShoppingBag size={48} style={{ color: "var(--text-muted)", marginBottom: "16px" }} />
        <h3>YOUR CART IS LOCKED</h3>
        <p style={{ color: "var(--text-muted)", margin: "12px 0 24px 0" }}>Please login to view your cart items.</p>
        <Link to="/login" className="btn btn-primary">LOG IN</Link>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="container" style={centerPanelStyle}>
        <h3>LOADING CART...</h3>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container" style={centerPanelStyle}>
        <h3 style={{ color: "var(--error)" }}>FAILED TO RETRIEVE CART</h3>
        <p style={{ color: "var(--text-muted)", margin: "12px 0 24px 0" }}>{error.message}</p>
      </div>
    );
  }

  if (cartItems.length === 0) {
    return (
      <div className="container" style={centerPanelStyle}>
        <ShoppingBag size={48} style={{ color: "var(--text-muted)", marginBottom: "16px" }} />
        <h3>YOUR CART IS EMPTY</h3>
        <p style={{ color: "var(--text-muted)", margin: "12px 0 24px 0" }}>Add some heat to your cart from our catalog.</p>
        <Link to="/" className="btn btn-primary">GO SHOPPING</Link>
      </div>
    );
  }

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: "64px" }}>
      <h1 style={pageTitleStyle}>YOUR BAG</h1>

      <div style={layoutStyle}>
        {/* Cart items list */}
        <div style={itemsListStyle}>
          {cartItems.map((item) => {
            const imageUrl = item.image 
              ? item.image.split(",")[0] 
              : "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=200&auto=format&fit=crop";

            return (
              <div key={item.product_id} className="premium-panel" style={itemCardStyle}>
                <img src={imageUrl} alt={item.name} style={itemImgStyle} />

                <div style={itemInfoStyle}>
                  <Link to={`/product/${item.product_id}`} style={itemTitleLinkStyle}>
                    <h3 style={itemTitleStyle}>{item.name}</h3>
                  </Link>
                  <span style={itemPriceStyle}>${Number(item.price).toFixed(2)}</span>

                  <div style={qtyControlsWrapperStyle}>
                    <div style={qtyControlsStyle}>
                      <button
                        onClick={() => changeQuantityMutation.mutate({ productId: item.product_id, change: -1 })}
                        disabled={changeQuantityMutation.isPending}
                        style={qtyBtnStyle}
                      >
                        <Minus size={14} />
                      </button>
                      <span style={qtyValStyle}>{item.quantity}</span>
                      <button
                        onClick={() => changeQuantityMutation.mutate({ productId: item.product_id, change: 1 })}
                        disabled={changeQuantityMutation.isPending}
                        style={qtyBtnStyle}
                      >
                        <Plus size={14} />
                      </button>
                    </div>

                    <button
                      onClick={() => deleteItemMutation.mutate(item.product_id)}
                      disabled={deleteItemMutation.isPending}
                      style={deleteBtnStyle}
                      title="Remove item"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>

                <div style={subtotalColStyle}>
                  <span style={subtotalLabelStyle}>SUBTOTAL</span>
                  <span style={subtotalValStyle}>${Number(item.price * item.quantity).toFixed(2)}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary & Checkout Panel */}
        <div className="premium-panel" style={summaryPanelStyle}>
          <h3 style={summaryTitleStyle}>ORDER SUMMARY</h3>

          <div style={summaryRowStyle}>
            <span>Cart Subtotal</span>
            <span>${cartTotal.toFixed(2)}</span>
          </div>

          <div style={summaryRowStyle}>
            <span>Double Boxed Shipping</span>
            <span style={{ color: "var(--success)", fontWeight: "700" }}>FREE</span>
          </div>

          <div style={totalRowStyle}>
            <span>TOTAL</span>
            <span>${cartTotal.toFixed(2)}</span>
          </div>

          {/* Checkout address form */}
          <form onSubmit={handleCheckout} style={checkoutFormStyle}>
            <div className="form-group">
              <label className="form-label">Shipping Address</label>
              <textarea
                className="input-field"
                placeholder="Enter complete shipping address (e.g. Street, City, State, ZIP)"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                rows={3}
                style={{ resize: "none" }}
                disabled={checkoutMutation.isPending}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-accent"
              style={checkoutBtnStyle}
              disabled={checkoutMutation.isPending}
            >
              {checkoutMutation.isPending ? "CHECKING OUT..." : <>CHECKOUT ORDER <ChevronRight size={18} /></>}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

// Styles
const pageTitleStyle = {
  fontSize: "36px",
  margin: "32px 0 24px 0",
};

const layoutStyle = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: "32px",
};

if (typeof window !== "undefined" && window.innerWidth >= 1024) {
  layoutStyle.gridTemplateColumns = "1.8fr 1fr";
}

const itemsListStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const itemCardStyle = {
  display: "flex",
  padding: "20px",
  gap: "24px",
  alignItems: "center",
  flexWrap: "wrap",
};

const itemImgStyle = {
  width: "100px",
  height: "100px",
  objectFit: "cover",
  borderRadius: "8px",
  backgroundColor: "rgba(255, 255, 255, 0.02)",
};

const itemInfoStyle = {
  flexGrow: 1,
  display: "flex",
  flexDirection: "column",
  gap: "6px",
};

const itemTitleLinkStyle = {
  width: "fit-content",
};

const itemTitleStyle = {
  fontSize: "18px",
  color: "var(--text-primary)",
};

const itemPriceStyle = {
  color: "var(--text-muted)",
  fontSize: "14px",
  fontWeight: "600",
};

const qtyControlsWrapperStyle = {
  display: "flex",
  alignItems: "center",
  gap: "16px",
  marginTop: "8px",
};

const qtyControlsStyle = {
  display: "flex",
  alignItems: "center",
  backgroundColor: "var(--bg-input)",
  border: "1px solid var(--border-color)",
  borderRadius: "8px",
  padding: "2px",
};

const qtyBtnStyle = {
  width: "28px",
  height: "28px",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const qtyValStyle = {
  width: "24px",
  textAlign: "center",
  fontFamily: "var(--font-display)",
  fontWeight: "700",
  fontSize: "13px",
};

const deleteBtnStyle = {
  background: "transparent",
  border: "none",
  color: "var(--text-muted)",
  cursor: "pointer",
  padding: "6px",
  borderRadius: "6px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  transition: "all var(--transition-fast)",
};

const subtotalColStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
  justifyContent: "center",
  minWidth: "120px",
};

const subtotalLabelStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "9px",
  fontWeight: "700",
  color: "var(--text-muted)",
  letterSpacing: "0.15em",
};

const subtotalValStyle = {
  fontFamily: "var(--font-display)",
  fontSize: "18px",
  fontWeight: "800",
  color: "var(--text-primary)",
};

const summaryPanelStyle = {
  padding: "32px",
  height: "fit-content",
  display: "flex",
  flexDirection: "column",
  gap: "20px",
};

const summaryTitleStyle = {
  fontSize: "20px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "12px",
};

const summaryRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  fontSize: "14px",
  color: "var(--text-muted)",
};

const totalRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  fontFamily: "var(--font-display)",
  fontWeight: "800",
  fontSize: "20px",
  borderTop: "1px solid var(--border-color)",
  paddingTop: "16px",
  color: "var(--text-primary)",
};

const checkoutFormStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "12px",
  marginTop: "16px",
};

const checkoutBtnStyle = {
  width: "100%",
  padding: "16px",
};

const centerPanelStyle = {
  textAlign: "center",
  padding: "80px 24px",
};
