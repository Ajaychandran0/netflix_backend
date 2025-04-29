// config/httpLogger.ts

import type { IncomingMessage, ServerResponse } from 'http';
import pinoHttp, { HttpLogger } from 'pino-http';
import { randomUUID } from 'crypto';
import { logger } from './logger';
import { env } from './env';


export const httpLogger: HttpLogger<IncomingMessage, ServerResponse> = pinoHttp({
    logger,

    // Generate and attach a unique request ID
    genReqId: (req): string => {
        const requestId = req.headers['x-request-id'] as string ?? randomUUID();
        req.id = requestId;
        return requestId;
    },

    // Attach custom props to log (like requestId)
    customProps: (req, _res: ServerResponse) => {
        return {
            requestId: req.id,
        };
    },

    // Log level based on response status or error
    customLogLevel: (_req, res: ServerResponse, err?: Error) => {
        if (err || res.statusCode >= 500) return 'error';
        if (res.statusCode >= 400) return 'warn';
        return 'info';
    },

    // Control what data gets logged
    serializers: {
        req(req) {
            return env.NODE_ENV === 'development'
                ? {
                    method: req.method,
                    url: req.url,
                    headers: req.headers,
                    id: req.id,
                }
                : {
                    method: req.method,
                    url: req.url,
                    id: req.id,
                };
        },
        res(res: ServerResponse) {
            return {
                statusCode: res.statusCode,
            };
        },
    },

    // Log only on errors in production for better performance
    quietReqLogger: env.NODE_ENV !== 'development',
});
