import { App } from './app';
import { config } from './config/env'; // <- load env early

const PORT = config.PORT;

const app = new App();
app.listen(PORT);
