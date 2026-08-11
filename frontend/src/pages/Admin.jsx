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
import { ShieldCheck, Plus, Trash2, Edit3, Calendar, Eye, EyeOff, Ban, Send, RefreshCw, CheckCircle2, AlertCircle, Check, Pause, Play, Flame } from "lucide-react";

export default function Admin() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const { user } = useContext(AuthContext);

  // Active sub-sections tabs: "products" or "drops"
  const [activeTab, setActiveTab] = useState("products");
  
  const STANDARD_SIZES = ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 11.5", "US 12"];

  const [sizes, setSizes] = useState(
    STANDARD_SIZES.map(s => ({ size: s, stock: 0 }))
  );
  
  const totalStock = sizes.reduce((acc, curr) => acc + (parseInt(curr.stock) || 0), 0);

  // Form States - Product Create/Update
  const [productForm, setProductForm] = useState({
    id: "",
    name: "",
    price: "",
    description: "",
    stock: "",
    images: "",
    is_reserved_for_drop: false,
    is_visible: true,
  });

  // Form States - Drop Create
  const [dropForm, setDropForm] = useState({
    product_id: "",
    opens_at: "",
    closes_at: "",
    drop_inventory: "",
  });
  const [dropSizes, setDropSizes] = useState([]);

  // Queries
  const { data: products = [] } = useQuery({
    queryKey: ["adminProducts"],
    queryFn: async () => {
      const res = await api.get("/products?include_hidden=true");
      return res.data;
    },
    enabled: user?.role === "admin",
  });

  const { data: drops = [] } = useQuery({
    queryKey: ["adminDrops"],
    queryFn: async () => {
      const res = await api.get("/admin/drop");
      return res.data;
    },
    enabled: user?.role === "admin",
  });

  // Search and filter states
  const [productSearch, setProductSearch] = useState("");
  const [productFilter, setProductFilter] = useState("");
  const [dropFilter, setDropFilter] = useState("");

  const filteredProducts = products.filter((prod) =>
    prod.name.toLowerCase().includes(productSearch.toLowerCase())
  );

  const filteredAdminProducts = products.filter((prod) =>
    prod.name.toLowerCase().includes(productFilter.toLowerCase())
  );

  const filteredAdminDrops = drops.filter((drop) => {
    const term = dropFilter.toLowerCase();
    return (
      drop.drop_id.toString().includes(term) ||
      (drop.product_name || "").toLowerCase().includes(term) ||
      drop.status.toLowerCase().includes(term)
    );
  });

  // Product Mutations
  const createProductMutation = useMutation({
    mutationFn: async (payload) => {
      return await api.post("/admin/create", payload);
    },
    onSuccess: () => {
      toast.success("Product created successfully!");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
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
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
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
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to delete product.");
    },
  });

  const toggleProductVisibilityMutation = useMutation({
    mutationFn: async (id) => {
      return await api.patch(`/admin/products/${id}/toggle-visibility`);
    },
    onSuccess: () => {
      toast.success("Product visibility updated.");
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update product visibility.");
    },
  });

  const toggleProductReservedMutation = useMutation({
    mutationFn: async (id) => {
      return await api.patch(`/admin/products/${id}/toggle-reserved`);
    },
    onSuccess: () => {
      toast.success("Product drop reservation updated.");
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update drop reservation.");
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
      setDropForm({ id: "", product_id: "", opens_at: "", closes_at: "", drop_inventory: "" });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to schedule drop.");
    },
  });

  const updateDropMutation = useMutation({
    mutationFn: async ({ id, payload }) => {
      return await api.patch(`/admin/drop/${id}`, payload);
    },
    onSuccess: () => {
      toast.success("Drop updated successfully!");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
      setDropForm({ id: "", product_id: "", opens_at: "", closes_at: "", drop_inventory: "" });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update drop.");
    },
  });

  const publishDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.patch(`/admin/drop/${id}/publish`);
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
      return await api.patch(`/admin/drop/${id}/cancel`);
    },
    onSuccess: () => {
      toast.success("Drop drawing canceled.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to cancel drop.");
    },
  });

  const toggleVisibilityMutation = useMutation({
    mutationFn: async (id) => {
      return await api.patch(`/admin/drop/${id}/toggle-visibility`);
    },
    onSuccess: () => {
      toast.success("Visibility updated.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update visibility.");
    },
  });

  const pauseDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.patch(`/admin/drop/${id}/pause`);
    },
    onSuccess: () => {
      toast.success("Drop paused.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to pause drop.");
    },
  });

  const resumeDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.patch(`/admin/drop/${id}/resume`);
    },
    onSuccess: () => {
      toast.success("Drop resumed.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to resume drop.");
    },
  });

  const drawDropMutation = useMutation({
    mutationFn: async (id) => {
      return await api.post(`/admin/drop/${id}/draw`);
    },
    onSuccess: () => {
      toast.success("Raffle draw executed! Winners selected.");
      queryClient.invalidateQueries({ queryKey: ["adminDrops"] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to execute raffle draw.");
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
    setProductForm({ id: "", name: "", price: "", description: "", stock: "", images: "", is_reserved_for_drop: false, is_visible: true });
    setSizes(STANDARD_SIZES.map(s => ({ size: s, stock: 0 })));
  };

  const handleProductSubmit = (e) => {
    e.preventDefault();
    const payload = {
      name: productForm.name,
      price: parseFloat(productForm.price),
      description: productForm.description,
      stock: totalStock,
      sizes: sizes,
      images: productForm.images || "",
      is_reserved_for_drop: productForm.is_reserved_for_drop,
      is_visible: productForm.is_visible,
    };

    if (productForm.id) {
      updateProductMutation.mutate({ id: productForm.id, payload });
    } else {
      createProductMutation.mutate(payload);
    }
  };

  const handleDropProductSelect = (productIdStr) => {
    const pId = parseInt(productIdStr, 10);
    const selectedProd = products.find((p) => p.product_id === pId);

    if (selectedProd) {
      let initialDropSizes = [];
      if (selectedProd.sizes && Array.isArray(selectedProd.sizes) && selectedProd.sizes.length > 0) {
        initialDropSizes = STANDARD_SIZES.map((sName) => {
          const found = selectedProd.sizes.find((ps) => ps.size === sName);
          const maxStock = found ? found.stock : 0;
          return { size: sName, stock: maxStock, maxStock };
        });
      } else {
        initialDropSizes = STANDARD_SIZES.map((sName) => ({
          size: sName,
          stock: 0,
          maxStock: 0,
        }));
      }

      let totalCalculatedStock = initialDropSizes.reduce(
        (acc, curr) => acc + (parseInt(curr.stock) || 0),
        0
      );

      // If sum of size stock exceeds available product stock (due to reserved drops/orders), cap size quantities proportionally or down to total product stock
      if (totalCalculatedStock > selectedProd.stock && selectedProd.stock >= 0) {
        let diff = totalCalculatedStock - selectedProd.stock;
        // Trim difference starting from largest size stocks
        for (let i = initialDropSizes.length - 1; i >= 0 && diff > 0; i--) {
          if (initialDropSizes[i].stock > 0) {
            const reduceBy = Math.min(initialDropSizes[i].stock, diff);
            initialDropSizes[i].stock -= reduceBy;
            diff -= reduceBy;
          }
        }
        totalCalculatedStock = selectedProd.stock;
        toast.info(
          `Shoe sizes auto-filled for "${selectedProd.name}". Unreserved stock available: ${selectedProd.stock} pairs (${totalCalculatedStock} pairs allocated).`
        );
      } else {
        toast.info(`Shoe sizes auto-filled for "${selectedProd.name}". Total available stock: ${selectedProd.stock} pairs.`);
      }

      setDropSizes(initialDropSizes);
      setDropForm((prev) => ({
        ...prev,
        product_id: productIdStr,
        drop_inventory: totalCalculatedStock.toString(),
      }));
    } else {
      setDropSizes([]);
      setDropForm((prev) => ({
        ...prev,
        product_id: productIdStr,
        drop_inventory: "",
      }));
    }
  };

  const handleDropSizeChange = (idx, newStockVal) => {
    const val = parseInt(newStockVal, 10) || 0;
    const updated = [...dropSizes];
    const targetSize = updated[idx];

    if (val > targetSize.maxStock) {
      toast.error(
        `Not sufficient stock for ${targetSize.size}! Maximum available stock is ${targetSize.maxStock}.`
      );
    } else if (val < 0) {
      toast.error(`Quantity for ${targetSize.size} cannot be negative.`);
    }

    updated[idx] = { ...targetSize, stock: val };
    setDropSizes(updated);

    const newTotal = updated.reduce((acc, curr) => acc + (parseInt(curr.stock) || 0), 0);
    setDropForm((prev) => ({
      ...prev,
      drop_inventory: newTotal.toString(),
    }));
  };

  const handleDropSubmit = (e) => {
    e.preventDefault();

    if (!dropForm.product_id) {
      toast.error("Please select a target product for the drop.");
      return;
    }

    const selectedProd = products.find((p) => p.product_id === parseInt(dropForm.product_id, 10));

    // Check size-level stock limits
    const invalidSizes = dropSizes.filter((s) => s.stock > s.maxStock || s.stock < 0);
    if (invalidSizes.length > 0) {
      const names = invalidSizes.map((s) => `${s.size} (Available: ${s.maxStock}, Given: ${s.stock})`).join(", ");
      toast.error(`Cannot schedule drop: Not sufficient stock for size(s): ${names}`);
      return;
    }

    const requestedInventory = parseInt(dropForm.drop_inventory, 10) || 0;
    if (selectedProd && requestedInventory > selectedProd.stock) {
      toast.error(`Cannot schedule drop: Total drop allocation (${requestedInventory}) exceeds product stock (${selectedProd.stock}).`);
      return;
    }

    if (requestedInventory <= 0) {
      toast.error("Drop allocation size must be greater than zero.");
      return;
    }

    const payload = {
      product_id: parseInt(dropForm.product_id, 10),
      opens_at: new Date(dropForm.opens_at).toISOString(),
      closes_at: new Date(dropForm.closes_at).toISOString(),
      drop_inventory: requestedInventory,
    };

    if (dropForm.id) {
      updateDropMutation.mutate({ id: dropForm.id, payload });
    } else {
      createDropMutation.mutate(payload);
    }
  };

  const fillDropForm = (drop) => {
    setDropForm({
      id: drop.drop_id,
      product_id: drop.product_id.toString(),
      opens_at: drop.opens_at ? drop.opens_at.slice(0, 16) : "",
      closes_at: drop.closes_at ? drop.closes_at.slice(0, 16) : "",
      drop_inventory: drop.drop_inventory.toString(),
    });

    const selectedProd = products.find((p) => p.product_id === drop.product_id);
    if (selectedProd) {
      if (selectedProd.sizes && Array.isArray(selectedProd.sizes) && selectedProd.sizes.length > 0) {
        setDropSizes(
          STANDARD_SIZES.map((sName) => {
            const found = selectedProd.sizes.find((ps) => ps.size === sName);
            const maxStock = found ? found.stock : 0;
            return { size: sName, stock: maxStock, maxStock };
          })
        );
      } else {
        setDropSizes(STANDARD_SIZES.map((sName) => ({ size: sName, stock: 0, maxStock: 0 })));
      }
    }
  };

  const fillProductForm = (prod) => {
    setProductForm({
      id: prod.product_id,
      name: prod.name,
      price: prod.price.toString(),
      description: prod.description || "",
      stock: prod.stock.toString(),
      images: prod.images || "",
      is_reserved_for_drop: prod.is_reserved_for_drop || false,
      is_visible: prod.is_visible !== undefined ? prod.is_visible : true,
    });

    if (prod.sizes && Array.isArray(prod.sizes) && prod.sizes.length > 0) {
      setSizes(STANDARD_SIZES.map(s => {
        const found = prod.sizes.find(ps => ps.size === s);
        return { size: s, stock: found ? found.stock : 0 };
      }));
    } else {
      setSizes(STANDARD_SIZES.map(s => ({ size: s, stock: 0 })));
    }
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
                  <label className="form-label">Total Stock</label>
                  <input
                    type="number"
                    className="input-field"
                    value={totalStock}
                    disabled
                    style={{ backgroundColor: "var(--bg-secondary)", cursor: "not-allowed" }}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Size Inventory (Pairs)</label>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "16px" }}>
                  {sizes.map((sObj, idx) => (
                    <div key={sObj.size} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ fontSize: "12px", width: "50px", color: "var(--text-muted)", fontWeight: "600" }}>{sObj.size}</span>
                      <input
                        type="number"
                        className="input-field"
                        style={{ padding: "6px", height: "30px", fontSize: "12px" }}
                        min="0"
                        value={sObj.stock}
                        onChange={(e) => {
                          const newSizes = [...sizes];
                          newSizes[idx].stock = parseInt(e.target.value) || 0;
                          setSizes(newSizes);
                        }}
                      />
                    </div>
                  ))}
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

              {/* Product Visibility & Drop Reservation Switches */}
              <div style={{ display: "flex", gap: "20px", flexWrap: "wrap", margin: "16px 0", padding: "12px", backgroundColor: "var(--bg-secondary)", borderRadius: "6px", border: "1px solid var(--border-color)" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer", fontSize: "12px", fontWeight: "700" }}>
                  <input
                    type="checkbox"
                    checked={productForm.is_reserved_for_drop}
                    onChange={(e) => setProductForm({ ...productForm, is_reserved_for_drop: e.target.checked })}
                    style={{ width: "16px", height: "16px", accentColor: "var(--accent-red)" }}
                  />
                  <Flame size={15} style={{ color: "var(--accent-red)" }} />
                  Reserved for Drop (Preview only)
                </label>

                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer", fontSize: "12px", fontWeight: "700" }}>
                  <input
                    type="checkbox"
                    checked={productForm.is_visible}
                    onChange={(e) => setProductForm({ ...productForm, is_visible: e.target.checked })}
                    style={{ width: "16px", height: "16px", accentColor: "var(--accent-neon-green)" }}
                  />
                  <Eye size={15} style={{ color: "var(--accent-neon-green)" }} />
                  Visible in Catalog
                </label>
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
            <input
              type="text"
              className="input-field"
              placeholder="Search products by name..."
              value={productFilter}
              onChange={(e) => setProductFilter(e.target.value)}
              style={{ marginBottom: "16px", fontSize: "12px", height: "36px" }}
            />
            <div style={listScrollStyle}>
              {filteredAdminProducts.map((prod) => (
                <div key={prod.product_id} style={listItemStyle}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <img 
                      src={prod.images?.split(",")[0] || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=100&auto=format&fit=crop"} 
                      alt={prod.name} 
                      style={listImgStyle} 
                    />
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <h4 style={{ fontSize: "14px", margin: 0 }}>{prod.name}</h4>
                        {prod.is_reserved_for_drop && (
                          <span className="badge" style={{ backgroundColor: "#E30613", color: "#FFF", fontSize: "9px", padding: "2px 6px", display: "inline-flex", alignItems: "center", gap: "2px" }}>
                            <Flame size={10} fill="#FFF" /> RESERVED
                          </span>
                        )}
                        {!prod.is_visible && (
                          <span className="badge badge-warning" style={{ fontSize: "9px", padding: "2px 6px" }}>
                            HIDDEN
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                        ID #{prod.product_id} &bull; stock: {prod.stock} &bull; ₹{Number(prod.price).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "8px" }}>
                    <button 
                      onClick={() => toggleProductReservedMutation.mutate(prod.product_id)} 
                      style={{ ...iconBtnStyle, color: prod.is_reserved_for_drop ? "var(--accent-red)" : "var(--text-muted)" }}
                      title={prod.is_reserved_for_drop ? "Purchasing Disabled (Click to make purchasable)" : "Purchasable (Click to reserve for drop)"}
                    >
                      <Flame size={14} fill={prod.is_reserved_for_drop ? "var(--accent-red)" : "none"} />
                    </button>
                    <button 
                      onClick={() => toggleProductVisibilityMutation.mutate(prod.product_id)} 
                      style={{ ...iconBtnStyle, color: prod.is_visible ? "var(--accent-neon-green)" : "var(--text-muted)" }}
                      title={prod.is_visible ? "Visible in catalog (Click to hide)" : "Hidden from catalog (Click to show)"}
                    >
                      {prod.is_visible ? <Eye size={14} /> : <EyeOff size={14} />}
                    </button>
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
            <h3 style={formTitleStyle}>
              {dropForm.id ? "UPDATE DROP DRAW" : "SCHEDULE DROP DRAW"}
            </h3>

            <form onSubmit={handleDropSubmit}>
              <div className="form-group">
                <label className="form-label">Target Product ID</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Filter dropdown list by name..."
                  value={productSearch}
                  onChange={(e) => setProductSearch(e.target.value)}
                  style={{ marginBottom: "8px", fontSize: "12px", height: "36px" }}
                />
                <select
                  className="input-field"
                  value={dropForm.product_id}
                  onChange={(e) => handleDropProductSelect(e.target.value)}
                  style={{ backgroundColor: "var(--bg-input)" }}
                  required
                >
                  <option value="">-- Choose a sneaker --</option>
                  {filteredProducts.map((prod) => (
                    <option key={prod.product_id} value={prod.product_id}>
                      {prod.name} (stock: {prod.stock})
                    </option>
                  ))}
                </select>
              </div>

              {/* Shoe Size Inventory Allocation & Checks */}
              {dropForm.product_id && dropSizes.length > 0 && (
                <div
                  className="form-group"
                  style={{
                    backgroundColor: "rgba(255, 255, 255, 0.02)",
                    padding: "16px",
                    borderRadius: "8px",
                    border: "1px solid var(--border-color)",
                    marginBottom: "20px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                    <label className="form-label" style={{ margin: 0, fontSize: "12px", color: "var(--accent-neon-green)", letterSpacing: "0.5px" }}>
                      SHOE SIZE ALLOCATION &amp; STOCK CHECKS
                    </label>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>
                      Allocated: {dropForm.drop_inventory || 0} pairs
                    </span>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {dropSizes.map((sObj, idx) => {
                      const allocated = parseInt(sObj.stock, 10) || 0;
                      const isStockValid = allocated >= 0 && allocated <= sObj.maxStock;

                      return (
                        <div
                          key={sObj.size}
                          style={{
                            display: "grid",
                            gridTemplateColumns: "60px 100px 90px 1fr",
                            alignItems: "center",
                            gap: "8px",
                            padding: "6px 10px",
                            backgroundColor: "var(--bg-input)",
                            borderRadius: "6px",
                            border: isStockValid ? "1px solid var(--border-color)" : "1px solid var(--error)",
                          }}
                        >
                          <span style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-primary)" }}>
                            {sObj.size}
                          </span>

                          <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                            Max: <strong style={{ color: "var(--text-primary)" }}>{sObj.maxStock}</strong>
                          </span>

                          <input
                            type="number"
                            className="input-field"
                            style={{
                              padding: "2px 6px",
                              height: "28px",
                              fontSize: "12px",
                              borderColor: !isStockValid ? "var(--error)" : undefined,
                            }}
                            min="0"
                            max={sObj.maxStock}
                            value={sObj.stock}
                            onChange={(e) => handleDropSizeChange(idx, e.target.value)}
                          />

                          <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "flex-end" }}>
                            {isStockValid ? (
                              <span style={{ color: "var(--accent-neon-green)", fontSize: "11px", fontWeight: "600", display: "flex", alignItems: "center", gap: "3px" }}>
                                <CheckCircle2 size={13} /> Stock OK
                              </span>
                            ) : (
                              <span style={{ color: "var(--error)", fontSize: "11px", fontWeight: "600", display: "flex", alignItems: "center", gap: "3px" }}>
                                <AlertCircle size={13} /> Exceeds stock!
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Total Drop Inventory (Auto-calculated from sizes)</label>
                <input
                  type="number"
                  className="input-field"
                  value={dropForm.drop_inventory}
                  disabled
                  style={{ backgroundColor: "var(--bg-secondary)", cursor: "not-allowed" }}
                  placeholder="Sum of shoe-sizes pairs"
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
            <input
              type="text"
              className="input-field"
              placeholder="Search drops by name, ID or status..."
              value={dropFilter}
              onChange={(e) => setDropFilter(e.target.value)}
              style={{ marginBottom: "16px", fontSize: "12px", height: "36px" }}
            />
            <div style={listScrollStyle}>
              {filteredAdminDrops.map((drop) => (
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

                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "flex-end", maxWidth: "180px" }}>
                    <button
                      onClick={() => toggleVisibilityMutation.mutate(drop.drop_id)}
                      className="btn btn-outline"
                      style={{ 
                        ...actionBtnTinyStyle, 
                        color: drop.is_visible ? "var(--text-primary)" : "var(--text-muted)",
                        borderColor: drop.is_visible ? "var(--border-color)" : "dotted var(--border-color)"
                      }}
                      title={drop.is_visible ? "Hide from Public Page" : "Show on Public Page"}
                    >
                      {drop.is_visible ? <Eye size={11} /> : <EyeOff size={11} />}
                      {drop.is_visible ? " Visible" : " Hidden"}
                    </button>
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
                          onClick={() => fillDropForm(drop)}
                          className="btn btn-outline"
                          style={actionBtnTinyStyle}
                          title="Edit Drop"
                        >
                          <Edit3 size={11} /> Edit
                        </button>
                      </>
                    )}
                    {(drop.status === "SCHEDULED" || drop.status === "ENTRY_OPEN" || drop.status === "ENTRY_CLOSED" || drop.status === "SELECTING" || drop.status === "CLAIMING") && (
                      <>
                        <button
                          onClick={() => drawDropMutation.mutate(drop.drop_id)}
                          className="btn btn-primary"
                          style={actionBtnTinyStyle}
                          title="Trigger Draw & Select Winners"
                        >
                          <Send size={11} /> Draw Winners
                        </button>
                        <button
                          onClick={() => pauseDropMutation.mutate(drop.drop_id)}
                          className="btn btn-outline"
                          style={{ ...actionBtnTinyStyle, color: "var(--accent-neon-orange, #ff9900)" }}
                          title="Pause Drop"
                        >
                          <Pause size={11} /> Pause
                        </button>
                        <button
                          onClick={() => cancelDropMutation.mutate(drop.drop_id)}
                          className="btn btn-danger"
                          style={actionBtnTinyStyle}
                          title="Cancel Drop"
                        >
                          <Ban size={11} /> Cancel
                        </button>
                      </>
                    )}
                    {drop.status === "PAUSED" && (
                      <>
                        <button
                          onClick={() => resumeDropMutation.mutate(drop.drop_id)}
                          className="btn btn-primary"
                          style={actionBtnTinyStyle}
                          title="Resume Drop"
                        >
                          <Play size={11} /> Resume
                        </button>
                        <button
                          onClick={() => cancelDropMutation.mutate(drop.drop_id)}
                          className="btn btn-danger"
                          style={actionBtnTinyStyle}
                          title="Cancel Drop"
                        >
                          <Ban size={11} /> Cancel
                        </button>
                      </>
                    )}
                    
                    {/* Delete button available for ALL drop states */}
                    <button
                      onClick={() => {
                        if (window.confirm(`Delete Drop #${drop.drop_id}? Reserved stock will be restored back to product inventory.`)) {
                          deleteDropMutation.mutate(drop.drop_id);
                        }
                      }}
                      className="btn btn-danger"
                      style={actionBtnTinyStyle}
                      title="Delete Drop & Restore Stock"
                    >
                      <Trash2 size={11} /> Delete
                    </button>
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