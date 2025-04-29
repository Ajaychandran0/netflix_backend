// types/global/index.d.ts

import type { ReqId } from 'pino-http';

// Extending the IncomingMessage type to add an `id` property.
declare module 'http' {
  interface IncomingMessage {
    id: ReqId;
  }
}
