import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig(({mode})=>({
  plugins:[tailwindcss()],server:{proxy:{'/api':'http://127.0.0.1:8000'}},
  define:mode==='showcase'?{'import.meta.env.VITE_SHOWCASE':'"true"','import.meta.env.VITE_SHOWCASE_AI':'"true"'}:{}
}));
