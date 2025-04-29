import pino from 'pino';
import { env } from './env';

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



