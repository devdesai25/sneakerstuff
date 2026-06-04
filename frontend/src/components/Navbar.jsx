import { useContext } from "react";
import { Link, Navigate } from "react-router-dom"
import { AuthContext } from "../context/AuthContext";

function Navbar() {

    const token = localStorage.getItem("token");
    const {isLoggedIn, setIsLoggedIn} = useContext(AuthContext)
    return(
        <nav>
            <Link to="/" >Home</Link>

            {isLoggedIn && (
                <>
                    < Link to="/admin">Admin</Link>
                    < Link to="/cart">Cart</Link>
                    < button onClick={() => {
                        localStorage.removeItem("token");
                        setIsLoggedIn(false);
                        //window.location.reload();
                    }}>
                        Logout
                    </button>
                </>
            )}

            {!isLoggedIn && (
                <>
                    < Link to="/signup">Signup</Link>
                    < Link to="/login">Login</Link>
                </>
            )}

        </nav>
    )
}

export default Navbar