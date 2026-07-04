/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useCallback, useMemo } from "react";
import { CheckCircle2, XCircle, AlertCircle, Info, X } from "lucide-react";
import "../../styles/toast.css";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback((message, type = "info", duration = 4000) => {
    const id = Date.now() + Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, [removeToast]);

  const value = useMemo(() => ({
    success: (msg) => addToast(msg, "success"),
    error: (msg) => addToast(msg, "error"),
    warning: (msg) => addToast(msg, "warning"),
    info: (msg) => addToast(msg, "info"),
    remove: removeToast
  }), [addToast, removeToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onClose }) {
  const icon = useMemo(() => {
    switch (toast.type) {
      case "success":
        return <CheckCircle2 className="toast-icon" size={18} />;
      case "error":
        return <XCircle className="toast-icon" size={18} />;
      case "warning":
        return <AlertCircle className="toast-icon" size={18} />;
      case "info":
      default:
        return <Info className="toast-icon" size={18} />;
    }
  }, [toast.type]);

  return (
    <div className={`toast toast-${toast.type}`}>
      {icon}
      <div className="toast-message">{toast.message}</div>
      <button className="toast-close" onClick={() => onClose(toast.id)}>
        <X size={16} />
      </button>
    </div>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
