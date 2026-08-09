import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Tier 1: 10 VUs
    { duration: '15s', target: 100 },  // Tier 2: 100 VUs
    { duration: '15s', target: 500 },  // Tier 3: 500 VUs
    { duration: '20s', target: 1000 }, // Tier 4: 1000 VUs
    { duration: '10s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],    // Error rate should be < 5%
    http_req_duration: ['p(95)<1000'], // 95% of read requests should complete within 1000ms
  },
};

export default function () {
  // Scenario 1: Product List (Read-heavy)
  group('Product List', function () {
    const res = http.get('http://host.docker.internal:8000/api/products?limit=10&offset=0');
    check(res, {
      'status is 200': (r) => r.status === 200,
      'body is non-empty list': (r) => r.body && r.body.length > 2,
    });
  });

  // Scenario 2: Single Product Details by ID
  group('Product Details', function () {
    const res = http.get('http://host.docker.internal:8000/api/products/284');
    check(res, {
      'status is 200': (r) => r.status === 200,
    });
  });

  // Scenario 3: Product Search Query
  group('Product Search - Common Keyword', function () {
    const res = http.get('http://host.docker.internal:8000/api/products?q=Nike');
    check(res, {
      'status is 200': (r) => r.status === 200,
    });
  });

  group('Product Search - Rare Keyword', function () {
    const res = http.get('http://host.docker.internal:8000/api/products?q=nonexistent_rare_query_xyz');
    check(res, {
      'status is 200': (r) => r.status === 200,
    });
  });
}
