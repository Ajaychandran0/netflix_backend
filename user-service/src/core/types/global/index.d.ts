import type { ReqId } from 'pino-http';
import { PrismaClient } from '@prisma/client';


// Extending the IncomingMessage type to add an `id` property.
declare module 'http' {
  interface IncomingMessage {
    id: ReqId;
  }
}
