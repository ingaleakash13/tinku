// Tinku & Friends — 3D test scene (three.js, toon shading). window.renderAt(t) draws the frame for song time t.
import * as THREE from './node_modules/three/build/three.module.js';

const D = await (await fetch('data.json')).json();
const B = 60 / D.bpm;
const W = 1280, H = 720;
const PI = Math.PI;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const back = (x, s = 1.7) => { x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1; };

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('stage').appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 200);

// ---------- toon materials + outlines
const grad = new THREE.DataTexture(new Uint8Array([90, 90, 90, 255, 170, 170, 170, 255, 255, 255, 255, 255]), 3, 1);
grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
const matCache = {};
function toon(col, emissive = 0) {
  const k = col + ':' + emissive;
  if (!matCache[k]) matCache[k] = new THREE.MeshToonMaterial({ color: new THREE.Color(col), gradientMap: grad, emissive: new THREE.Color(col), emissiveIntensity: emissive });
  return matCache[k];
}
const OUT = new THREE.MeshBasicMaterial({ color: 0x2a1a24, side: THREE.BackSide });
function mesh(geo, col, { outline = 0.035, shadow = true, emissive = 0 } = {}) {
  const m = new THREE.Mesh(geo, toon(col, emissive));
  m.castShadow = shadow; m.receiveShadow = true;
  if (outline) {
    const o = new THREE.Mesh(geo, OUT);
    geo.computeBoundingSphere();
    const r = geo.boundingSphere.radius || 1;
    o.scale.setScalar(1 + outline / r); o.position.copy(geo.boundingSphere.center).multiplyScalar(-outline / r);
    m.add(o);
  }
  return m;
}
const sph = (r, ws = 32, hs = 24) => new THREE.SphereGeometry(r, ws, hs);
const cap = (r, l) => new THREE.CapsuleGeometry(r, l, 8, 20);
function at(obj, x, y, z, parent) { obj.position.set(x, y, z); if (parent) parent.add(obj); return obj; }

// ---------- face (eyes, glasses, mouth) shared by the kids
function face(head, o) {
  const eyes = [];
  for (const s of [-1, 1]) {
    const e = new THREE.Group(); at(e, s * o.eyeX, o.eyeY, o.eyeZ, head);
    const white = mesh(sph(o.eyeR), '#ffffff', { outline: 0.012 }); white.scale.set(0.9, 1.1, 0.55); e.add(white);
    const pupil = mesh(sph(o.eyeR * 0.6), o.iris || '#3a2414', { outline: 0 }); at(pupil, 0, -o.eyeR * 0.1, o.eyeR * 0.4, e); pupil.scale.set(0.9, 1.1, 0.6);
    const shine = mesh(sph(o.eyeR * 0.2), '#ffffff', { outline: 0, emissive: 0.8 }); at(shine, o.eyeR * 0.2, o.eyeR * 0.25, o.eyeR * 0.72, e);
    if (o.lashes) { const l = mesh(new THREE.BoxGeometry(o.eyeR * 0.7, 0.012, 0.01), '#1a0f0a', { outline: 0 }); at(l, s * o.eyeR * 0.6, o.eyeR * 0.95, o.eyeR * 0.3, e); l.rotation.z = s * 0.5; }
    eyes.push(e);
    const cheek = mesh(sph(o.eyeR * 0.6), '#ff8a9a', { outline: 0 }); cheek.scale.set(1.2, 0.7, 0.3); at(cheek, s * o.eyeX * 1.55, o.eyeY - o.eyeR * 1.6, o.eyeZ - 0.03, head);
    cheek.material = new THREE.MeshBasicMaterial({ color: '#ff8a9a', transparent: true, opacity: 0.55 });
  }
  const nose = mesh(sph(0.03), o.skinD, { outline: 0 }); at(nose, 0, o.eyeY - o.eyeR * 1.2, o.eyeZ + 0.03, head);
  // smile (closed) + open mouth (singing)
  const smile = mesh(new THREE.TorusGeometry(0.075, 0.016, 8, 24, PI), '#7c1d2c', { outline: 0 });
  smile.rotation.z = PI; at(smile, 0, o.mouthY + 0.04, o.eyeZ - 0.005, head);
  const open = new THREE.Group(); at(open, 0, o.mouthY, o.eyeZ - 0.02, head);
  const lip = mesh(sph(0.075), '#7c1d2c', { outline: 0.01 }); lip.scale.set(1, 1, 0.4); open.add(lip);
  const tongue = mesh(sph(0.045), '#ff7a8f', { outline: 0 }); at(tongue, 0, -0.035, 0.015, open); tongue.scale.set(1.1, 0.6, 0.4);
  const teeth = mesh(new THREE.BoxGeometry(0.08, 0.02, 0.02), '#ffffff', { outline: 0 }); at(teeth, 0, 0.05, 0.02, open);
  return { eyes, smile, open };
}
function setFace(f, m, blink) {
  for (const e of f.eyes) e.scale.y = blink ? 0.08 : 1;
  const on = m > 0.08; f.smile.visible = !on; f.open.visible = on;
  f.open.scale.set(0.8 + 0.25 * m, 0.25 + 0.95 * m, 1);
}

// ---------- arms (two-part with elbows)
function arm(parent, side, x, y, sleeve, skin, len = 0.5, r = 0.065) {
  const sh = new THREE.Group(); at(sh, side * x, y, 0, parent);
  const up = mesh(cap(r, len * 0.5 - r), sleeve); at(up, 0, -len * 0.25, 0, sh);
  const el = new THREE.Group(); at(el, 0, -len * 0.5, 0, sh);
  const fo = mesh(cap(r * 0.9, len * 0.45 - r), skin); at(fo, 0, -len * 0.22, 0, el);
  const hand = mesh(sph(r * 1.35), skin); at(hand, 0, -len * 0.47, 0, el);
  return { sh, el, side };
}
// pose: {out: shoulder raise sideways (0 down .. 2.8 up), fwd: forward raise, bend: elbow bend, twist}
function setArm(a, p) {
  a.sh.rotation.set(-(p.fwd || 0), 0, a.side * (p.out || 0));
  a.el.rotation.set(-(p.bendF || 0), 0, a.side * (p.bend || 0));
}

// ---------- characters
function kidBase(o) {
  const root = new THREE.Group(); const body = new THREE.Group(); root.add(body);
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(0.42 * o.scale, 32), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.18 }));
  shadow.rotation.x = -PI / 2; shadow.position.y = 0.005; root.add(shadow);
  body.scale.setScalar(o.scale);
  return { root, body, shadow };
}
function makeTinku() {
  const k = kidBase({ scale: 1.0 }); const b = k.body; const skin = '#f3c39f';
  for (const s of [-1, 1]) {
    at(mesh(cap(0.085, 0.3), '#4a78c2'), s * 0.1, 0.28, 0, b);
    const shoe = mesh(sph(0.1), '#ff6b3d'); shoe.scale.set(0.9, 0.55, 1.35); at(shoe, s * 0.1, 0.05, 0.05, b);
  }
  const hips = mesh(cap(0.13, 0.12), '#4a78c2'); hips.rotation.z = PI / 2; at(hips, 0, 0.5, 0, b);
  const torso = mesh(cap(0.2, 0.22), '#ffd23b'); torso.scale.set(1.05, 1, 0.8); at(torso, 0, 0.72, 0, b);
  const collar = mesh(new THREE.TorusGeometry(0.075, 0.018, 8, 20), '#e8a900', { outline: 0 }); collar.rotation.x = PI / 2; at(collar, 0, 0.93, 0.0, b);
  k.arms = [arm(b, -1, 0.22, 0.86, '#ffcf2e', skin), arm(b, 1, 0.22, 0.86, '#ffcf2e', skin)];
  const head = new THREE.Group(); at(head, 0, 1.28, 0, b); k.head = head;
  const skull = mesh(sph(0.36), skin); skull.scale.set(1, 0.96, 0.92); head.add(skull);
  for (const s of [-1, 1]) at(mesh(sph(0.07), skin), s * 0.35, 0, 0, head);
  // fluffy brown hair
  const hairCol = '#7a4a24'; const pts = [];
  for (let i = 0; i < 26; i++) {
    const a = (i / 26) * PI * 2, ring = i % 2;
    pts.push([Math.cos(a) * 0.3, 0.2 + ring * 0.08 + 0.05 * Math.sin(a * 3), Math.sin(a) * 0.27 - 0.03]);
  }
  pts.push([0, 0.36, 0], [0.12, 0.34, 0.1], [-0.12, 0.34, 0.1], [0, 0.3, 0.2], [0.16, 0.26, 0.2], [-0.16, 0.26, 0.2], [0, 0.32, -0.15]);
  for (const [x, y, z] of pts) { if (z > 0.22 && y < 0.25) continue; at(mesh(sph(0.115, 16, 12), hairCol, { outline: 0.02 }), x, y, z, head); }
  const f = face(head, { eyeX: 0.13, eyeY: 0.02, eyeZ: 0.3, eyeR: 0.085, mouthY: -0.17, skinD: '#c8926c' });
  // glasses
  for (const s of [-1, 1]) { const g = mesh(new THREE.TorusGeometry(0.105, 0.016, 10, 32), '#2b2d42', { outline: 0 }); at(g, s * 0.13, 0.02, 0.37, head); }
  const br = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.06), '#2b2d42', { outline: 0 }); br.rotation.z = PI / 2; at(br, 0, 0.04, 0.38, head);
  k.face = f; k.name = 'tinku'; return k;
}
function makePinky() {
  const k = kidBase({ scale: 0.95 }); const b = k.body; const skin = '#e9b48a';
  for (const s of [-1, 1]) {
    at(mesh(cap(0.06, 0.3), skin), s * 0.09, 0.26, 0, b);
    const shoe = mesh(sph(0.09), '#ff4f8b'); shoe.scale.set(0.9, 0.55, 1.3); at(shoe, s * 0.09, 0.05, 0.04, b);
  }
  const dress = mesh(new THREE.CylinderGeometry(0.16, 0.36, 0.5, 32), '#ff7ab0'); at(dress, 0, 0.62, 0, b); dress.scale.z = 0.85;
  const hem = mesh(new THREE.TorusGeometry(0.355, 0.022, 8, 40), '#ffffff', { outline: 0 }); hem.rotation.x = PI / 2; hem.scale.y = 0.85; at(hem, 0, 0.38, 0, b);
  for (let i = 0; i < 7; i++) { const a = -0.9 + i * 0.3; at(mesh(sph(0.025), '#ffffff', { outline: 0 }), Math.sin(a) * 0.27, 0.5 + (i % 2) * 0.1, Math.cos(a) * 0.24, b); }
  const torso = mesh(cap(0.16, 0.12), '#ff7ab0'); at(torso, 0, 0.86, 0, b);
  k.arms = [arm(b, -1, 0.19, 0.92, '#ff7ab0', skin, 0.46, 0.055), arm(b, 1, 0.19, 0.92, '#ff7ab0', skin, 0.46, 0.055)];
  const head = new THREE.Group(); at(head, 0, 1.3, 0, b); k.head = head;
  const skull = mesh(sph(0.35), skin); skull.scale.set(1, 0.98, 0.92); head.add(skull);
  for (const s of [-1, 1]) at(mesh(sph(0.065), skin), s * 0.34, 0, 0, head);
  const hair = '#2a1610';
  const capg = new THREE.SphereGeometry(0.37, 32, 16, 0, PI * 2, 0, PI * 0.47); const hc = mesh(capg, hair); hc.rotation.x = -0.35; hc.scale.set(1, 1, 0.95); at(hc, 0, 0.03, -0.02, head);
  const fringe = mesh(sph(0.2), hair); fringe.scale.set(1.5, 0.45, 0.8); at(fringe, 0.03, 0.27, 0.16, head);
  k.tails = [];
  for (const s of [-1, 1]) {
    const tg = new THREE.Group(); at(tg, s * 0.36, 0.12, -0.05, head);
    const tail = mesh(sph(0.12), hair); tail.scale.set(0.8, 1.6, 0.8); at(tail, s * 0.08, -0.16, 0, tg);
    const tie = mesh(sph(0.055), '#ffd23f'); at(tie, 0, 0, 0, tg);
    k.tails.push(tg);
  }
  for (let i = 0; i < 5; i++) { const a = i * PI * 2 / 5; at(mesh(sph(0.03), '#ff4f8b', { outline: 0 }), -0.17 + Math.cos(a) * 0.04, 0.3 + Math.sin(a) * 0.04, 0.24, head); }
  at(mesh(sph(0.022), '#ffffff', { outline: 0 }), -0.17, 0.3, 0.26, head);
  at(mesh(sph(0.018), '#d81b60', { outline: 0 }), 0, 0.14, 0.33, head);
  k.face = face(head, { eyeX: 0.13, eyeY: 0.03, eyeZ: 0.29, eyeR: 0.085, mouthY: -0.16, skinD: '#c48a62', lashes: true, iris: '#4a2a14' });
  k.name = 'pinky'; return k;
}
function makeGolu() {
  const k = kidBase({ scale: 0.84 }); const b = k.body; const skin = '#d9a074';
  for (const s of [-1, 1]) {
    at(mesh(cap(0.09, 0.2), '#3fae4a'), s * 0.11, 0.22, 0, b);
    const shoe = mesh(sph(0.1), '#2f7bff'); shoe.scale.set(0.95, 0.55, 1.3); at(shoe, s * 0.11, 0.05, 0.05, b);
  }
  const tee = mesh(sph(0.3), '#ff9f1a'); tee.scale.set(1, 1.05, 0.85); at(tee, 0, 0.66, 0, b);
  const dung = mesh(new THREE.CylinderGeometry(0.29, 0.27, 0.32, 32), '#3fae4a'); dung.scale.z = 0.85; at(dung, 0, 0.5, 0, b);
  const bib = mesh(new THREE.BoxGeometry(0.26, 0.2, 0.05), '#3fae4a'); at(bib, 0, 0.72, 0.23, b);
  const pocket = mesh(new THREE.BoxGeometry(0.12, 0.08, 0.02), '#5fcf6a', { outline: 0.01 }); at(pocket, 0, 0.7, 0.26, b);
  for (const s of [-1, 1]) {
    const st = mesh(new THREE.BoxGeometry(0.05, 0.3, 0.04), '#3fae4a', { outline: 0.01 }); st.rotation.z = s * 0.15; at(st, s * 0.12, 0.88, 0.2, b);
    at(mesh(sph(0.025), '#ffd23f', { outline: 0 }), s * 0.11, 0.8, 0.26, b);
  }
  k.arms = [arm(b, -1, 0.28, 0.82, '#ff9f1a', skin, 0.42, 0.07), arm(b, 1, 0.28, 0.82, '#ff9f1a', skin, 0.42, 0.07)];
  const head = new THREE.Group(); at(head, 0, 1.25, 0, b); k.head = head;
  const skull = mesh(sph(0.4), skin); skull.scale.set(1.04, 0.96, 0.92); head.add(skull);
  for (const s of [-1, 1]) at(mesh(sph(0.075), skin), s * 0.4, 0, 0, head);
  const capg = new THREE.SphereGeometry(0.41, 32, 16, 0, PI * 2, 0, PI * 0.36); const hc = mesh(capg, '#2a1a12'); hc.rotation.x = -0.45; at(hc, 0, 0.02, -0.03, head);
  const tuft = mesh(sph(0.07), '#2a1a12'); tuft.scale.set(0.6, 1.5, 0.6); tuft.rotation.z = -0.4; at(tuft, 0.02, 0.43, 0.05, head);
  k.face = face(head, { eyeX: 0.14, eyeY: 0.0, eyeZ: 0.33, eyeR: 0.09, mouthY: -0.2, skinD: '#b07a50' });
  k.name = 'golu'; return k;
}
function makeMoti() {
  const k = kidBase({ scale: 0.95 }); const b = k.body; const fur = '#f3dfbf', ear = '#a8673a';
  const torso = mesh(sph(0.3), fur); torso.scale.set(0.85, 0.75, 1.25); at(torso, 0, 0.38, 0, b);
  const spot = mesh(sph(0.12), '#d8a878', { outline: 0 }); spot.scale.set(1, 0.6, 1); at(spot, 0.12, 0.55, -0.12, b);
  for (const [x, z] of [[-0.14, 0.2], [0.14, 0.2], [-0.14, -0.22], [0.14, -0.22]]) {
    at(mesh(cap(0.065, 0.14), fur), x, 0.15, z, b);
    const paw = mesh(sph(0.075), '#fff2dc'); paw.scale.set(1, 0.6, 1.2); at(paw, x, 0.04, z + 0.03, b);
  }
  const tail = new THREE.Group(); at(tail, 0, 0.5, -0.36, b);
  const tm = mesh(cap(0.05, 0.15), fur); tm.rotation.x = -0.7; at(tm, 0, 0.08, -0.06, tail); k.tail = tail;
  const collar = mesh(new THREE.TorusGeometry(0.17, 0.035, 10, 28), '#e8322f', { outline: 0 }); collar.rotation.x = PI / 2 - 0.5; at(collar, 0, 0.62, 0.26, b);
  at(mesh(sph(0.045), '#ffd23f'), 0, 0.53, 0.42, b);
  const head = new THREE.Group(); at(head, 0, 0.82, 0.32, b); k.head = head;
  const skull = mesh(sph(0.27), fur); head.add(skull);
  const snout = mesh(sph(0.15), '#fff2dc'); snout.scale.set(1.1, 0.8, 0.9); at(snout, 0, -0.08, 0.2, head);
  const nose = mesh(sph(0.05), '#2b1b14'); nose.scale.set(1.2, 0.8, 0.8); at(nose, 0, -0.03, 0.34, head);
  k.ears = [];
  for (const s of [-1, 1]) {
    const eg = new THREE.Group(); at(eg, s * 0.22, 0.12, 0, head);
    const e = mesh(sph(0.11), ear); e.scale.set(0.55, 1.4, 0.8); at(e, s * 0.04, -0.14, 0, eg); k.ears.push(eg);
  }
  k.face = face(head, { eyeX: 0.1, eyeY: 0.06, eyeZ: 0.21, eyeR: 0.07, mouthY: -0.17, skinD: '#2b1b14', iris: '#2a1a10' });
  k.face.open.position.z = 0.27; k.face.smile.position.z = 0.29;
  k.name = 'moti'; return k;
}

// ---------- world: rainbow meadow
scene.fog = new THREE.Fog('#cfeaff', 30, 90);
const skyGeo = new THREE.SphereGeometry(100, 32, 16);
const skyMat = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: {},
  vertexShader: 'varying vec3 vp; void main(){ vp = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
  fragmentShader: 'varying vec3 vp; void main(){ float h = clamp(normalize(vp).y*1.6, 0.0, 1.0); vec3 top=vec3(0.18,0.55,1.0); vec3 hor=vec3(0.82,0.94,1.0); gl_FragColor = vec4(mix(hor, top, h), 1.0);}' });
scene.add(new THREE.Mesh(skyGeo, skyMat));
const sun = new THREE.Mesh(sph(3.2), new THREE.MeshBasicMaterial({ color: '#fff3a0', fog: false })); sun.position.set(26, 22, -70); scene.add(sun);
const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: radialTex('#fff8c0'), transparent: true, depthWrite: false, fog: false })); glow.scale.set(30, 30, 1); glow.position.copy(sun.position); scene.add(glow);
function radialTex(col) {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 4, 64, 64, 64); gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const hemi = new THREE.HemisphereLight('#dff1ff', '#6fbf4a', 1.6); scene.add(hemi);
const dl = new THREE.DirectionalLight('#fff4dc', 2.6); dl.position.set(6, 10, 7); dl.castShadow = true;
dl.shadow.mapSize.set(2048, 2048); Object.assign(dl.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 }); dl.shadow.bias = -0.0008; dl.shadow.normalBias = 0.045; dl.shadow.radius = 4;
scene.add(dl);
// ground + rolling hills
const ground = new THREE.Mesh(new THREE.PlaneGeometry(220, 220), toon('#7fd45a')); ground.rotation.x = -PI / 2; ground.receiveShadow = true; scene.add(ground);
const rnd = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
for (const [x, z, r, col] of [[-14, -22, 12, '#8fdc66'], [4, -30, 16, '#79cc58'], [20, -24, 12, '#8fdc66'], [-30, -35, 18, '#6fc24e'], [34, -38, 18, '#6fc24e']]) {
  const h = mesh(sph(r, 48, 24), col, { outline: 0 }); h.scale.y = 0.32; at(h, x, -0.5, z, scene); h.castShadow = false;
}
const path = new THREE.Mesh(new THREE.CircleGeometry(4.2, 48), toon('#f0dca8')); path.rotation.x = -PI / 2; path.scale.set(1.25, 0.5, 1); path.position.set(0, 0.01, 0.6); path.receiveShadow = true; scene.add(path);
function tree(x, z, s = 1, leaf = ['#3f9e3f', '#55b84a']) {
  const g = new THREE.Group(); at(g, x, 0, z, scene); g.scale.setScalar(s);
  at(mesh(new THREE.CylinderGeometry(0.16, 0.24, 1.6, 12), '#8a5a2e'), 0, 0.8, 0, g);
  for (const [dx, dy, dz, r] of [[0, 2.1, 0, 0.9], [-0.6, 1.8, 0.2, 0.65], [0.6, 1.8, 0.1, 0.7], [0.1, 2.6, 0.1, 0.6], [0, 1.9, 0.5, 0.6]])
    at(mesh(sph(r, 20, 16), r > 0.68 ? leaf[0] : leaf[1], { outline: 0.03 }), dx, dy, dz, g);
  return g;
}
tree(-6.2, -3.5, 1.3); tree(6.5, -4.2, 1.5); tree(-10, -9, 1.6); tree(11, -10, 1.8); tree(-3.5, -12, 1.2);
for (let i = 0; i < 9; i++) { const bsh = mesh(sph(0.5, 16, 12), i % 2 ? '#4fae44' : '#5fbf4a'); bsh.scale.set(1.3, 0.75, 1); at(bsh, -9 + i * 2.3 + rnd(), 0.2, -6 - rnd() * 2, scene); }
const FL = ['#ff5f8f', '#ffd23f', '#ffffff', '#a04dff', '#ff8c1a', '#2f8bff'];
const flowerHeads = [];
for (let i = 0; i < 70; i++) {
  const x = (rnd() - 0.5) * 22, z = -1.5 - rnd() * 8 + (rnd() < 0.3 ? 5.5 : 0);
  if (Math.abs(x) < 3.2 && z > -2.5) continue;
  const st = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.28), toon('#3f9e3f')); at(st, x, 0.14, z, scene);
  const hd = mesh(sph(0.065, 12, 8), FL[i % FL.length], { outline: 0.012 }); at(hd, x, 0.3, z, scene); flowerHeads.push(hd);
}
const clouds = [];
for (let i = 0; i < 7; i++) {
  const g = new THREE.Group(); at(g, -40 + i * 13 + rnd() * 5, 9 + rnd() * 6, -32 - rnd() * 12, scene);
  for (const [dx, dy, r] of [[0, 0, 1.6], [1.6, 0.4, 1.9], [3.2, 0, 1.5], [1.6, -0.4, 1.4], [0.8, 0.9, 1.2]]) {
    const c = new THREE.Mesh(sph(r, 16, 12), new THREE.MeshToonMaterial({ color: '#ffffff', gradientMap: grad, emissive: '#dfefff', emissiveIntensity: 0.35 })); at(c, dx, dy, 0, g);
  }
  g.userData.sp = 0.3 + rnd() * 0.4; clouds.push(g);
}
// rainbow bands (rebuilt as they grow)
const RAIN = ['#ff3b3b', '#ff8c1a', '#ffd21a', '#2fbf4a', '#2f8bff', '#4b3cc4', '#9b3fd6'];
const RB = { R: 8.6, w: 0.6, z: -15, y: -1.2 };
const bands = RAIN.map((c, i) => {
  const m = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshToonMaterial({ color: c, gradientMap: grad, emissive: c, emissiveIntensity: 0.35, fog: false }));
  m.position.set(0, RB.y, RB.z); scene.add(m); m.userData.p = -1; return m;
});
function setBand(i, p, glow) {
  const m = bands[i]; const pp = Math.round(clamp(p) * 60) / 60;
  if (pp !== m.userData.p) {
    m.geometry.dispose();
    m.geometry = pp > 0 ? new THREE.TorusGeometry(RB.R - i * RB.w, RB.w * 0.5, 10, 96, PI * pp) : new THREE.BufferGeometry();
    m.rotation.z = PI - PI * pp; m.userData.p = pp;
  }
  m.material.emissiveIntensity = 0.35 + 0.9 * glow;
}
// floating colour balls with names
const NAMES_C = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Indigo', 'Violet'];
const balls = RAIN.map((c, i) => {
  const g = new THREE.Group(); scene.add(g);
  g.add(mesh(sph(0.42), c, { outline: 0.03, emissive: 0.2 }));
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 96; const x = cv.getContext('2d');
  x.font = 'bold 54px Fredoka'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineWidth = 10; x.strokeStyle = '#ffffff'; x.strokeText(NAMES_C[i], 128, 50); x.fillStyle = c; x.fillText(NAMES_C[i], 128, 50);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tx, transparent: true, depthTest: false })); sp.scale.set(1.5, 0.56, 1); sp.position.y = -0.72; g.add(sp);
  g.visible = false; return g;
});

// ---------- cast
const kids = [makeTinku(), makePinky(), makeGolu()];
const moti = makeMoti();
const XS = [-1.9, -0.55, 0.75, 2.05];
kids.forEach((k, i) => { k.root.position.set(XS[i], 0, 0.6 + (i === 1 ? 0.15 : 0)); scene.add(k.root); });
moti.root.position.set(XS[3], 0, 0.9); moti.root.rotation.y = -0.5; scene.add(moti.root);

// ---------- audio-driven helpers
function mouth(name, t) { const a = D.mouth[name]; if (!a) return 0; const i = Math.round(t * D.fps); return i >= 0 && i < a.length ? a[i] : 0; }
const blink = (t, off) => ((t + off) % 3.6) < 0.12;
function dance(i, t, kind) {
  const bt = t / B, ph = bt - Math.floor(bt), bi = Math.floor(bt), bar = Math.floor(bi / 4);
  const bounce = Math.pow(Math.sin(PI * ph), 2);
  if (kind === 'intro') return { L: { out: 0.25 }, R: { out: 2.4, bend: 0.5 + 0.5 * Math.sin(t * 9 + i) }, hop: 0.06 * bounce, lean: 0, turn: 0 };
  const move = bar % 4;
  if (move === 0) { const up = bi % 2; return { L: { out: up ? 2.7 : 0.9, bend: up ? 0.2 : 1.2 }, R: { out: up ? 0.9 : 2.7, bend: up ? 1.2 : 0.2 }, hop: 0.08 * bounce, lean: 0, turn: 0 }; }
  if (move === 1) return { L: { out: 0.3 }, R: { out: 2.3, bend: 0.6 + 0.6 * Math.sin(t * 10 + i) }, hop: 0.04 * bounce, lean: 0.12 * Math.sin(PI * bt), turn: 0.25 * Math.sin(PI * bt / 2) };
  if (move === 2) { const clap = ph < 0.3 || (ph >= 0.5 && ph < 0.8); const P = clap ? { out: -0.25, fwd: 1.3, bend: 0 } : { out: 0.15, fwd: 1.1, bend: 0.5 }; return { L: P, R: P, hop: 0.05 * bounce, lean: 0, turn: 0 }; }
  return { L: { out: 2.6, bend: 0.3 }, R: { out: 2.6, bend: 0.3 }, hop: 0.16 * Math.sin(PI * ph), lean: 0, turn: Math.sin(PI * bt / 4) * 0.2 };
}

// ---------- captions overlay
const capEl = document.getElementById('cap'), capName = document.getElementById('capname'), capTxt = document.getElementById('captxt');
function captions(t) {
  let cur = null;
  D.lines.forEach((l, i) => { const nxt = i + 1 < D.lines.length ? D.lines[i + 1].start - 0.25 : 1e9; if (l.start - 0.25 <= t && t <= Math.min(l.end + 0.3, nxt)) cur = l; });
  if (!cur || t < D.introEnd) { capEl.style.opacity = 0; return; }
  capEl.style.opacity = clamp((t - cur.start + 0.25) / 0.15);
  capName.textContent = D.names[cur.spk][0]; capName.style.background = D.names[cur.spk][1]; capEl.style.borderColor = D.names[cur.spk][1];
  capTxt.textContent = cur.cap;
}
const title = document.getElementById('title');

// ---------- frame
window.renderAt = function (t) {
  const bt = t / B, phBar = (bt % 4) / 4;
  const intro = t < D.introEnd;
  // camera: gentle orbit + push-in + downbeat kick
  const lt = t - D.t0;
  const ang = 0.18 * Math.sin(lt * 0.18) - 0.05;
  const dist = intro ? 9.5 - 1.5 * ease(lt / 6) : 7.6 - 0.9 * ease((t - D.introEnd) / 14);
  camera.position.set(Math.sin(ang) * dist, 2.0 + 0.25 * Math.sin(lt * 0.3), Math.cos(ang) * dist + 0.6);
  camera.lookAt(0, intro ? 2.2 : 1.15, 0);
  camera.fov = 34 - 0.8 * Math.exp(-phBar * 10); camera.updateProjectionMatrix();
  // rainbow grows colour by colour as each colour is sung
  RAIN.forEach((c, i) => {
    const tw = D.colorTimes[i];
    const p = intro ? ease((t - D.t0 - 0.5 - i * 0.18) / 0.8) : ease((t - tw + 0.05) / 0.45);
    const g = t >= tw - 0.05 ? Math.exp(-Math.max(0, t - tw) * 2.2) : 0;
    setBand(i, D.firstChorus ? (intro ? p * 0.0 + (t > tw ? 1 : 0) : p) : 1, g);
    const ball = balls[i]; const l = t - tw;
    if (l >= -0.02 && l < 2.6) {
      ball.visible = true; const q = Math.max(0.01, back(l / 0.35));
      ball.scale.setScalar(q * (1 - ease((l - 2.2) / 0.4)) + 0.001);
      ball.position.set(-3.9 + i * 1.3, 2.35 + l * 0.22 + 0.08 * Math.sin(t * 4 + i), -1.0);
    } else ball.visible = false;
  });
  clouds.forEach(g => { g.position.x += 0; g.position.x = ((g.userData.x0 ??= g.position.x) + t * g.userData.sp + 60) % 120 - 60; });
  flowerHeads.forEach((h, i) => { h.position.y = 0.3 + 0.015 * Math.sin(t * 3 + i); });
  // kids
  kids.forEach((k, i) => {
    const d = dance(i, t, intro ? 'intro' : 'chorus');
    setArm(k.arms[0], d.L); setArm(k.arms[1], d.R);
    k.body.position.y = d.hop; k.body.rotation.z = d.lean; k.root.rotation.y = d.turn + (i - 1) * -0.12;
    const m = mouth(k.name, t);
    setFace(k.face, m, blink(t, i * 1.1));
    k.head.rotation.z = 0.05 * Math.sin(t * 2.2 + i) + 0.04 * m; k.head.rotation.x = -0.06 * m;
    k.shadow.scale.setScalar(1 - d.hop * 1.5);
    if (k.tails) k.tails.forEach((tg, s) => tg.rotation.z = (s ? 1 : -1) * (0.25 + 0.15 * Math.sin(PI * bt)));
  });
  const mph = bt % 1;
  moti.body.position.y = 0.12 * Math.pow(Math.sin(PI * mph), 2);
  moti.tail.rotation.y = 0.7 * Math.sin(t * 14);
  moti.ears.forEach((e, s) => e.rotation.z = (s ? 1 : -1) * (0.15 + 0.15 * Math.sin(PI * bt)));
  setFace(moti.face, 0, blink(t, 0.9));
  // title overlay during intro
  title.style.opacity = intro ? clamp((t - D.t0 - 0.3) / 0.4) * (1 - clamp((t - D.introEnd + 0.5) / 0.5)) : 0;
  title.style.transform = `translate(-50%,0) scale(${0.9 + 0.1 * back((t - D.t0 - 0.3) / 0.5) + 0.03 * Math.pow(Math.sin(PI * (bt % 1)), 4)})`;
  captions(t);
  renderer.render(scene, camera);
  return true;
};
window.READY = true;
