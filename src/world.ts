import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { gates, obstacles, type CameraMode, type FlightState } from "./flight";

export class FlightWorld {
  scene = new THREE.Scene();
  renderer: THREE.WebGLRenderer;
  camera = new THREE.PerspectiveCamera(55, 1, .1, 1800);
  drone = new THREE.Group();
  controls: OrbitControls;
  props: THREE.Group[] = [];
  rings: THREE.Mesh[] = [];
  sun = new THREE.DirectionalLight(0xfff2d7, 3.1);
  ambient = new THREE.HemisphereLight(0xe2f2ff, 0x6b7956, 2.5);
  trail: THREE.Line;
  trailPoints: THREE.Vector3[] = [];
  trailOn = true;
  cameraMode: CameraMode = "Chase";
  zoom = 1;
  private resize: ResizeObserver;
  private follow = new THREE.Vector3();
  private target = new THREE.Vector3();
  private lastTrail = 0;
  private currentCamera: CameraMode = "Chase";
  private onWheel: (event: WheelEvent) => void;

  constructor(private host: HTMLElement) {
    this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
    this.renderer.domElement.setAttribute("aria-label", "Interactive 3D drone flight environment");
    host.append(this.renderer.domElement);
    this.scene.background = new THREE.Color(0xc0d7dc);
    this.scene.fog = new THREE.FogExp2(0xc0d7dc, .0028);
    this.sun.position.set(60, 100, 30);
    this.sun.castShadow = true;
    Object.assign(this.sun.shadow.camera, { left: -95, right: 95, top: 95, bottom: -95, near: 1, far: 300 });
    this.sun.shadow.mapSize.set(2048, 2048);
    this.sun.shadow.bias = -.0005;
    this.scene.add(this.sun, this.ambient);
    this.buildWorld();
    this.buildDrone();
    this.scene.add(this.drone);
    this.trail = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xf16c3a, transparent: true, opacity: .65 }));
    this.scene.add(this.trail);
    this.camera.position.set(12, 8, 17);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.enabled = false;
    this.controls.maxPolarAngle = Math.PI / 2 - .03;
    this.controls.minDistance = 4; this.controls.maxDistance = 100;
    this.resize = new ResizeObserver(() => {
      const { clientWidth: w, clientHeight: h } = host;
      if (!w || !h) return;
      this.renderer.setSize(w, h); this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    });
    this.resize.observe(host);
    this.onWheel = (e) => {
      if (this.cameraMode !== "Chase") return;
      e.preventDefault(); this.zoom = THREE.MathUtils.clamp(this.zoom + e.deltaY * .001, .5, 2.5);
    };
    host.addEventListener("wheel", this.onWheel, { passive: false });
  }

  private material(color: number, roughness = .8) { return new THREE.MeshStandardMaterial({ color, roughness }); }
  private box(w: number, h: number, d: number, color: number, x: number, y: number, z: number, parent: THREE.Object3D = this.scene) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), this.material(color));
    m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
  }
  private buildWorld() {
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), this.material(0x839a76));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; this.scene.add(floor);
    this.box(54, .12, 290, 0x9baba0, 0, -.01, -100);
    this.box(18, .14, 285, 0x737f79, 0, .02, -100);
    for (let i = 0; i < 25; i++) this.box(.2, .015, 4, 0xd9dfd1, 0, .11, 30 - i * 11);
    for (const x of [-8.5, 8.5]) this.box(.12, .015, 280, 0xcdd2c2, x, .11, -100);
    // Launch platform and its painted landing target.
    const pad = new THREE.Mesh(new THREE.CylinderGeometry(6, 6.5, .22, 64), this.material(0x555e59));
    pad.position.y = .12; pad.receiveShadow = true; this.scene.add(pad);
    const ring = new THREE.Mesh(new THREE.RingGeometry(4.8, 5, 64), new THREE.MeshBasicMaterial({ color: 0xf6dbae, side: THREE.DoubleSide }));
    ring.rotation.x = -Math.PI / 2; ring.position.y = .24; this.scene.add(ring);
    for (const x of [-1.1, 1.1]) this.box(.25, .01, 2.8, 0xf3e6cf, x, .25, 0);
    this.box(2.2, .01, .25, 0xf3e6cf, 0, .25, 0);
    for (const o of obstacles) {
      this.box(o.w, o.h, o.d, 0xadb9ae, o.x, o.h / 2, o.z);
      this.box(o.w + .8, .7, o.d + .8, 0x526562, o.x, o.h, o.z);
      for (let y = 3; y < o.h - 2; y += 4) {
        this.box(o.w - 3, 1.6, .05, 0x657e7c, o.x, y, o.z + o.d / 2 + .02);
        this.box(.05, 1.6, o.d - 3, 0x657e7c, o.x + o.w / 2 + .02, y, o.z);
      }
      this.box(4, 1.3, 5, 0x788d88, o.x + 2, o.h + 1, o.z);
    }
    gates.forEach((g, i) => {
      const r = new THREE.Mesh(new THREE.TorusGeometry(4.7, .18, 10, 64), this.material(i === 0 ? 0xf58049 : 0xf1e9d4));
      r.position.set(g.x, g.y, g.z); r.castShadow = true; this.scene.add(r); this.rings.push(r);
      for (const dx of [-4.7, 4.7]) this.box(.14, g.y, .14, 0x788479, g.x + dx, g.y / 2, g.z);
      const canvas = document.createElement("canvas"); canvas.width = 128; canvas.height = 64;
      const ctx = canvas.getContext("2d")!; ctx.fillStyle = "#263c38"; ctx.fillRect(0, 0, 128, 64);
      ctx.fillStyle = "#ffffff"; ctx.font = "bold 34px monospace"; ctx.textAlign = "center"; ctx.fillText(`0${i + 1}`, 64, 44);
      const label = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas) }));
      label.position.set(g.x, g.y + 5.8, g.z); label.scale.set(2.4, 1.2, 1); this.scene.add(label);
    });
    let seed = 42;
    const rand = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    const treeCount = 180;
    const trunks = new THREE.InstancedMesh(new THREE.CylinderGeometry(.35, .55, 3, 5), this.material(0x746752), treeCount);
    const crowns = new THREE.InstancedMesh(new THREE.ConeGeometry(3, 9, 7), this.material(0x486c56), treeCount);
    const dummy = new THREE.Object3D();
    for (let i = 0; i < treeCount; i++) {
      const x = (rand() > .5 ? 1 : -1) * (120 + rand() * 200), z = rand() * 600 - 350, scale = .6 + rand() * .8;
      dummy.position.set(x, 1.5 * scale, z); dummy.scale.setScalar(scale); dummy.updateMatrix(); trunks.setMatrixAt(i, dummy.matrix);
      dummy.position.y = 6 * scale; dummy.updateMatrix(); crowns.setMatrixAt(i, dummy.matrix);
      crowns.setColorAt(i, new THREE.Color().setHSL(.36, .14 + rand() * .15, .23 + rand() * .12));
    }
    trunks.castShadow = true; crowns.castShadow = true; this.scene.add(trunks, crowns);
    for (let i = 0; i < 22; i++) {
      const x = (i - 11) * 75;
      const mountain = new THREE.Mesh(new THREE.ConeGeometry(80 + rand() * 90, 90 + rand() * 150, 5), this.material(i % 2 ? 0x8ba49b : 0x9bafa5));
      mountain.position.set(x, 20, -430 - rand() * 130); mountain.rotation.y = rand() * 5; this.scene.add(mountain);
    }
    for (let i = 0; i < 16; i++) {
      this.box(.16, 1, .16, 0x5d7167, -27, .5, 25 - i * 17);
      this.box(.35, .15, .35, 0xe8ddad, -27, 1, 25 - i * 17);
    }
    // Airfield windsock.
    this.box(.16, 8, .16, 0xd7dfd4, 15, 4, 8);
    const sock = new THREE.Mesh(new THREE.CylinderGeometry(.48, .2, 2.5, 12), this.material(0xf08048));
    sock.rotation.z = Math.PI / 2; sock.position.set(16.2, 7.8, 8); this.scene.add(sock);
  }

  private buildDrone() {
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(.53, .55, 6, 12), this.material(0xe4e8e3)); this.drone.add(body); body.castShadow = true;
    body.rotation.x = Math.PI / 2;
    this.box(.72, .12, 1.05, 0x283833, 0, .35, .1, this.drone);
    for (const x of [-1, 1]) for (const z of [-1, 1]) {
      const arm = this.box(1.8, .13, .22, 0x46534d, x * .85, 0, z * .8, this.drone);
      arm.rotation.y = -x * z * .7;
      const motor = new THREE.Mesh(new THREE.CylinderGeometry(.23, .22, .3, 16), this.material(0x202e29));
      motor.position.set(x * 1.5, .1, z * 1.4); this.drone.add(motor);
      const prop = new THREE.Group(); prop.position.set(x * 1.5, .29, z * 1.4);
      this.box(1.9, .035, .13, 0x2b3832, 0, 0, 0, prop);
      this.box(.13, .035, 1.9, 0x2b3832, 0, 0, 0, prop);
      this.drone.add(prop); this.props.push(prop);
      const light = new THREE.Mesh(new THREE.SphereGeometry(.08, 8, 8), new THREE.MeshBasicMaterial({ color: z < 0 ? 0x8affbb : 0xff644c }));
      light.position.set(x * 1.5, .05, z * 1.6); this.drone.add(light);
      this.box(.08, .45, .08, 0x3d4842, x * .7, -.32, z * .55, this.drone);
    }
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(.19, .19, .24, 20), this.material(0x192c2a, .15));
    lens.rotation.x = Math.PI / 2; lens.position.set(0, -.17, -.9); this.drone.add(lens);
  }

  setNight(night: boolean) {
    const color = night ? 0x273e51 : 0xc0d7dc;
    this.scene.background = new THREE.Color(color); (this.scene.fog as THREE.FogExp2).color.set(color);
    this.ambient.intensity = night ? .8 : 2.5; this.sun.intensity = night ? .65 : 3.1;
    this.sun.color.set(night ? 0x9ecbff : 0xfff2d7);
  }
  clearTrail() { this.trailPoints = []; this.trail.geometry.dispose(); this.trail.geometry = new THREE.BufferGeometry(); }
  update(s: FlightState, dt: number) {
    this.drone.position.set(s.x, s.y, s.z);
    this.drone.rotation.set(s.pitch, s.yaw, s.roll, "YXZ");
    this.props.forEach((p, i) => { if (s.armed && !s.paused) p.rotation.y += dt * (i % 2 ? 1 : -1) * 90; });
    this.rings.forEach((r, i) => (r.material as THREE.MeshStandardMaterial).color.set(i < s.gates ? 0x67d5a2 : i === s.gates ? 0xff884d : 0xf1e9d4));
    this.trail.visible = this.trailOn;
    if (s.armed && !s.paused && s.elapsed - this.lastTrail > .15) {
      this.lastTrail = s.elapsed; this.trailPoints.push(new THREE.Vector3(s.x, s.y, s.z));
      if (this.trailPoints.length > 1200) this.trailPoints.shift();
      this.trail.geometry.dispose(); this.trail.geometry = new THREE.BufferGeometry().setFromPoints(this.trailPoints);
    }
    if (s.elapsed < this.lastTrail) this.lastTrail = 0;
    this.drone.visible = this.cameraMode !== "FPV";
    this.controls.enabled = this.cameraMode === "Orbit";
    this.target.set(s.x, s.y + .5, s.z);
    if (this.cameraMode === "Orbit") {
      if (this.currentCamera !== "Orbit") this.camera.position.set(s.x + 14, s.y + 10, s.z + 14);
      this.controls.target.copy(this.target); this.controls.update();
    } else if (this.cameraMode === "FPV") {
      this.camera.position.set(s.x - Math.sin(s.yaw), s.y + .25, s.z - Math.cos(s.yaw));
      this.camera.lookAt(s.x - Math.sin(s.yaw) * 50, s.y + s.pitch * 30, s.z - Math.cos(s.yaw) * 50);
      this.camera.rotateZ(s.roll * .5);
    } else {
      this.follow.set(s.x + (6 * Math.cos(s.yaw) + 12 * Math.sin(s.yaw)) * this.zoom, s.y + 6 * this.zoom, s.z + (12 * Math.cos(s.yaw) - 6 * Math.sin(s.yaw)) * this.zoom);
      this.camera.position.lerp(this.follow, this.currentCamera !== "Chase" ? 1 : 1 - Math.exp(-dt * 3));
      this.target.y += 1; this.target.z -= 2; this.camera.lookAt(this.target);
    }
    this.currentCamera = this.cameraMode;
    this.renderer.render(this.scene, this.camera);
  }
  screenshot() {
    const link = document.createElement("a"); link.download = `droneverse-${Date.now()}.png`; link.href = this.renderer.domElement.toDataURL("image/png"); link.click();
  }
  dispose() {
    this.renderer.setAnimationLoop(null); this.resize.disconnect(); this.controls.dispose();
    this.host.removeEventListener("wheel", this.onWheel);
    this.scene.traverse(o => {
      const mesh = o as THREE.Mesh;
      mesh.geometry?.dispose();
      if (mesh.material) for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
        const map = (m as THREE.MeshStandardMaterial).map; map?.dispose(); m.dispose();
      }
    });
    this.renderer.dispose(); this.renderer.domElement.remove();
  }
}


