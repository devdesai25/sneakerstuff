import http from 'k6/http';
import { check } from 'k6';

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
    http_req_duration: ['p(95)<2000'], // 95% of requests should complete within 2000ms
  },
};

export default function () {
  const rand = Math.floor(Math.random() * 10000000);
  const uniqueId = `u_${__VU}_${__ITER}_${rand}`;
  const payload = JSON.stringify({
    username: uniqueId,
    email: `${uniqueId}@benchmark.com`,
    password: 'password123',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post('http://host.docker.internal:8000/api/signup', payload, params);

  check(res, {
    'status is 200 or 201': (r) => r.status === 200 || r.status === 201,
  });
}
