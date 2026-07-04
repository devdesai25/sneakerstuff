/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import OrderCard from "../components/OrderCard";
import { OrderCardSkeleton } from "../components/common/Skeleton";
import api from "../services/api";
import { ClipboardList, ShoppingBag } from "lucide-react";

export default function Orders() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const { isLoggedIn } = useContext(AuthContext);

  // Fetch products query so OrderCard can resolve sneaker names & images
  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await api.get("/products");
      return res.data;
    }
  });

  // Fetch orders query
  const {
    data: orders = [],
    isLoading,
    isError,
    error
  } = useQuery({
    queryKey: ["orders"],
    queryFn: async () => {
      const res = await api.get("/orders");
      return res.data;
    },
    enabled: isLoggedIn,
    retry: (failureCount, error) => {
      // Don't retry if it is a 404 (which means "no orders" in this backend)
      if (error.response?.status === 404) return false;
      return failureCount < 2;
    }
  });

  // Payment mutation
  const payMutation = useMutation({
    mutationFn: async (orderId) => {
      const res = await api.patch(`/orders/${orderId}/pay`);
      return res.data;
    },
    onSuccess: (data) => {
      toast.success(`Payment successful for Order #${data.order_id}!`);
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      // Invalidate products because product stock decreases/restores
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Payment failed. Try again.");
    }
  });

  // Cancel mutation
  const cancelMutation = useMutation({
    mutationFn: async (orderId) => {
      const res = await api.patch(`/orders/${orderId}/cancel`);
      return res.data;
    },
    onSuccess: (data) => {
      toast.success(`Order #${data.order_id} has been canceled.`);
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to cancel order.");
    }
  });

  if (!isLoggedIn) {
    return (
      <div className="container" style={centerPanelStyle}>
        <ClipboardList size={48} style={{ color: "var(--text-muted)", marginBottom: "16px" }} />
        <h3>YOUR ORDERS ARE PRIVATE</h3>
        <p style={{ color: "var(--text-muted)", margin: "12px 0 24px 0" }}>Please login to view your order history.</p>
        <Link to="/login" className="btn btn-primary">LOG IN</Link>
      </div>
    );
  }

  // Handle backend's 404 "Orders not found" response as a clean empty state
  const isNoOrders = isError && error.response?.status === 404;

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: "64px", maxWidth: "800px" }}>
      <h1 style={pageTitleStyle}>MY ORDERS</h1>

      {isLoading ? (
        <div>
          <OrderCardSkeleton />
          <OrderCardSkeleton />
        </div>
      ) : isNoOrders || orders.length === 0 ? (
        <div className="premium-panel" style={centerPanelStyle}>
          <ShoppingBag size={40} style={{ color: "var(--text-muted)", marginBottom: "16px" }} />
          <h3>YOU HAVE NO ORDERS</h3>
          <p style={{ color: "var(--text-muted)", margin: "8px 0 24px 0" }}>
            You haven't placed any sneaker orders yet. Shop our catalog to cop some grails!
          </p>
          <Link to="/" className="btn btn-primary">GO SHOPPING</Link>
        </div>
      ) : isError ? (
        <div style={errorContainerStyle}>
          <h3 style={{ color: "var(--error)", marginBottom: "12px" }}>FAILED TO LOAD ORDERS</h3>
          <p style={{ color: "var(--text-muted)", marginBottom: "24px" }}>
            {error.response?.data?.detail || "Could not retrieve order details from server."}
          </p>
          <button className="btn btn-outline" onClick={() => queryClient.invalidateQueries({ queryKey: ["orders"] })}>
            TRY AGAIN
          </button>
        </div>
      ) : (
        <div>
          {orders.map((order) => (
            <OrderCard
              key={order.order_id}
              order={order}
              products={products}
              onPay={(id) => payMutation.mutate(id)}
              onCancel={(id) => cancelMutation.mutate(id)}
              isPaying={payMutation.isPending}
              isCancelling={cancelMutation.isPending}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Styles
const pageTitleStyle = {
  fontSize: "36px",
  margin: "32px 0 24px 0",
};

const centerPanelStyle = {
  textAlign: "center",
  padding: "64px 24px",
};

const errorContainerStyle = {
  textAlign: "center",
  padding: "48px 24px",
  backgroundColor: "var(--bg-card)",
  border: "1px solid var(--border-color)",
  borderRadius: "var(--border-radius-md)",
};