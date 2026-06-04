import { useContext } from "react"
import { AuthContext } from "../context/AuthContext"
import { Navigate } from "react-router-dom";

function ProtectedRoute({ children }) {

    const {isLoggedIn} = useContext(AuthContext);
    console.log("isLoggedIn =", isLoggedIn);

    if (!isLoggedIn) { 
        return <Navigate to="/login" />
    }
    return children
}

export default ProtectedRoute