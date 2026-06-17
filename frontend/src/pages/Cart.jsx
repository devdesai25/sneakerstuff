import { useEffect, useState } from "react";
import {useNavigate} from "react-router-dom";
import api from "../services/api";
import { createOrder} from "../services/orderApi";

function Cart() {
  const [cart, setCart] = useState([]);
  const [address, setAddress] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const res = await api.get("/cart");

      setCart(res.data);

    } catch (err) {
      console.log(err);
    }
  };

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const deleteItem = async (product_id) => {
    try{
      const res = await api.delete(`/cart/${product_id}`)
      await fetchCart();
    } catch(error)
    {
      console.error(error);
    }
  }

  const incrementItem = async (product_id) => {
    try{
      const res = await api.post("/cart",{
        product_id: product_id,
        quantity: 1
      })

      await fetchCart();
    } catch(error) {
      console.log(error);
      
    }
  }

  const decrementItem = async (item) => {
    try{
      const res = await api.patch(`/cart/${item.product_id}`, {
        quantity: item.quantity - 1
      })

      await fetchCart();
    } catch(error){
      console.log(error);
    }
  }
  
  const orderItems = async(address) => {
    try{
      const res = await createOrder(address);

      await fetchCart();
      
      navigate("/orders");
      
    } catch(error) {
      console.log(error);
    }
  }

  return (
    <div>
      <h1>Cart</h1>

      {cart.map((item) => (
        <div
          key={item.product_id}
          style={{
            display: "flex",
            gap: "20px",
            marginBottom: "20px",
          }}
        >
          <img
            src={item.image_url}
            alt={item.name}
            width="120"
          />

          <div>
            <h3>{item.name}</h3>
            <p>₹{item.price}</p>
            <p>Quantity: {item.quantity}</p>
            <p>
              Subtotal: ₹
              {item.price * item.quantity}
            </p>
            
            <button
              onClick={() => decrementItem(item)}
            >
              -
            </button>

            <span
              style={{
              margin: "0 10px"
              }}
            >
              {item.quantity}
            </span>

            <button
              onClick={() => incrementItem(item.product_id)}
            >
              +
            </button>

            <button 
              onClick={() => deleteItem(item.product_id)}
              style={{
              marginLeft: "20px"
              }}
            >
              Delete
            </button>
          
          </div>
        </div>
      ))}

      <h2>Total: ₹{total}</h2>
      <input 
      type="text"
      value={address}
      onChange={(e)=>setAddress(e.target.value)}
      placeholder="Enter Delivery Address"
      />
      <button onClick={()  => orderItems(address) }
        style={{
        marginLeft: "20px"
      }}
      >
        Order
      </button>
    </div>
  );
}

export default Cart;
