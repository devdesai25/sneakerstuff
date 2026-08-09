/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

import { Clock, CheckCircle, XCircle, AlertCircle, Calendar, MapPin, DollarSign } from "lucide-react";
import { useEffect, useState } from "react";

export default function OrderCard({ order, onPay, onCancel, isPaying, isCancelling }) {
  const [timeLeft, setTimeLeft] = useState("");
  const isPending = order.status?.toUpperCase() === "PENDING";

  useEffect(() => {
    if (!isPending || !order.expires_at) return;

    const updateTimer = () => {
      const now = new Date().getTime();
      const expiry = new Date(order.expires_at).getTime();
      const diff = expiry - now;

      if (diff <= 0) {
        setTimeLeft("EXPIRED");
      } else {
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const secs = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeLeft(`${mins}m ${secs}s`);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [order.expires_at, isPending]);

  const getStatusBadge = (status) => {
    switch (status?.toUpperCase()) {
      case "PAID":
        return (
          <span className="badge badge-success" style={badgeStyle}>
            <CheckCircle size={12} /> PAID
          </span>
        );
      case "CANCELLED":
        return (
          <span className="badge badge-danger" style={badgeStyle}>
            <XCircle size={12} /> CANCELLED
          </span>
        );
      case "PENDING":
        return (
          <span className="badge badge-warning" style={badgeStyle}>
            <Clock size={12} /> UNPAID RESERVATION
          </span>
        );
      default:
        return <span className="badge badge-neon" style={badgeStyle}>{status}</span>;
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  return (
    <div className="premium-panel" style={cardContainerStyle}>
      {/* Header Info */}
      <div style={headerStyle}>
        <div>
          <span style={orderIdLabelStyle}>Order Reference</span>
          <h3 style={orderIdStyle}>#STUFF-{order.order_id}</h3>
        </div>
        <div>{getStatusBadge(order.status)}</div>
      </div>

      {/* Order Info Details */}
      <div style={detailsGridStyle}>
        <div style={detailItemStyle}>
          <Calendar size={15} style={iconStyle} />
          <div>
            <span style={labelStyle}>Date Created</span>
            <span style={valueStyle}>{formatDate(order.created_at || new Date())}</span>
          </div>
        </div>

        <div style={detailItemStyle}>
          <MapPin size={15} style={iconStyle} />
          <div>
            <span style={labelStyle}>Shipping Address</span>
            <span style={valueStyle}>{order.address || "No address supplied"}</span>
          </div>
        </div>

        <div style={detailItemStyle}>
          <DollarSign size={15} style={iconStyle} />
          <div>
            <span style={labelStyle}>Total Amount</span>
            <span style={amountValueStyle}>₹{parseFloat(order.total_amount).toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Nested Order Item List */}
      {order.order_items && order.order_items.length > 0 && (
        <div style={itemsListStyle}>
          <h4 style={itemsTitleStyle}>Items Secured</h4>
          {order.order_items.map((item, idx) => (
            <div key={idx} style={itemRowStyle}>
              <div style={itemDetailsStyle}>
                <span style={itemNameStyle}>{item.product?.name || `Secured Release (Product #${item.product_id})`}</span>
                <span style={itemQtyStyle}>
                  Qty: {item.quantity} 
                  {item.size && <span style={sizeBadgeStyle}>| Size: {item.size}</span>}
                </span>
              </div>
              <span style={itemPriceStyle}>₹{parseFloat(item.subtotal).toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}

      {/* Action Buttons Footer */}
      {isPending && timeLeft !== "EXPIRED" && (
        <div style={actionsFooterStyle}>
          <div style={timerBoxStyle}>
            <AlertCircle size={14} style={{ color: "var(--warning)" }} />
            <span>Reservation expires in: <strong style={{ color: "var(--accent-red)" }}>{timeLeft}</strong></span>
          </div>
          
          <div style={btnRowStyle}>
            <button
              onClick={() => onCancel(order.order_id)}
              disabled={isCancelling || isPaying}
              className="btn btn-outline"
              style={btnCancelStyle}
            >
              {isCancelling ? "CANCELING..." : "FORFEIT RELEASE"}
            </button>
            <button
              onClick={() => onPay(order.order_id)}
              disabled={isPaying || isCancelling}
              className="btn btn-accent"
              style={btnPayStyle}
            >
              {isPaying ? "PROCESSING..." : "PAY & SECURE PAIR"}
            </button>
          </div>
        </div>
      )}

      {isPending && timeLeft === "EXPIRED" && (
        <div style={expiredBannerStyle}>
          <XCircle size={16} />
          <span>This payment reservation has expired. The stock has been released.</span>
        </div>
      )}
    </div>
  );
}

// OrderCard Styling Specifications
const cardContainerStyle = {
  border: "1px solid var(--border-color)",
  boxShadow: "var(--shadow-sm)",
  display: "flex",
  flexDirection: "column",
  gap: "24px",
  padding: "24px",
};

const headerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "16px",
};

const orderIdLabelStyle = {
  fontSize: "10px",
  fontWeight: "800",
  textTransform: "uppercase",
  color: "var(--text-muted)",
  letterSpacing: "0.08em",
};

const orderIdStyle = {
  fontSize: "18px",
  fontWeight: "900",
  color: "var(--text-primary)",
  marginTop: "4px",
};

const badgeStyle = {
  display: "inline-flex",
  alignItems: "center",
  gap: "6px",
  padding: "6px 12px",
};

const detailsGridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "18px",
};

const detailItemStyle = {
  display: "flex",
  gap: "12px",
  alignItems: "flex-start",
};

const iconStyle = {
  marginTop: "3px",
  color: "var(--text-muted)",
};

const labelStyle = {
  display: "block",
  fontSize: "11px",
  fontWeight: "800",
  textTransform: "uppercase",
  color: "var(--text-muted)",
  letterSpacing: "0.05em",
  marginBottom: "2px",
};

const valueStyle = {
  fontSize: "14px",
  fontWeight: "500",
  color: "var(--text-primary)",
};

const amountValueStyle = {
  fontSize: "15px",
  fontWeight: "800",
  color: "var(--text-primary)",
  fontFamily: "var(--font-display)",
};

const itemsListStyle = {
  backgroundColor: "var(--bg-secondary)",
  padding: "16px",
  borderRadius: "var(--border-radius-sm)",
};

const itemsTitleStyle = {
  fontSize: "11px",
  fontWeight: "800",
  color: "var(--text-primary)",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  marginBottom: "12px",
  borderBottom: "1px solid #e0e0e0",
  paddingBottom: "6px",
};

const itemRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "6px 0",
  fontSize: "13px",
};

const itemDetailsStyle = {
  display: "flex",
  flexDirection: "column",
};

const itemNameStyle = {
  fontWeight: "700",
  color: "var(--text-primary)",
};

const itemQtyStyle = {
  fontSize: "11px",
  color: "var(--text-muted)",
  marginTop: "2px",
  display: "flex",
  alignItems: "center",
  gap: "4px"
};

const sizeBadgeStyle = {
  fontWeight: "700",
  color: "var(--text-primary)",
};

const itemPriceStyle = {
  fontWeight: "800",
  fontFamily: "var(--font-display)",
};

const actionsFooterStyle = {
  borderTop: "1px solid var(--border-color)",
  paddingTop: "18px",
  display: "flex",
  flexDirection: "column",
  gap: "14px",
};

const timerBoxStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  fontSize: "13px",
  color: "var(--text-muted)",
};

const btnRowStyle = {
  display: "flex",
  gap: "12px",
  flexWrap: "wrap",
};

const btnCancelStyle = {
  padding: "10px 18px",
  fontSize: "11px",
  flex: 1,
  minWidth: "140px",
};

const btnPayStyle = {
  padding: "10px 18px",
  fontSize: "11px",
  flex: 1.2,
  minWidth: "160px",
};

const expiredBannerStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  color: "var(--error)",
  backgroundColor: "rgba(227, 6, 19, 0.05)",
  border: "1px solid rgba(227, 6, 19, 0.15)",
  padding: "12px 16px",
  borderRadius: "var(--border-radius-sm)",
  fontSize: "13px",
};