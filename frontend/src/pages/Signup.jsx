/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

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
import { UserPlus, User, Mail, Lock, ShieldCheck, Eye, EyeOff } from "lucide-react";

// Form validation schema using Zod
const signupSchema = z
  .object({
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .regex(/^[a-zA-Z0-9_]+$/, "Username can only contain alphanumeric characters and underscores"),
    email: z.string().min(1, "Email is required").email("Invalid email format"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirmPassword: z.string().min(1, "Confirm password is required"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export default function Signup() {
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useContext(AuthContext);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Setup React Hook Form with Zod schema resolver
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      // Signup payload mapping
      // Backend expects JSON payload: { username, email, password }
      const res = await api.post("/signup", {
        username: data.username,
        email: data.email,
        password: data.password,
      });

      // Auto-logs the user in on successful signup
      login(res.data.access_token, res.data.user);
      toast.success(`Account created! Welcome, ${data.username}!`);
      navigate("/");
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail || "Signup failed. Username or email might be taken.";
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

        <h2 style={titleStyle}>CREATE AN ACCOUNT</h2>
        <p style={subtitleStyle}>Register your email to enter exclusive draws and cop sneaker grails</p>

        <form onSubmit={handleSubmit(onSubmit)} style={formStyle}>
          {/* Username (Public Identity) */}
          <div className="form-group">
            <label className="form-label">Public Username</label>
            <div style={inputWrapperStyle}>
              <User size={16} style={inputIconStyle} />
              <input
                type="text"
                className="input-field"
                placeholder="e.g. kicks_expert"
                style={{ paddingLeft: "42px" }}
                {...register("username")}
                disabled={isSubmitting}
              />
            </div>
            {errors.username && <span style={errorTextStyle}>{errors.username.message}</span>}
          </div>

          {/* Email Address (Login Credential) */}
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

          {/* Password */}
          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={inputWrapperStyle}>
              <Lock size={16} style={inputIconStyle} />
              <input
                type={showPassword ? "text" : "password"}
                className="input-field"
                placeholder="Min. 6 characters"
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

          {/* Confirm Password */}
          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <div style={inputWrapperStyle}>
              <ShieldCheck size={16} style={inputIconStyle} />
              <input
                type={showConfirmPassword ? "text" : "password"}
                className="input-field"
                placeholder="Repeat password"
                style={{ paddingLeft: "42px", paddingRight: "42px" }}
                {...register("confirmPassword")}
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                style={togglePasswordBtnStyle}
                aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
              >
                {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.confirmPassword && (
              <span style={errorTextStyle}>{errors.confirmPassword.message}</span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary"
            style={submitBtnStyle}
            disabled={isSubmitting}
          >
            {isSubmitting ? "CREATING ACCOUNT..." : <>REGISTER <UserPlus size={16} /></>}
          </button>
        </form>

        <div style={footerStyle}>
          <span>Already have an account?</span>{" "}
          <Link to="/login" style={linkStyle}>
            Log In
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

// Inline Page Styles
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

const submitBtnStyle = {
  width: "100%",
  padding: "14px",
  backgroundColor: "#111111",
  color: "#ffffff",
  fontWeight: "700",
  marginTop: "12px",
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