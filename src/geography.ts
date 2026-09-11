export type GeoLocation = { name: string; lng: number; lat: number; tileset?: string };
export const locations: GeoLocation[] = [
  { name: 'Exton campus · 3D capture', lng: -75.59670696255716, lat: 40.03879587543085, tileset: 'https://pelican-public.s3.amazonaws.com/3dtiles/agi-hq/tileset.json' },
  { name: 'Lauterbrunnen · Swiss Alps', lng: 7.9087, lat: 46.5935 },
  { name: 'Yosemite Valley · California', lng: -119.5904, lat: 37.7459 },
  { name: 'Manali · Himalayas', lng: 77.1887, lat: 32.2432 },
];
const R = 6378137;
// Local Three.js coordinates: X east, Y up, Z south. Distances are ground meters.
export function toLngLat(origin: GeoLocation, x: number, z: number): [number, number] {
  return [origin.lng + x / (R * Math.cos(origin.lat * Math.PI / 180)) * 180 / Math.PI,
    origin.lat - z / R * 180 / Math.PI];
}
export const mapStyle = 'https://tiles.openfreemap.org/styles/bright';
export const terrainSource = {
  type: 'raster-dem' as const,
  tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
  tileSize: 256, maxzoom: 15, encoding: 'terrarium' as const,
  attribution: '<a href="https://registry.opendata.aws/terrain-tiles/" target="_blank" rel="noopener">Elevation: Mapzen / AWS Open Data</a>',
};
