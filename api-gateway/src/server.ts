import { App } from './app';
import { env } from '@core/config/env';

const PORT = env.API_GATEWAY_PORT || 3000;

const app = new App();
app.listen(PORT);
