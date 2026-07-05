import "../../styles/skeleton.css";

export function Skeleton({ className, style }) {
  return <div className={`skeleton ${className || ""}`} style={style} />;
}

export function ProductCardSkeleton() {
  return (
    <div className="skeleton-card">
      <Skeleton className="skeleton-image" />
      <Skeleton className="skeleton-title" />
      <Skeleton className="skeleton-text" style={{ width: "80%" }} />
      <Skeleton className="skeleton-text" style={{ width: "40%" }} />
      <Skeleton className="skeleton-text" style={{ height: "40px", marginTop: "12px", borderRadius: "12px" }} />
    </div>
  );
}

export function ProductGridSkeleton({ count = 4 }) {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: count }).map((_, index) => (
        <ProductCardSkeleton key={index} />
      ))}
    </div>
  );
}

export function ProductDetailsSkeleton() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "32px", width: "100%" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "24px" }}>
        <Skeleton style={{ width: "100%", aspectRatio: "1.2", borderRadius: "16px" }} />
      </div>
      <div>
        <Skeleton style={{ height: "32px", width: "30%", marginBottom: "12px" }} />
        <Skeleton style={{ height: "48px", width: "70%", marginBottom: "16px" }} />
        <Skeleton style={{ height: "24px", width: "20%", marginBottom: "24px" }} />
        <Skeleton style={{ height: "16px", width: "100%", marginBottom: "12px" }} />
        <Skeleton style={{ height: "16px", width: "95%", marginBottom: "12px" }} />
        <Skeleton style={{ height: "16px", width: "80%", marginBottom: "32px" }} />
        <Skeleton style={{ height: "50px", width: "50%", borderRadius: "12px" }} />
      </div>
    </div>
  );
}

export function OrderCardSkeleton() {
  return (
    <div className="skeleton-card" style={{ gap: "12px", marginBottom: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <Skeleton style={{ height: "24px", width: "30%" }} />
        <Skeleton style={{ height: "24px", width: "20%" }} />
      </div>
      <Skeleton style={{ height: "16px", width: "40%" }} />
      <Skeleton style={{ height: "16px", width: "60%" }} />
      <div style={{ borderTop: "1px solid #212946", paddingTop: "12px", display: "flex", gap: "12px" }}>
        <Skeleton style={{ height: "40px", width: "100px", borderRadius: "8px" }} />
        <Skeleton style={{ height: "40px", width: "100px", borderRadius: "8px" }} />
      </div>
    </div>
  );
}

export function DropCardSkeleton() {
  return (
    <div className="skeleton-card" style={{ gap: "12px" }}>
      <Skeleton className="skeleton-image" style={{ aspectRatio: "1.5" }} />
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <Skeleton style={{ height: "24px", width: "50%" }} />
        <Skeleton style={{ height: "24px", width: "20%" }} />
      </div>
      <Skeleton style={{ height: "16px", width: "80%" }} />
      <Skeleton style={{ height: "40px", width: "100%", borderRadius: "8px", marginTop: "12px" }} />
    </div>
  );
}
