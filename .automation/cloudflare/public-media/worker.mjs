import manifest from './manifest.mjs';
import { serveMedia } from './serve.mjs';

export default {
  fetch(request, env) {
    return serveMedia(request, manifest, {
      get(key, range) { return env.PUBLIC_MEDIA.get(key, range ? { range } : undefined); },
      head(key) { return env.PUBLIC_MEDIA.head(key); },
    }, request => fetch(request));
  },
};
