/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import api from "../services/api";
import { ShieldCheck, Plus, Trash2, Edit3, Calendar, Eye, Ban, Send, RefreshCw } from "lucide-react";

export default function Admin() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const { user } = useContext(AuthContext);

  // Active sub-sections tabs: "products" or "drops"
  const [activeTab, setActiveTab] = useState("products");

  // Form States - Product Create/Update
  const [productForm, setProductForm] = useState({
    id: "",
    name: "",
    price: "",
    description: "",
    stock: "",
    images: "",
  });

  // Form States - Drop Create
  const [dropForm, setDropForm] = useState({
    product_id: "",
    opens_at: "",
    closes_at: "",
    drop_inventory: "",
  });

  // Queries
  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await api.get("/products");
      return res.data;
    },
  });

  const { data: drops = [] } = useQuery({
    queryKey: ["adminDrops"],
    queryFn: async () => {
      const res = await api.get("/admin/drop");
      return res.data;
    },
    enabled: user?.role === "admin",
  });

  // Product Mutations
  const createProductMutation = useMutation({
    mutationFn: async (payload) => {
      return await api.post("/admin/create", payload);
    },
    onSuccess: () => {
      toast.success("Product created successfully!");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      resetProductForm();
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to create product.");
    },
  });

  const updateProductMutation = useMutation({
    mutationFn: async ({ id, payload }) => {
      return await api.patch(`/admin/update/${id}`, payload);
    },
    onSuccess: () => {
      toast.success("Product updated successfully!");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      resetProductForm();
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update product.");
    },
  });

  const deleteProductMutation = useMutation({
    mutationFn: async (id) => {
      return await api.delete(`/admin/delete/${id}`);
    },
    onSuccess: () => {
      toast.success("Product deleted successfully.");
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to delete product.");
    },
  });

  // Drop Mutations
  const createDropMutation = useMutation({
    mutationFn: async (payload) => {
      return await api.post("/admin/drop", payload);
    },
    onSuccess: () => {
      toast.success("Drop scheduled successfully!");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
      setDropForm({ product_id: "", opens_at: "", closes_at: "", drop_inventory: "" });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to schedule drop.");
    },
  });

  const publishDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.post(`/admin/drop/${id}/publish`);
    },
    onSuccess: () => {
      toast.success("Drop published to scheduled queues!");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to publish drop.");
    },
  });

  const cancelDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.post(`/admin/drop/${id}/cancel`);
    },
    onSuccess: () => {
      toast.success("Drop drawing canceled.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to cancel drop.");
    },
  });

  const deleteDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.delete(`/admin/drop/${id}/delete`);
    },
    onSuccess: () => {
      toast.success("Drop deleted.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to delete drop.");
    },
  });

  const resetProductForm = () => {
    setProductForm({ id: "", name: "", price: "", description: "", stock: "", images: "" });
  };

  const handleProductSubmit = (e) => {
    e.preventDefault();
    const payload = {
      name: productForm.name,
      price: parseFloat(productForm.price),
      description: productForm.description,
      stock: parseInt(productForm.stock, 10),
      images: productForm.images || "",
    };

    if (productForm.id) {
      updateProductMutation.mutate({ id: productForm.id, payload });
    } else {
      createProductMutation.mutate(payload);
    }
  };

  const handleDropSubmit = (e) => {
    e.preventDefault();
    // Convert to ISO-8601 strings expected by Pydantic datetime fields
    const payload = {
      product_id: parseInt(dropForm.product_id, 10),
      opens_at: new Date(dropForm.opens_at).toISOString(),
      closes_at: new Date(dropForm.closes_at).toISOString(),
      drop_inventory: parseInt(dropForm.drop_inventory, 10),
    };
    createDropMutation.mutate(payload);
  };

  const fillProductForm = (prod) => {
    setProductForm({
      id: prod.product_id,
      name: prod.name,
      price: prod.price.toString(),
      description: prod.description || "",
      stock: prod.stock.toString(),
      images: prod.images || "",
    });
  };

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: "64px" }}>
      <div style={headerStyle}>
        <ShieldCheck size={28} style={{ color: "var(--accent-neon-green)" }} />
        <div>
          <h1 style={{ fontSize: "28px" }}>ADMIN CONTROL CENTRE</h1>
          <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>Manage sneakers catalog and launch draws</span>
        </div>
      </div>

      {/* Tabs Menu */}
      <div style={tabsContainerStyle}>
        <button
          onClick={() => setActiveTab("products")}
          style={activeTab === "products" ? activeTabStyle : tabStyle}
        >
          Catalog CRUD
        </button>
        <button
          onClick={() => setActiveTab("drops")}
          style={activeTab === "drops" ? activeTabStyle : tabStyle}
        >
          Drops Orchestration
        </button>
      </div>

      {/* Tab Panel: Products */}
      {activeTab === "products" && (
        <div style={panelGridStyle}>
          {/* Create/Update form */}
          <div className="premium-panel" style={formCardStyle}>
            <h3 style={formTitleStyle}>
              {productForm.id ? "UPDATE PRODUCT" : "REGISTER PRODUCT"}
            </h3>

            <form onSubmit={handleProductSubmit}>
              <div className="form-group">
                <label className="form-label">Sneaker Name</label>
                <input
                  type="text"
                  className="input-field"
                  value={productForm.name}
                  onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                  placeholder="e.g. Jordan 1 Retro High OG"
                  required
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="form-group">
                  <label className="form-label">Price (INR)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={productForm.price}
                    onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                    placeholder="15999"
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Stock Qty</label>
                  <input
                    type="number"
                    className="input-field"
                    value={productForm.stock}
                    onChange={(e) => setProductForm({ ...productForm, stock: e.target.value })}
                    placeholder="25"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Image URL</label>
                <input
                  type="url"
                  className="input-field"
                  value={productForm.images}
                  onChange={(e) => setProductForm({ ...productForm, images: e.target.value })}
                  placeholder="https://..."
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="input-field"
                  value={productForm.description}
                  onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
                  placeholder="Details, materials, sizing..."
                  rows={4}
                  style={{ resize: "none" }}
                  required
                />
              </div>

              <div style={{ display: "flex", gap: "12px", marginTop: "12px" }}>
                <button type="submit" className="btn btn-primary" style={{ flexGrow: 1 }}>
                  {productForm.id ? "SAVE SNEAKER" : "CREATE SNEAKER"}
                </button>
                {productForm.id && (
                  <button type="button" className="btn btn-outline" onClick={resetProductForm}>
                    RESET
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* List panel */}
          <div className="premium-panel" style={listCardStyle}>
            <h3 style={listTitleStyle}>PRODUCT LIST</h3>
            <div style={listScrollStyle}>
              {products.map((prod) => (
                <div key={prod.product_id} style={listItemStyle}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <img 
                      src={prod.images?.split(",")[0] || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=100&auto=format&fit=crop"} 
                      alt={prod.name} 
                      style={listImgStyle} 
                    />
                    <div>
                      <h4 style={{ fontSize: "14px" }}>{prod.name}</h4>
                      <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                        ID #{prod.product_id} &bull; stock: {prod.stock} &bull; ${Number(prod.price).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "8px" }}>
                    <button onClick={() => fillProductForm(prod)} style={iconBtnStyle} title="Edit Product">
                      <Edit3 size={14} />
                    </button>
                    <button 
                      onClick={() => deleteProductMutation.mutate(prod.product_id)} 
                      style={{ ...iconBtnStyle, color: "var(--error)" }}
                      title="Delete Product"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab Panel: Drops */}
      {activeTab === "drops" && (
        <div style={panelGridStyle}>
          {/* Create Drop Form */}
          <div className="premium-panel" style={formCardStyle}>
            <h3 style={formTitleStyle}>SCHEDULE DROP DRAW</h3>

            <form onSubmit={handleDropSubmit}>
              <div className="form-group">
                <label className="form-label">Target Product ID</label>
                <select
                  className="input-field"
                  value={dropForm.product_id}
                  onChange={(e) => setDropForm({ ...dropForm, product_id: e.target.value })}
                  style={{ backgroundColor: "var(--bg-input)" }}
                  required
                >
                  <option value="">-- Choose a sneaker --</option>
                  {products.map((prod) => (
                    <option key={prod.product_id} value={prod.product_id}>
                      {prod.name} (stock: {prod.stock})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Drop Allocation Size</label>
                <input
                  type="number"
                  className="input-field"
                  value={dropForm.drop_inventory}
                  onChange={(e) => setDropForm({ ...dropForm, drop_inventory: e.target.value })}
                  placeholder="Pairs allocated to raffle"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Opens At</label>
                <input
                  type="datetime-local"
                  className="input-field"
                  value={dropForm.opens_at}
                  onChange={(e) => setDropForm({ ...dropForm, opens_at: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Closes At</label>
                <input
                  type="datetime-local"
                  className="input-field"
                  value={dropForm.closes_at}
                  onChange={(e) => setDropForm({ ...dropForm, closes_at: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className="btn btn-accent" style={{ width: "100%", marginTop: "12px" }}>
                SCHEDULE RAFFLE DRAW
              </button>
            </form>
          </div>

          {/* Drops List */}
          <div className="premium-panel" style={listCardStyle}>
            <h3 style={listTitleStyle}>ORCHESTRATED DROPS</h3>
            <div style={listScrollStyle}>
              {drops.map((drop) => (
                <div key={drop.drop_id} style={listItemStyle}>
                  <div>
                    <h4 style={{ fontSize: "14px" }}>
                      Drop #{drop.drop_id} &bull; {drop.product_name || `Product ID #${drop.product_id}`}
                    </h4>
                    <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px", display: "flex", flexDirection: "column", gap: "2px" }}>
                      <span>Status: <strong style={{ color: "var(--text-primary)" }}>{drop.status}</strong></span>
                      <span>Inventory: {drop.drop_inventory} pairs</span>
                      <span>Opens: {new Date(drop.opens_at).toLocaleString()}</span>
                      <span>Closes: {new Date(drop.closes_at).toLocaleString()}</span>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "flex-end", maxWidth: "160px" }}>
                    {drop.status === "DRAFT" && (
                      <>
                        <button
                          onClick={() => publishDropMutation.mutate(drop.drop_id)}
                          className="btn btn-primary"
                          style={actionBtnTinyStyle}
                          title="Publish & Schedule Tasks"
                        >
                          <Send size={11} /> Publish
                        </button>
                        <button
                          onClick={() => deleteDropMutation.mutate(drop.drop_id)}
                          className="btn btn-danger"
                          style={actionBtnTinyStyle}
                          title="Delete Draft"
                        >
                          <Trash2 size={11} /> Delete
                        </button>
                      </>
                    )}
                    {drop.status === "SCHEDULED" && (
                      <button
                        onClick={() => cancelDropMutation.mutate(drop.drop_id)}
                        className="btn btn-danger"
                        style={actionBtnTinyStyle}
                        title="Cancel Drop"
                      >
                        <Ban size={11} /> Cancel
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Styles
const headerStyle = {
  display: "flex",
  alignItems: "center",
  gap: "16px",
  margin: "32px 0 40px 0",
};

const tabsContainerStyle = {
  display: "flex",
  borderBottom: "1px solid var(--border-color)",
  marginBottom: "32px",
  gap: "16px",
};

const tabStyle = {
  padding: "12px 24px",
  background: "transparent",
  border: "none",
  borderBottom: "2px solid transparent",
  color: "var(--text-muted)",
  fontFamily: "var(--font-display)",
  fontWeight: "700",
  fontSize: "15px",
  textTransform: "uppercase",
  cursor: "pointer",
  transition: "all var(--transition-fast)",
};

const activeTabStyle = {
  ...tabStyle,
  color: "var(--accent-neon-green)",
  borderBottomColor: "var(--accent-neon-green)",
};

const panelGridStyle = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: "32px",
};

if (typeof window !== "undefined" && window.innerWidth >= 1024) {
  panelGridStyle.gridTemplateColumns = "1fr 1.2fr";
}

const formCardStyle = {
  padding: "32px",
  height: "fit-content",
};

const formTitleStyle = {
  fontSize: "20px",
  marginBottom: "24px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "12px",
};

const listCardStyle = {
  padding: "32px",
  display: "flex",
  flexDirection: "column",
};

const listTitleStyle = {
  fontSize: "20px",
  marginBottom: "24px",
  borderBottom: "1px solid var(--border-color)",
  paddingBottom: "12px",
};

const listScrollStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  maxHeight: "600px",
  overflowY: "auto",
  paddingRight: "8px",
};

const listItemStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "12px",
  backgroundColor: "var(--bg-input)",
  border: "1px solid var(--border-color)",
  borderRadius: "8px",
  gap: "16px",
};

const listImgStyle = {
  width: "48px",
  height: "48px",
  objectFit: "cover",
  borderRadius: "6px",
  backgroundColor: "rgba(255, 255, 255, 0.02)",
};

const iconBtnStyle = {
  padding: "8px",
  background: "transparent",
  border: "none",
  color: "var(--text-muted)",
  cursor: "pointer",
  borderRadius: "4px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  transition: "all var(--transition-fast)",
  backgroundColor: "rgba(255,255,255,0.02)",
};

const actionBtnTinyStyle = {
  padding: "6px 12px",
  fontSize: "11px",
  borderRadius: "6px",
  gap: "4px",
};