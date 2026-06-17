import { useState, useEffect } from "react"
import "./Home.css"
import api from "../services/api";

function Home(){
    
    const [products, setProduct] = useState([])

    const fetchProducts = async () => {
        try{
            const res = await api.get("/admin/products")    
            setProduct(res.data);
        }catch(error){
            console.log("Error fetching products",error)
        }
    };

    useEffect(()=>{
    
        fetchProducts()

    }, []);
    
    const addToCart = async (productId) => {
        try{
            const res = await api.post("cart", 
                {
                    product_id: productId,
                    quantity: 1
                })
            
            console.log(res)
        }catch(error){
            console.log("Error Fetching Products", error)
        }
    }

    return (<div className="product-grid">
        {products.map(product => (
            <div key={product.product_id} className="card">
                <img src={product.images} alt={product.name} />    
                <h3>{product.name}</h3>
                <p className="price">
                    {product.price}
                </p>
                <p className="description">
                    {product.description}
                </p>
                <button onClick={() => addToCart(product.product_id)}>Add To Cart</button>
            </div>
        ))}
    </div>)
}

export default Home