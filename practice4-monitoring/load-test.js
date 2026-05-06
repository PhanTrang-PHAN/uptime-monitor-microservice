import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 10,
  duration: '10s',
};

export default function () {
  let res = http.get('http://uptime.local/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
