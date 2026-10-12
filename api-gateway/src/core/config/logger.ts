import pino from 'pino';
import { env } from './env';

/**
 * 🔧 Pino Logger Configuration
 *
 * In development, we use `pino-pretty` for readable logs.
 * In production, we avoid pretty-printing for performance and use default JSON output.
 *
 * ---------------------------------------------------------
 * 💡 Transport Explanation:
 *  - `target`     : Defines the module that handles log output.
 *                   Common values:
 *                     'pino-pretty'       => Human-readable logs (Dev only)
 *                     'pino/file'         => Stream logs to a file (Prod/Dev)
 *                     './custom-logger.js'=> Custom handler (advanced use)
 *                     'pino-loki'         => Send logs to Grafana Loki
 *                     'pino-elasticsearch'=> Send logs to Elasticsearch
 *
 *  - `destination`: Specifies where to send the logs.
 *                   Common values:
 *                     './logs/app.log'    => Logs to a file
 *                     1                   => stdout (standard output)
 *                     2                   => stderr (standard error)
 *
 *  - `sync`       : If false, logs are written asynchronously (recommended for production).
 * ---------------------------------------------------------
 */

const isDev = env.NODE_ENV === 'development';

const transport = isDev
    ? {
        target: 'pino-pretty', // Use pretty logs in development
        options: {
            colorize: true,      // Colorize output for better readability
        },
    }
    : {
        target: 'pino/file',    // Use file logging in production
        options: {
            destination: 1,       // Log to stdout (can be picked up by container logging tools)
            sync: false,          // Enable async logging (non-blocking, better performance)
        },
    }

export const logger = pino({
    level: isDev ? 'debug' : 'info',
    transport,
});



