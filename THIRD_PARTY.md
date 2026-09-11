# Third-party scenery and decoder

- Default textured 3D capture: AGI headquarters campus, Exton, Pennsylvania. Public sample tileset linked by the [MapLibre 3D Tiles example](https://maplibre.org/maplibre-gl-js/docs/examples/add-3d-tiles-using-threejs/), streamed from `pelican-public.s3.amazonaws.com/3dtiles/agi-hq/`. The capture is not bundled or redistributed in this repository; its attribution is shown in the map. It is a limited-area sample, not worldwide imagery.
- Basemap: [OpenFreeMap](https://openfreemap.org/) / OpenMapTiles / [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). MapLibre displays provider attribution.
- Topographic elevation: [Mapzen terrain tiles through AWS Open Data](https://registry.opendata.aws/terrain-tiles/), with source attribution displayed by the map.
- `public/draco/` contains the Draco WASM decoder and wrapper distributed with Three.js. Draco is Copyright Google Inc., licensed under the [Apache License 2.0](https://github.com/google/draco/blob/main/LICENSE). Decoder files are kept local to avoid an extra runtime CDN dependency.
- Three.js, MapLibre GL JS, and 3D Tiles Renderer retain their licenses in their respective installed packages.
