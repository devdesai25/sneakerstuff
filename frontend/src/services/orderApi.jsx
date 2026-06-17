import api from './api'

export const createOrder = async(address) => {
    const response = await api.post("/orders",{
        address: address
    });
    return response.data;
}

export const getOrder = async() => {
    const response = await api.get("/orders");
    return response.data;
}

export const payOrder = async(id) => {
    console.log(id, typeof id)
    const respone = await api.patch(`/orders/${id}/pay`);
    return respone.data;
}

export const cancelOrder = async(id) => {
    const response = await api.patch(`/orders/${id}/cancel`)
    return response.data;
}