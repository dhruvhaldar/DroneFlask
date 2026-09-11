import test from 'node:test';
import assert from 'node:assert/strict';
import { initialFlight, stepFlight, takeoff } from '../src/flight.ts';
const tick = (s: ReturnType<typeof initialFlight>, seconds: number, keys: string[] = []) => { for (let i = 0; i < seconds * 60; i++) stepFlight(s, new Set(keys), 1 / 60, 'Stabilized', 0); };
test('disarmed drone stays still; takeoff settles into a stable hover', () => {
  const s = initialFlight(); tick(s, 2, ['Space']); assert.equal(s.y, .65);
  takeoff(s); tick(s, 5); assert.ok(Math.abs(s.y - 3) < .1); assert.equal(s.armed, true);
});
test('heading-relative movement, ascent, and braking', () => {
  const s = initialFlight(); takeoff(s); tick(s, 3, ['Space']); assert.ok(s.y > 15);
  s.yaw = Math.PI / 2; tick(s, 1, ['KeyW']); assert.ok(s.x < -5); assert.ok(Math.abs(s.z) < .01);
  tick(s, 3); assert.ok(Math.abs(s.vx) < .01);
});
test('pause freezes all flight state', () => {
  const s = initialFlight(); takeoff(s); s.paused = true; const before = { ...s }; tick(s, 3, ['Space', 'KeyW']); assert.deepEqual(s, before);
});
test('soft landing disarms the motors', () => {
  const s = initialFlight(); takeoff(s); tick(s, 4); s.landing = true; tick(s, 5); assert.equal(s.armed, false); assert.equal(s.y, .65); assert.equal(s.crashed, false);
});
test('hard landing stops flight and reset recovers', () => {
  const s = initialFlight(); takeoff(s); s.y = .7; s.vy = -7; tick(s, .1, ['ShiftLeft']); assert.equal(s.crashed, true); assert.equal(s.armed, false); takeoff(s); assert.equal(s.armed, false); assert.equal(initialFlight().crashed, false);
});
test('ordered gate scoring requires passing through the opening', () => {
  const s = initialFlight(); takeoff(s); s.y = 7; s.z = -29; s.vz = -13; tick(s, .2, ['KeyW']); assert.equal(s.gates, 1);
  s.z = -64; s.x = 10; s.y = 10; tick(s, .2, ['KeyW']); assert.equal(s.gates, 1);
});
test('return home climbs then lands at origin', () => {
  const s = initialFlight(); takeoff(s); s.x = 30; s.z = -40; s.y = 8; s.returning = true; tick(s, 50);
  assert.equal(s.crashed, false); assert.equal(s.armed, false); assert.ok(Math.hypot(s.x, s.z) < 1.5); assert.equal(s.y, .65);
});
test('flight boundary and altitude ceiling stay bounded', () => {
  const s = initialFlight(); takeoff(s); s.x = 244; s.y = 99; tick(s, 5, ['Space', 'KeyD']); assert.ok(s.x <= 245); assert.ok(s.y <= 100);
});
test('low battery engages return home', () => {
  const s = initialFlight(); takeoff(s); s.y = 5; s.x = 20; s.battery = 14; tick(s, .1); assert.equal(s.returning, true);
});
