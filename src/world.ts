import * as THREE from 'three';
import { RealityCapture } from './reality';
import { Map as GeoMap, Marker, setWorkerUrl, MercatorCoordinate, LngLat, type CustomLayerInterface } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
setWorkerUrl(workerUrl);
import { gates, type CameraMode, type FlightState } from './flight';
import { locations, mapStyle, terrainSource, toLngLat, type GeoLocation } from './geography';

/** A georeferenced Three.js drone layer sharing MapLibre's terrain depth buffer. */
export class FlightWorld {
  scene = new THREE.Scene();
  camera = new THREE.Camera();
  renderer?: THREE.WebGLRenderer;
  map: GeoMap;
  minimap: GeoMap;
  marker: Marker;
  drone = new THREE.Group();
  props: THREE.Group[] = [];
  rings: THREE.Mesh[] = [];
  trail = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xf16c3a }));
  sun = new THREE.DirectionalLight(0xfff2d7, 3);
  ambient = new THREE.HemisphereLight(0xe2f2ff, 0x6b7956, 2.5);
  trailOn = true;
  cameraMode: CameraMode = 'Orbit';
  location = locations[0];
  ready = false;
  groundElevation = 0;
  zoom = 1;
  private trailPoints: THREE.Vector3[] = [];
  private lastTrail = 0;
  private lastMini = 0;
  private currentCamera: CameraMode = 'Orbit';
  private observer: ResizeObserver;
  private onWheel: (e: WheelEvent) => void;
  private orbitPointer?: { x: number; y: number; bearing: number; pitch: number };
  private abort = new AbortController();
  private loadingTimer: ReturnType<typeof setTimeout>;
  private frame = 0;
  private destroyed = false;
  private reality?: RealityCapture;
  private surfaceCache = new globalThis.Map<string, number>();
  private status: (message: string, ready: boolean) => void;

  constructor(private host: HTMLElement, miniHost: HTMLElement, status: (message: string, ready: boolean) => void) {
    this.status = status;
    this.map = new GeoMap({
      container: host, style: mapStyle, center: [this.location.lng, this.location.lat],
      zoom: 17, elevation: 265, pitch: 60, bearing: 20, maxPitch: 85, maxZoom: 23,
      centerClampedToGround: false, interactive: false,
      canvasContextAttributes: { antialias: true, preserveDrawingBuffer: true },
      attributionControl: { compact: false, customAttribution: '<a href="https://maplibre.org/maplibre-gl-js/docs/examples/add-3d-tiles-using-threejs/" target="_blank" rel="noopener">3D capture: AGI HQ sample</a>' },
    });
    this.map.getCanvas().setAttribute('aria-label', '3D topographic map with a keyboard-controlled drone');
    this.minimap = new GeoMap({ container: miniHost, style: mapStyle,
      center: [this.location.lng, this.location.lat], zoom: 13, interactive: false, attributionControl: false });
    const markerElement = document.createElement('div'); markerElement.className = 'geo-drone-marker'; markerElement.textContent = '▲';
    this.marker = new Marker({ element: markerElement, rotationAlignment: 'map' }).setLngLat([this.location.lng, this.location.lat]).addTo(this.minimap);
    this.sun.position.set(60, 100, 30); this.scene.add(this.sun, this.ambient, this.drone, this.trail);
    this.buildDrone();
    gates.forEach(g => {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(4.7, .18, 10, 48), this.material(0xf58049));
      ring.position.set(g.x, g.y, g.z); this.scene.add(ring); this.rings.push(ring);
    });
    this.map.on('style.load', () => {
      this.map.addSource('elevation', terrainSource);
      this.map.addSource('hillshade-dem', terrainSource);
      const firstSymbol = this.map.getStyle().layers.find(l => l.type === 'symbol')?.id;
      this.map.addLayer({ id: 'terrain-hillshade', type: 'hillshade', source: 'hillshade-dem', paint: {
        'hillshade-exaggeration': .4, 'hillshade-shadow-color': '#526653', 'hillshade-highlight-color': '#f5f1d9',
      } }, firstSymbol);
      if (this.map.getLayer('terrain-hillshade')) this.configureScenery();
      this.map.setSky({ 'sky-color': '#b9d9ec', 'horizon-color': '#e4ead9', 'fog-color': '#d5dfce', 'sky-horizon-blend': .6, 'horizon-fog-blend': .5, 'fog-ground-blend': .4 });
      this.map.addLayer(this.flightLayer());
    });
    this.map.on('error', () => {
      this.status(this.ready ? 'Some map tiles could not load. Check your connection.' : 'Map data unavailable. Check your connection, then retry.', this.ready);
    });
    this.map.on('webglcontextlost', () => { this.ready = false; this.status('Graphics context lost. Reload to resume.', false); });
    this.loadingTimer = setTimeout(() => { if (!this.ready) this.status('Map is taking longer to load. Check your connection or retry.', false); }, 20000);
    let viewportHeight = host.clientHeight;
    this.observer = new ResizeObserver(() => {
      const height = host.clientHeight;
      const zoom = this.map.getZoom();
      this.map.resize(); this.minimap.resize();
      // Map zoom is measured in pixels: compensate for height changes to
      // preserve the orbit camera's distance when entering/leaving fullscreen.
      if (height > 0 && viewportHeight > 0 && height !== viewportHeight && this.cameraMode === 'Orbit') {
        this.map.setZoom(zoom + Math.log2(height / viewportHeight));
      }
      if (height > 0) viewportHeight = height;
    });
    this.observer.observe(host); this.observer.observe(miniHost);
    this.onWheel = e => {
      e.preventDefault();
      if (this.cameraMode === 'Orbit') this.map.setZoom(THREE.MathUtils.clamp(this.map.getZoom() - e.deltaY * .002, 10, 20));
      else this.zoom = THREE.MathUtils.clamp(this.zoom + e.deltaY * .001, .5, 8);
    };
    host.addEventListener('wheel', this.onWheel, { passive: false, signal: this.abort.signal });
    host.addEventListener('pointerdown', e => {
      if (this.cameraMode !== 'Orbit' || (e.target as HTMLElement).closest('a,button')) return;
      this.orbitPointer = { x: e.clientX, y: e.clientY, bearing: this.map.getBearing(), pitch: this.map.getPitch() }; host.setPointerCapture(e.pointerId);
    }, { signal: this.abort.signal });
    host.addEventListener('pointermove', e => {
      const p = this.orbitPointer; if (!p) return;
      this.map.jumpTo({ bearing: p.bearing + (e.clientX - p.x) * .3, pitch: THREE.MathUtils.clamp(p.pitch - (e.clientY - p.y) * .2, 0, 85) });
    }, { signal: this.abort.signal });
    for (const event of ['pointerup', 'pointercancel']) host.addEventListener(event, () => { this.orbitPointer = undefined; }, { signal: this.abort.signal });
  }
  private flightLayer(): CustomLayerInterface {
    return {
      id: 'droneverse-flight', type: 'custom', renderingMode: '3d',
      onAdd: (_map, gl) => {
        this.renderer = new THREE.WebGLRenderer({ canvas: this.map.getCanvas(), context: gl, antialias: true });
        this.renderer.autoClear = false;
        this.renderer.toneMapping = THREE.NoToneMapping;
      },
      render: (_gl, args) => {
        if (!this.renderer) return;
        const origin = MercatorCoordinate.fromLngLat([this.location.lng, this.location.lat]);
        const scale = origin.meterInMercatorCoordinateUnits();
        const local = new THREE.Matrix4().makeTranslation(origin.x, origin.y, 0)
          .scale(new THREE.Vector3(scale, -scale, scale)).multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2));
        this.camera.projectionMatrix.fromArray(args.defaultProjectionData.mainMatrix).multiply(local);
        this.reality?.update(args.projectionMatrix, this.camera.projectionMatrix, this.renderer);
        this.renderer.resetState();
        // MapLibre owns the canvas size. Keep Three's viewport in drawing-buffer
        // pixels without resizing the shared canvas (which would clear the map).
        const canvas = this.map.getCanvas();
        this.renderer.setViewport(0, 0, canvas.width, canvas.height);
        this.renderer.render(this.scene, this.camera); if (this.reality) this.map.triggerRepaint();
      },
    };
  }
  start(callback: (time: number) => void) {
    const tick = (time: number) => { if (this.destroyed) return; callback(time); this.frame = requestAnimationFrame(tick); };
    this.frame = requestAnimationFrame(tick);
  }
  private configureScenery() {
    this.reality?.dispose(); this.reality = undefined; this.surfaceCache.clear();
    if (this.location.tileset) {
      this.map.setTerrain(null);
      this.map.setLayoutProperty('terrain-hillshade', 'visibility', 'none');
      this.reality = new RealityCapture(this.location, this.scene, () => this.status('Some 3D capture tiles could not load. Retry if scenery is incomplete.', this.ready), () => this.surfaceCache.clear());
    } else {
      this.map.setTerrain({ source: 'elevation', exaggeration: 1 });
      this.map.setLayoutProperty('terrain-hillshade', 'visibility', 'visible');
    }
  }
  setLocation(location: GeoLocation) {
    this.location = location; this.ready = false; this.groundElevation = 0; this.clearTrail();
    this.status(location.tileset ? 'Loading textured 3D capture…' : 'Loading map and elevation…', false);
    if (this.map.getLayer('terrain-hillshade')) this.configureScenery();
    this.map.jumpTo({ center: [location.lng, location.lat], elevation: location.tileset ? 265 : 0, zoom: location.tileset ? 17 : 14.3, pitch: 60, bearing: 20 });
    this.minimap.jumpTo({ center: [location.lng, location.lat], zoom: 13 });
    this.cameraMode = this.currentCamera = 'Orbit';
  }
  constrainFlight(s: FlightState, previous: {x: number; z: number}) {
    if (!this.reality || !s.armed) return;
    if (this.elevation(s.x, s.z) === null) {
      s.x = previous.x; s.z = previous.z; s.vx = s.vz = 0;
      s.message = 'Edge of loaded 3D capture. Turn back or wait for the next tiles.';
    }
  }
  coordinates(x: number, z: number) { return toLngLat(this.location, x, z); }
  private elevation(x: number, z: number): number | null {
    if (this.reality) {
      const key = Math.round(x * 2) + ',' + Math.round(z * 2);
      if (this.surfaceCache.has(key)) return this.surfaceCache.get(key)!;
      const value = this.reality.surface(x, z);
      if (value !== null) { if (this.surfaceCache.size > 3000) this.surfaceCache.clear(); this.surfaceCache.set(key, value); }
      return value ?? this.surfaceCache.get(key) ?? null;
    }
    return this.map.queryTerrainElevation(this.coordinates(x, z));
  }
  setNight(night: boolean) {
    this.ambient.intensity = night ? .9 : 2.5; this.sun.intensity = night ? .7 : 3;
    if (this.map.isStyleLoaded()) this.map.setSky({ 'sky-color': night ? '#273e51' : '#b9d9ec', 'horizon-color': night ? '#546a78' : '#e4ead9', 'fog-color': night ? '#65737c' : '#d5dfce' });
    this.host.classList.toggle('blue-hour', night);
  }
  clearTrail() { this.trailPoints = []; this.lastTrail = 0; this.trail.geometry.dispose(); this.trail.geometry = new THREE.BufferGeometry(); }
  update(s: FlightState, dt: number) {
    if (!this.map.getLayer('droneverse-flight')) return;
    if (!this.reality && !this.ready && !this.map.isSourceLoaded('elevation')) return;
    const ground = this.elevation(s.x, s.z);
    if (ground === null || !Number.isFinite(ground)) return;
    this.groundElevation = ground;
    if (!this.ready) { this.ready = true; clearTimeout(this.loadingTimer); this.status(this.reality ? 'Textured 3D capture ready · Exton campus' : '3D terrain ready · OpenStreetMap + elevation', true); }
    // Recreational terrain-following flight: state.y is local height above the DEM.
    this.drone.position.set(s.x, ground + s.y, s.z);
    this.drone.rotation.set(s.pitch, s.yaw, s.roll, 'YXZ');
    this.props.forEach((p, i) => { if (s.armed && !s.paused) p.rotation.y += dt * (i % 2 ? 1 : -1) * 90; });
    this.rings.forEach((r, i) => {
      r.position.y = (this.elevation(gates[i].x, gates[i].z) ?? ground) + gates[i].y;
      (r.material as THREE.MeshStandardMaterial).color.set(i < s.gates ? 0x67d5a2 : i === s.gates ? 0xff884d : 0xf1e9d4);
    });
    this.trail.visible = this.trailOn;
    if (s.armed && !s.paused && s.elapsed - this.lastTrail > .2) {
      this.lastTrail = s.elapsed; this.trailPoints.push(this.drone.position.clone());
      if (this.trailPoints.length > 1200) this.trailPoints.shift();
      this.trail.geometry.dispose(); this.trail.geometry = new THREE.BufferGeometry().setFromPoints(this.trailPoints);
    }
    this.drone.visible = this.cameraMode !== 'FPV';
    if (this.cameraMode === 'Orbit') {
      if (this.currentCamera !== 'Orbit') this.map.jumpTo({ center: this.coordinates(s.x, s.z), elevation: ground, zoom: this.reality ? 17 : 14.3, pitch: 60 });
      else if (s.armed) this.map.setCenter(this.coordinates(s.x, s.z));
      // Center elevation must match terrain once DEM tiles become available.
      if (!s.armed && Math.abs(this.map.getCenterElevation() - ground) > 1) this.map.jumpTo({ elevation: ground });
    } else {
      const heading = -s.yaw * 180 / Math.PI;
      if (this.cameraMode === 'FPV') {
        this.map.jumpTo(this.map.calculateCameraOptionsFromCameraLngLatAltRotation(this.coordinates(s.x, s.z), ground + s.y + .5, heading, 80, s.roll * 12));
      } else {
        const distance = (this.reality ? 10 : 24) * this.zoom;
        const cx = s.x + distance * Math.sin(s.yaw), cz = s.z + distance * Math.cos(s.yaw);
        const cameraGround = this.elevation(cx, cz) ?? ground;
        const height = Math.max(ground + s.y + (this.reality ? 36 : 14) * this.zoom, cameraGround + 15);
        this.map.jumpTo(this.map.calculateCameraOptionsFromTo(new LngLat(...this.coordinates(cx, cz)), height,
          new LngLat(...this.coordinates(s.x, s.z)), ground + s.y));
      }
    }
    this.currentCamera = this.cameraMode;
    if (performance.now() - this.lastMini > 200) {
      this.lastMini = performance.now(); this.marker.setLngLat(this.coordinates(s.x, s.z)).setRotation(-s.yaw * 180 / Math.PI);
      this.minimap.setCenter(this.coordinates(s.x, s.z));
    }
    this.map.triggerRepaint();
  }
  screenshot() {
    const a = document.createElement('a'); a.download = `droneverse-${Date.now()}.png`; a.href = this.map.getCanvas().toDataURL('image/png'); a.click();
  }
  dispose() {
    this.destroyed = true; cancelAnimationFrame(this.frame); clearTimeout(this.loadingTimer); this.abort.abort(); this.observer.disconnect();
    this.reality?.dispose();
    this.scene.traverse(o => { const mesh = o as THREE.Mesh; mesh.geometry?.dispose();
      if (mesh.material) for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) m.dispose(); });
    this.renderer?.dispose(); this.marker.remove(); this.map.remove(); this.minimap.remove();
  }
  private material(color: number, roughness = .8) { return new THREE.MeshStandardMaterial({ color, roughness }); }
  private box(w: number, h: number, d: number, color: number, x: number, y: number, z: number, parent: THREE.Object3D = this.scene) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), this.material(color));
    m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
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

}
