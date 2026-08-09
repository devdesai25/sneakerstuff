import http from 'k6/http';
import { check, group } from 'k6';

const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjI0IiwidXNlcm5hbWUiOiJiZW5jaF90ZXN0X3VzZXIiLCJlbWFpbCI6ImJlbmNoX3Rlc3RfdXNlckBiZW5jaG1hcmsuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODYwOTA5MjV9.2JvDOo6c5EjrelxhO7OiHmqPSXozZVL-qvDh5y9oKpY';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Tier 1: 10 VUs
    { duration: '15s', target: 100 },  // Tier 2: 100 VUs
    { duration: '15s', target: 500 },  // Tier 3: 500 VUs
    { duration: '20s', target: 1000 }, // Tier 4: 1000 VUs
    { duration: '10s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_failed: ['rate<0.15'],    // Allow <15% failure rate under stock depletion / lock contention
    http_req_duration: ['p(95)<3000'], // 95% of transactions should complete within 3000ms
  },
};

const params = {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${AUTH_TOKEN}`,
  },
};

export default function () {
  let orderId = null;

  // Step 1: Ensure item in cart
  group('Prepare Cart', function () {
    const cartPayload = JSON.stringify({
      product_id: 284,
      quantity: 1,
      size: 'US 7',
    });
    http.post('http://host.docker.internal:8000/api/cart', cartPayload, params);
  });

  // Step 2: Create Order (Multi-table transaction + FOR UPDATE stock lock)
  group('Create Order', function () {
    const orderPayload = JSON.stringify({
      address: '123 Sneaker Street, New York, NY 10001',
    });
    const res = http.post('http://host.docker.internal:8000/api/orders', orderPayload, params);

    const success = check(res, {
      'order status 200/201 or 422/404': (r) => r.status === 200 || r.status === 201 || r.status === 422 || r.status === 404,
    });

    if (res.status === 200 || res.status === 201) {
      try {
        const body = JSON.parse(res.body);
        orderId = body.order_id;
      } catch (e) {
        orderId = null;
      }
    }
  });

  // Step 3: Pay for Order
  if (orderId) {
    group('Pay Order', function () {
      const res = http.patch(`http://host.docker.internal:8000/api/orders/${orderId}/pay`, null, params);
      check(res, {
        'payment status 200 or 400': (r) => r.status === 200 || r.status === 400,
      });
    });
  }

  // Step 4: Get Order History
  group('Get Order History', function () {
    const res = http.get('http://host.docker.internal:8000/api/orders', params);
    check(res, {
      'status is 200': (r) => r.status === 200,
    });
  });
}
