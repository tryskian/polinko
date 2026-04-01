import http from "k6/http";
import { check, sleep } from "k6";

const vus = Number(__ENV.VUS || 3);
const duration = __ENV.DURATION || "10s";

export const options = {
  vus,
  duration,
};

const baseUrl = (__ENV.BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export default function () {
  const payload = JSON.stringify({
    session_id: "k6-chat-smoke",
    message: "k6 smoke prompt",
  });
  const headers = {
    "Content-Type": "application/json",
  };
  const res = http.post(`${baseUrl}/chat`, payload, {
    headers,
    timeout: "30s",
  });

  check(res, {
    "status is 200": (r) => r.status === 200,
    "contains response field": (r) => String(r.body || "").includes('"response"'),
  });

  sleep(1);
}
