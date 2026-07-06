import { ControlPanel } from "./components/control-panel";

export default function HomePage() {
  return (
    <main>
      <section className="glass panel" aria-labelledby="header-title">
        <h1 id="header-title">Drone Control Station</h1>
        <p className="subtle">
          Rebuilt as a serverless-ready Next.js app with a glassmorphism interface and live control state endpoint.
        </p>
      </section>
      <ControlPanel />
    </main>
  );
}
