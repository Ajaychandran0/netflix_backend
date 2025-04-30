import { App } from './app';
import { env } from './core/config/env'; // <- load env early

const PORT = env.USER_SERVICE_PORT || 3001;

const app = new App();
app.listen(PORT);
