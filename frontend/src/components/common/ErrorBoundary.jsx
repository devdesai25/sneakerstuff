import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "400px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "24px",
            textAlign: "center",
            backgroundColor: "#0f1322",
            border: "1px solid #212946",
            borderRadius: "12px",
            margin: "24px auto",
            maxWidth: "600px",
          }}
        >
          <h2 style={{ color: "#ef4444", marginBottom: "16px", fontFamily: "Outfit, sans-serif" }}>
            SOMETHING WENT WRONG
          </h2>
          <p style={{ color: "#94a3b8", marginBottom: "24px" }}>
            The UI encountered an error. This might be due to a backend service exception.
          </p>
          <pre
            style={{
              padding: "16px",
              background: "#060913",
              border: "1px solid #212946",
              borderRadius: "8px",
              color: "#94a3b8",
              fontSize: "12px",
              maxWidth: "100%",
              overflowX: "auto",
              marginBottom: "24px",
              textAlign: "left",
            }}
          >
            {this.state.error?.toString() || "Unknown Error"}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: "12px 24px",
              background: "#f8fafc",
              color: "#060913",
              border: "none",
              borderRadius: "8px",
              fontWeight: "700",
              cursor: "pointer",
            }}
          >
            RELOAD PAGE
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
