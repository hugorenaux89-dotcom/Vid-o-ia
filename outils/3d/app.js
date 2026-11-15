import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';
import * as M from './monde.js';
import { construire } from './plans.js';

let renderer, effect, ctx;
window.init = async (init) => {
  const canvas = document.getElementById('c');
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(720, 1280, false);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  effect = new OutlineEffect(renderer, { defaultThickness: 0.0045, defaultColor: [0.05, 0.03, 0.06] });
  ctx = await construire(THREE, M, init, renderer);
};
window.frame = (T, svg) => {
  const { scene, camera, viewports } = ctx.update(T);
  if (viewports) {
    renderer.setScissorTest(true);
    for (const v of viewports) {
      renderer.setViewport(v.x, v.y, v.w, v.h); renderer.setScissor(v.x, v.y, v.w, v.h);
      effect.render(v.scene, v.camera);
    }
    renderer.setScissorTest(false); renderer.setViewport(0, 0, 720, 1280);
  } else effect.render(scene, camera);
  document.getElementById('o').innerHTML = svg || '';
};
window.pret = true;
