import { useState, useEffect, useContext } from 'react'
import { BrowserRouter, Routes, Route} from 'react-router-dom'
import Home from './pages/Home'
import Signup from './pages/Signup'
import Login from './pages/Login'
import Admin from './pages/Admin'
import Cart from './pages/cart'
import Orders from './pages/Orders'
import Navbar from './components/Navbar'
import axios from "axios"
import AuthContext from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const [message, setMessage] = useState("")
  
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/")
    .then(res => setMessage(res.data.message))
    .catch(err => console.log(err));
  },[]);

  return (
    <BrowserRouter>
    <Navbar />
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/login' element={<Login />} />
        <Route path='/signup' element={<Signup />} />
        <Route path='/Admin' element={<ProtectedRoute> <Admin /> </ProtectedRoute>} />
        <Route path='/Cart' element={ <ProtectedRoute> <Cart /> </ProtectedRoute>} />
        <Route path='/orders' element={<ProtectedRoute> <Orders /> </ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App