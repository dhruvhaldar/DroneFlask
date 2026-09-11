import * as THREE from 'three';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { TilesRenderer } from '3d-tiles-renderer';
import type { GeoLocation } from './geography';

// Convert Earth-centered mesh coordinates into local east/up/south meters.
export function earthToLocal(origin: GeoLocation): THREE.Matrix4 {
  const lat = origin.lat * Math.PI / 180, lon = origin.lng * Math.PI / 180;
  const a = 6378137, e2 = .00669437999014;
  const n = a / Math.sqrt(1 - e2 * Math.sin(lat) ** 2);
  const center = new THREE.Vector3(n * Math.cos(lat) * Math.cos(lon), n * Math.cos(lat) * Math.sin(lon), n * (1 - e2) * Math.sin(lat));
  const east = new THREE.Vector3(-Math.sin(lon), Math.cos(lon), 0);
  const up = new THREE.Vector3(Math.cos(lat) * Math.cos(lon), Math.cos(lat) * Math.sin(lon), Math.sin(lat));
  const south = new THREE.Vector3(Math.sin(lat) * Math.cos(lon), Math.sin(lat) * Math.sin(lon), -Math.cos(lat));
  return new THREE.Matrix4().set(east.x,east.y,east.z,-east.dot(center), up.x,up.y,up.z,-up.dot(center), south.x,south.y,south.z,-south.dot(center), 0,0,0,1);
}

export class RealityCapture {
  tiles: TilesRenderer;
  camera = new THREE.PerspectiveCamera();
  loaded = false;
  private draco = new DRACOLoader().setDecoderPath(import.meta.env.BASE_URL + 'draco/').setDecoderConfig({ type: 'wasm' }).setWorkerLimit(2);
  private ray = new THREE.Raycaster();
  constructor(origin: GeoLocation, scene: THREE.Scene, onError: () => void, onGeometry: () => void) {
    this.tiles = new TilesRenderer(origin.tileset!);
    this.tiles.group.matrixAutoUpdate = false;
    this.tiles.group.matrix.copy(earthToLocal(origin));
    this.tiles.group.updateMatrixWorld(true);
    this.tiles.errorTarget = 8;
    this.tiles.downloadQueue.maxJobsPerOrigin = 4;
    this.tiles.parseQueue.maxJobs = 2;
    this.tiles.lruCache.maxSize = 160;
    this.tiles.lruCache.minSize = 100;
    this.tiles.lruCache.minBytesSize = 128 * 1024 * 1024;
    this.tiles.lruCache.maxBytesSize = 192 * 1024 * 1024;
    this.tiles.manager.addHandler(/\.gltf$/, new GLTFLoader(this.tiles.manager).setDRACOLoader(this.draco));
    this.tiles.setCamera(this.camera);
    this.tiles.addEventListener('load-model', () => { this.loaded = true; onGeometry(); });
    this.tiles.addEventListener('load-error', onError);
    scene.add(this.tiles.group);
  }
  update(projection: ArrayLike<number>, combined: THREE.Matrix4, renderer: THREE.WebGLRenderer) {
    this.camera.projectionMatrix.fromArray(projection);
    this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert();
    this.camera.matrixWorldInverse.multiplyMatrices(this.camera.projectionMatrixInverse, combined);
    this.camera.matrixWorld.copy(this.camera.matrixWorldInverse).invert();
    this.camera.matrixAutoUpdate = false;
    // The shared canvas is resized by MapLibre, not renderer.setSize().
    // Renderer.getSize() therefore becomes stale after fullscreen or a resize.
    this.tiles.setResolution(this.camera, renderer.domElement.width, renderer.domElement.height);
    this.tiles.group.updateMatrixWorld(true);
    this.tiles.update();
  }
  surface(x: number, z: number): number | null {
    if (!this.loaded) return null;
    this.ray.set(new THREE.Vector3(x, 2000, z), new THREE.Vector3(0, -1, 0));
    const hits = this.ray.intersectObject(this.tiles.group, true);
    return hits[0]?.point.y ?? null;
  }
  dispose() { this.tiles.group.removeFromParent(); this.tiles.dispose(); this.draco.dispose(); }
}




