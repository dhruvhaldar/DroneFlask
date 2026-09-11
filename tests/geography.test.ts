import test from 'node:test';
import assert from 'node:assert/strict';
import { locations, toLngLat } from '../src/geography.ts';
import { earthToLocal } from '../src/reality.ts';
import { Vector3 } from 'three';

test('local east and north movement produce the correct longitude and latitude', () => {
  const origin=locations[0];
  assert.deepEqual(toLngLat(origin,0,0),[origin.lng,origin.lat]);
  assert.ok(toLngLat(origin,100,0)[0] > origin.lng);
  assert.ok(toLngLat(origin,0,-100)[1] > origin.lat);
});
test('earth-centered coordinates align with local east, up, and south axes', () => {
  const transform=earthToLocal({name:'Equator',lng:0,lat:0});
  const zero=new Vector3(6378137,0,0).applyMatrix4(transform);
  assert.ok(zero.length()<1e-6);
  assert.ok(new Vector3(6378147,0,0).applyMatrix4(transform).distanceTo(new Vector3(0,10,0))<1e-6);
  assert.ok(new Vector3(6378137,10,0).applyMatrix4(transform).distanceTo(new Vector3(10,0,0))<1e-6);
  assert.ok(new Vector3(6378137,0,10).applyMatrix4(transform).distanceTo(new Vector3(0,0,-10))<1e-6);
});
