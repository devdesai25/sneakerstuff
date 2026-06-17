export default function OrderCard ({
    order, 
    onPay, 
    onCancel
}) {

    return (
        <div 
        style={{
            border: "1px solid gray",
            padding: "10px",
            marginBottom: "10px"
        }}>
            Order #{order.order_id}
                
                <p>Status: {order.status}</p>

                <p>Total: {order.total_amount}</p>

                <p>Address: {order.address}</p>

                {order.items.map(item => (
                    <div key={item.product_id}>
                        <p>
                            Product ID: {item.product_id}
                        </p>
                        <p>
                            Quantity: {item.quantity}
                        </p>
                        <p>
                            Unit Price: {item.unit_price}
                        </p>
                        <p>
                            Subtotal: {item.subtotal}
                        </p>
                    </div>
                ))}

                {order.status === "Pending" && (
                    <>
                        <button
                            onClick={()=>
                                onPay(order.order_id)
                            }
                        >
                            Pay
                        </button>
                        <button
                            onClick={()=>
                                onCancel(order.order_id)
                            }
                        >
                            Cancel
                        </button>
                    </>
                )}
        </div>
    )
}