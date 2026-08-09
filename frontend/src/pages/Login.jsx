import { useContext, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
// eslint-disable-next-line no-unused-vars
import { motion } from "framer-motion";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import api from "../services/api";
import { LogIn, Mail, Lock, Eye, EyeOff } from "lucide-react";

// Form validation schema using Zod
const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email format"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

export default function Login() {
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useContext(AuthContext);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Setup React Hook Form with Zod schema resolver
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      // OAuth2 request formatting
      // Map frontend 'email' value to the backend OAuth2 username field
      const formData = new URLSearchParams();
      formData.append("username", data.email);
      formData.append("password", data.password);

      const res = await api.post("/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      // Decodes JWT and updates state inside AuthContext
      login(res.data.access_token);
      toast.success("Welcome back to SNEAKERSTUFF!");
      navigate("/");
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail || "Invalid email or password.";
      toast.error(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={containerStyle}>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="premium-panel animate-fade-in" 
        style={cardStyle}
      >
        <div style={brandHeaderStyle}>
          <Link to="/" style={logoStyle}>
            SNEAKER<span>STUFF</span>
          </Link>
        </div>

        <h2 style={titleStyle}>LOG IN</h2>
        <p style={subtitleStyle}>Log in with your email address to enter sneaker draws</p>

        <form onSubmit={handleSubmit(onSubmit)} style={formStyle}>
          {/* Email input group */}
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div style={inputWrapperStyle}>
              <Mail size={16} style={inputIconStyle} />
              <input
                type="email"
                className="input-field"
                placeholder="e.g. user@domain.com"
                style={{ paddingLeft: "42px" }}
                {...register("email")}
                disabled={isSubmitting}
              />
            </div>
            {errors.email && <span style={errorTextStyle}>{errors.email.message}</span>}
          </div>

          {/* Password input group */}
          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={inputWrapperStyle}>
              <Lock size={16} style={inputIconStyle} />
              <input
                type={showPassword ? "text" : "password"}
                className="input-field"
                placeholder="Enter password"
                style={{ paddingLeft: "42px", paddingRight: "42px" }}
                {...register("password")}
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={togglePasswordBtnStyle}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && <span style={errorTextStyle}>{errors.password.message}</span>}
          </div>

          <div style={optionsRowStyle}>
            <label style={checkboxLabelStyle}>
              <input type="checkbox" style={{ marginRight: "6px" }} />
              Remember Me
            </label>
            <a href="#forgot" style={forgotLinkStyle}>Forgot Password?</a>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary"
            style={submitBtnStyle}
            disabled={isSubmitting}
          >
            {isSubmitting ? "LOGGING IN..." : <>LOG IN <LogIn size={16} /></>}
          </button>
        </form>

        <div style={footerStyle}>
          <span>New to SNEAKERSTUFF?</span>{" "}
          <Link to="/signup" style={linkStyle}>
            Create an Account
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

// Inline Page Styles (Foot Locker Red/Black Theme)
const containerStyle = {
  minHeight: "calc(100vh - 160px)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "48px 20px",
  backgroundColor: "#f6f6f6",
};

const cardStyle = {
  width: "100%",
  maxWidth: "440px",
  border: "1px solid var(--border-color)",
  boxShadow: "var(--shadow-md)",
};

const brandHeaderStyle = {
  display: "flex",
  justifyContent: "center",
  marginBottom: "24px",
};

const logoStyle = {
  fontFamily: "var(--font-display)",
  fontWeight: "900",
  fontSize: "24px",
  color: "var(--text-primary)",
};

const titleStyle = {
  fontSize: "24px",
  color: "var(--text-primary)",
  marginBottom: "6px",
  textAlign: "center",
};

const subtitleStyle = {
  color: "var(--text-muted)",
  fontSize: "13px",
  marginBottom: "32px",
  textAlign: "center",
  lineHeight: "1.4",
};

const formStyle = {
  display: "flex",
  flexDirection: "column",
};

const inputWrapperStyle = {
  position: "relative",
  display: "flex",
  alignItems: "center",
};

const inputIconStyle = {
  position: "absolute",
  left: "14px",
  color: "#888888",
};

const errorTextStyle = {
  color: "var(--error)",
  fontSize: "11px",
  fontWeight: "600",
  marginTop: "4px",
};

const optionsRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginTop: "6px",
  marginBottom: "24px",
  fontSize: "13px",
};

const checkboxLabelStyle = {
  display: "inline-flex",
  alignItems: "center",
  color: "var(--text-muted)",
  cursor: "pointer",
};

const forgotLinkStyle = {
  color: "var(--text-muted)",
  textDecoration: "underline",
};

const submitBtnStyle = {
  width: "100%",
  padding: "14px",
  backgroundColor: "#111111",
  color: "#ffffff",
  fontWeight: "700",
};

const footerStyle = {
  marginTop: "24px",
  textAlign: "center",
  fontSize: "13px",
  color: "var(--text-muted)",
};

const linkStyle = {
  color: "var(--accent-red)",
  fontWeight: "700",
};

const togglePasswordBtnStyle = {
  position: "absolute",
  right: "14px",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  color: "#888888",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "4px",
};