import { env } from "@/core/config/env";

export const SERVICE_URLS = {
    USER_SERVICE: env.USER_SERVICE_URL || 'http://user-service:5000',
    // CONTENT_SERVICE: env.CONTENT_SERVICE_URL || 'http://content-service:5001',
  };
  

  