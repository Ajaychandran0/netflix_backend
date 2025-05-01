import { env } from "@/core/config/env";

export const SERVICE_URLS = {
    USER_SERVICE: env.USER_SERVICE_URL || 'http://user-service:5000',
    // CONTENT_SERVICE: env.CONTENT_SERVICE_URL || 'http://content-service:5001',
    // VIDEO_SERVICE: env.VIDEO_SERVICE_URL || 'http://video-processing-service:5002',
    // RECOMMENDATION_SERVICE: env.RECOMMENDATION_SERVICE_URL || 'http://recommendation-service:5003',
  };
  