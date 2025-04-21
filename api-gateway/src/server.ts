import { App } from './app';
import dotenv from 'dotenv';

dotenv.config();
const PORT = process.env.PORT || 8080;

const app = new App();
app.listen(PORT);
