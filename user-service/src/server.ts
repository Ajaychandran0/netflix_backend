import { App } from './app';
import { config } from './config/env'; // <- load env early

const PORT = config.USER_SERVICE_URL || 3001;

const app = new App();
app.listen(PORT);
