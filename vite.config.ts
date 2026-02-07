import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        control_center: resolve(__dirname, 'control_center.html'),
        ai_intro: resolve(__dirname, 'ai_intro.html'),
        preview_homepage: resolve(__dirname, 'preview_homepage.html'),
        signage: resolve(__dirname, 'signage.html'),
        desktop: resolve(__dirname, 'desktop.html'),
        cloud_gallery: resolve(__dirname, 'cloud_gallery.html'),
        translator: resolve(__dirname, 'translator.html'),
        usb_view: resolve(__dirname, 'usb_view.html'),
        wuchang_homepage_hq: resolve(__dirname, 'wuchang_homepage_hq.html'),
        wuchang_homepage_google_style: resolve(__dirname, 'wuchang_homepage_google_style.html'),
        schedule: resolve(__dirname, 'schedule.html'),
        animation_studio: resolve(__dirname, 'animation_studio.html'),
      },
    },
  },
});
