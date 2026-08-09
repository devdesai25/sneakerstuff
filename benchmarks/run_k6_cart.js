import http from 'k6/http';
import { check, group } from 'k6';

const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjI0IiwidXNlcm5hbWUiOiJiZW5jaF90ZXN0X3VzZXIiLCJlbWFpbCI6ImJlbmNoX3Rlc3RfdXNlckBiZW5jaG1hcmsuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODYwOTA5MjV9.2JvDOo6c5EjrelxhO7OiHmqPSXozZVL-qvDh5y9oKpY';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Tier 1: 10 VUs
    { duration: '15s', target: 100 },  // Tier 2: 100 VUs simultaneously modifying carts
    { duration: '15s', target: 500 },  // Tier 3: 500 VUs
    { duration: '20s', target: 1000 }, // Tier 4: 1000 VUs
    { duration: '10s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_failed: ['rate<0.10'],    // Allow <10% failure due to concurrent lock conflicts
    http_req_duration: ['p(95)<2000'], // 95% within 2000ms
  },
};

const params = {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${AUTH_TOKEN}`,
  },
};

export default function () {
  // Scenario 1: Add item to cart
  group('Add to Cart', function () {
    const payload = JSON.stringify({
      product_id: 284,
      quantity: 1,
      size: 'US 7',
    });
    const res = http.post('http://host.docker.internal:8000/api/cart', payload, params);
    check(res, {
      'status is 200 or 409': (r) => r.status === 200 || r.status === 409,
    });
  });

  // Scenario 2: View Cart
  group('Get Cart', function () {
    const res = http.get('http://host.docker.internal:8000/api/cart', params);
    check(res, {
      'status is 200': (r) => r.status === 200,
    });
  });

  // Scenario 3: Update Cart quantity
  group('Update Cart', function () {
    const payload = JSON.stringify({
      quantity: 2,
    });
    const res = http.patch('http://host.docker.internal:8000/api/cart/284', payload, params);
    check(res, {
      'status is 200 or 404 or 409': (r) => r.status === 200 || r.status === 404 || r.status === 409,
    });
  });

  // Scenario 4: Delete item from Cart
  group('Delete Cart', function () {
    const res = http.del('http://host.docker.internal:8000/api/cart/284', null, params);
    check(res, {
      'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });
  });
}
