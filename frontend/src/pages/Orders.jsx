import { useState, useEffect } from "react";
import { 
    getOrder, 
    payOrder, 
    cancelOrder 
} from "../services/orderApi";

import OrderCard from "../components/OrderCard";

function Orders() {
    const [orders, setOrders] = useState([]);

    useEffect(()=>{
        fetchOrders();
    }, []);

    const fetchOrders = async() => {
        try{
            const data = await getOrder();
            setOrders(data.orders);
        } catch(error) {
            console.log(error);
        }
    }
    
    const handlePay = async (id) => {
        try{
            await payOrder(id);
            fetchOrders();
        } catch(error) {
            alert(
                error.response?.data?.detail || 
                "Payment failed"
            );
        }
    }

    const handleCancel = async (id) => {
        try{
            await cancelOrder(id);
            fetchOrders();
        } catch(error) {
            alert(
                error.response?.data?.detail || 
                "Cancel Failed"
            );
        }
    }

    return (<div>
        <h1>My Orders</h1>

        {orders.map((order)=>(
            <OrderCard 
                key={order.order_id}
                order={order}
                onPay={handlePay}
                onCancel={handleCancel}
            />
        ))}    
    </div>)
}

export default Orders;