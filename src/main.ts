
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';

import {makeChannel} from 'sync-message';
import {SyncClient} from 'comsync';
import * as Comlink from "comlink";
import { serviceWorkerFile } from 'virtual:vite-plugin-service-worker'

import { ref } from 'vue';
import type { Ref } from 'vue';

const pyClient: Ref<SyncClient | null> = ref(null);

const pinia = createPinia();
const app = createApp(App);

app.provide('pyClient', pyClient);
app.use(pinia);
app.mount('#app');

if ("serviceWorker" in navigator) {
  // Register a service worker hosted at the root of the
  // site using the default scope.
  navigator.serviceWorker.register(serviceWorkerFile.slice(1), {type: 'module'}).then(
    (registration) => {
      console.log("Service worker registration succeeded:", registration);
      
      const channel = makeChannel({
        serviceWorker: {
          scope: registration.scope,
          timeout: 10
        }
      });
      const client = new SyncClient(() => new Worker(new URL('./worker/pyodide.ts', import.meta.url), {type: 'module'}), channel);
      pyClient.value = client;

      function notifyCallback(name: string, ...args: any[]) {
        const table: { [key: string]: any } = {
          print: (...args: any[]) => {
            console.log(...args);
          },
          sleep: (seconds: number) => {
            setTimeout(() => client.writeMessage('time up'), seconds*1000);
          },
          await_js: (code: string) => {
            const p = eval(code);
            if (p.then) {
              p.then((result: any) => {
                client.writeMessage(result);
              }).catch((error: any) => {
                throw error;
              });
            } else {
              return p;
            }
          }
        };
        const fn = table[name];
        if (fn) {
          return fn(...args);
        } else {
          throw new Error(`no function with name ${name}`);
        }
      }

      client.call(client.workerProxy.init).then(() => {
        console.log('init ok');
        return client.workerProxy.setStdout(Comlink.proxy(notifyCallback));
      }).then(() => {
        console.log('set stdout ok');
        client.call(client.workerProxy.runPython, `
          print('before')
          await_js('new Promise((resolve, reject) => setTimeout(resolve, 1000))')
          print('after')
        `, {}, Comlink.proxy(notifyCallback));
        // client.call(client.workerProxy.runTest, Comlink.proxy(notifyCallback));
      });
    },
    (error) => {
      console.error(`Service worker registration failed: ${error}`);
    },
  );
} else {
  console.error("Service workers are not supported.");
}
