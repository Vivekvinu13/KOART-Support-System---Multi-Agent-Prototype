import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import * as THREE from 'three';
import './styles.css';

const AGENTS = [
  ['Agent 1', 'Front Door / Triage', '#ff6b00', -3, 0, 0],
  ['Agent 2', 'Support Queue', '#007a78', 0, 1.4, 0],
  ['Agent 3', 'Data Analyst', '#1464c4', 0, -1.4, 0],
  ['Agent 4', 'Solution Architect', '#7a3db8', 3, 0, 0]
];

function Network({ handoffs, active }) {
  const ref = useRef();

  useEffect(() => {
    const el = ref.current;

    const s = new THREE.Scene();

    const c = new THREE.PerspectiveCamera(
      45,
      el.clientWidth / el.clientHeight,
      0.1,
      100
    );

    c.position.z = 9;

    const r = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });

    r.setSize(el.clientWidth, el.clientHeight);
    el.appendChild(r.domElement);

    const g = new THREE.Group();
    s.add(g);

    const nodes = {};

    // -------------------------------------------------
    // Create agent spheres and labels
    // -------------------------------------------------
    AGENTS.forEach(a => {
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(0.58, 28, 28),
        new THREE.MeshStandardMaterial({
          color: a[2],
          emissive: a[2],
          emissiveIntensity: active === a[0] ? 0.6 : 0.12
        })
      );

      m.position.set(a[3], a[4], a[5]);

      g.add(m);

      nodes[a[0]] = m;

      // -------------------------------------------------
      // Create text label using a canvas texture
      // -------------------------------------------------
      const canvas = document.createElement('canvas');

      canvas.width = 512;
      canvas.height = 128;

      const ctx = canvas.getContext('2d');

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Agent name
      ctx.font = 'bold 34px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      ctx.fillStyle = '#ffffff';

      ctx.fillText(
        a[0],
        256,
        38
      );

      // Agent role
      ctx.font = '26px Arial';

      ctx.fillStyle = '#cbd5e1';

      ctx.fillText(
        a[1],
        256,
        82
      );

      const texture = new THREE.CanvasTexture(canvas);

      texture.needsUpdate = true;

      const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: false
      });

      const label = new THREE.Sprite(material);

      label.scale.set(3.1, 0.78, 1);

      // Position label underneath the sphere
      label.position.set(
        a[3],
        a[4] - 0.95,
        a[5]
      );

      g.add(label);
    });

    // -------------------------------------------------
    // Handoff lines
    // -------------------------------------------------
    const lm = new THREE.LineBasicMaterial({
      color: 0x7b8c9b,
      transparent: true,
      opacity: 0.45
    });

    handoffs.forEach(h => {
      if (nodes[h.from] && nodes[h.to]) {
        g.add(
          new THREE.Line(
            new THREE.BufferGeometry().setFromPoints([
              nodes[h.from].position.clone(),
              nodes[h.to].position.clone()
            ]),
            lm
          )
        );
      }
    });

    // -------------------------------------------------
    // Lighting
    // -------------------------------------------------
    g.add(
      new THREE.AmbientLight(
        0xffffff,
        0.8
      )
    );

    // -------------------------------------------------
    // Animation
    // -------------------------------------------------
    let f;

    const loop = () => {
      f = requestAnimationFrame(loop);

      g.rotation.y =
        Math.sin(Date.now() / 3000) * 0.12;

      r.render(s, c);
    };

    loop();

    // -------------------------------------------------
    // Cleanup
    // -------------------------------------------------
    return () => {
      cancelAnimationFrame(f);

      r.dispose();

      if (el.contains(r.domElement)) {
        el.removeChild(r.domElement);
      }
    };
  }, [handoffs, active]);

  return (
    <div
      ref={ref}
      className="network"
    />
  );
}

function App() {
  const [q, setQ] = useState('');
  const [events, setEvents] = useState([]);
  const [active, setActive] = useState('Agent 1');
  const [handoffs, setHandoffs] = useState([]);
  const [final, setFinal] = useState(null);
  const [connected, setConnected] = useState(false);

  const ws = useRef();

  // -------------------------------------------------
  // WebSocket connection
  // -------------------------------------------------
  useEffect(() => {
    const x = new WebSocket(
      `ws://${location.hostname}:8000/ws/chat`
    );

    ws.current = x;

    x.onopen = () => {
      setConnected(true);
    };

    x.onclose = () => {
      setConnected(false);
    };

    x.onmessage = e => {
      const v = JSON.parse(e.data);

      setEvents(z => [...z, v]);

      if (v.agent) {
        setActive(v.agent);
      }

      if (
        v.type === 'route' &&
        v.to !== 'User'
      ) {
        setHandoffs(z => [
          ...z,
          {
            from: v.from,
            to: v.to
          }
        ]);
      }

      if (v.type === 'final') {
        setFinal(v);
      }
    };

    return () => {
      x.close();
    };
  }, []);

  // -------------------------------------------------
  // Send message
  // -------------------------------------------------
  const send = () => {
    if (
      !q.trim() ||
      ws.current?.readyState !== 1
    ) {
      return;
    }

    setEvents([]);
    setHandoffs([]);
    setFinal(null);
    setActive('Agent 1');

    ws.current.send(
      JSON.stringify({
        message: q
      })
    );

    setQ('');
  };

  return (
    <div className="app">

      {/* -------------------------------------------------
          Header
      ------------------------------------------------- */}
      <header>
        <div className="brand">
          <span>🦋</span>

          <div>
            <b>
              KOART <i>2.0</i>
            </b>

            <small>
              SUPPORT SYSTEM
            </small>
          </div>
        </div>

        <div className="status">
          <em
            className={
              connected ? 'on' : ''
            }
          />

          {
            connected
              ? 'Live agent connection'
              : 'Connecting…'
          }
        </div>
      </header>

      <main>

        {/* -------------------------------------------------
            Hero
        ------------------------------------------------- */}
        <section className="hero">

          <div>
            <p className="eyebrow">
              MULTI-AGENT CUSTOMER SUPPORT
            </p>

            <h1>
              Ask KOART Support.
              <br />
              <span>
                Watch the handoff.
              </span>
            </h1>

            <p className="lead">
              Agent 1 receives every ticket,
              then routes support, data, or
              configuration requests to the
              right specialist.
            </p>
          </div>

          <div className="agent-strip">

            {AGENTS.map(a => (
              <div
                key={a[0]}
                className={
                  'pill ' +
                  (
                    active === a[0]
                      ? 'active'
                      : ''
                  )
                }
              >
                <b>{a[0]}</b>

                <small>
                  {a[1]}
                </small>
              </div>
            ))}

          </div>

        </section>

        {/* -------------------------------------------------
            Main Grid
        ------------------------------------------------- */}
        <section className="grid">

          {/* -------------------------------------------------
              Support Conversation
          ------------------------------------------------- */}
          <div className="panel">

            <div className="head">

              <div>
                <b>
                  Support conversation
                </b>

                <small>
                  Grounded in the supplied KOART
                  knowledge base
                </small>
              </div>

              <label>
                MCP + AUTOGEN
              </label>

            </div>

            <div className="messages">

              {!events.length &&
                !final && (
                  <div className="empty">

                    <strong>
                      ✦
                    </strong>

                    <b>
                      Start with a KOART question
                    </b>

                    <small>
                      Try one of these examples.
                    </small>

                    <div>

                      <button
                        onClick={() =>
                          setQ(
                            'How do I access KOART 2.0?'
                          )
                        }
                      >
                        Access KOART
                      </button>

                      <button
                        onClick={() =>
                          setQ(
                            'How do I create a new project in KOART?'
                          )
                        }
                      >
                        Create a project
                      </button>

                      <button
                        onClick={() =>
                          setQ(
                            'What is the average amends for ASP?'
                          )
                        }
                      >
                        ASP average amends
                      </button>

                    </div>

                  </div>
                )
              }

              {events.map((e, i) => {

                if (e.type === 'ticket') {
                  return (
                    <div
                      className="ticket"
                      key={i}
                    >
                      {e.ticket_id}
                    </div>
                  );
                }

                if (
                  e.type ===
                  'agent_message'
                ) {
                  return (
                    <article key={i}>

                      <strong>
                        {e.agent}
                      </strong>

                      <p>
                        {
                          String(e.message)
                            .replace(
                              /ROUTE:\s*\w+\s*$/i,
                              ''
                            )
                            .trim()
                        }
                      </p>

                    </article>
                  );
                }

                if (e.type === 'route') {
                  return (
                    <div
                      className="handoff"
                      key={i}
                    >
                      ↗ Handoff{' '}
                      <b>
                        {e.from}
                      </b>{' '}
                      →{' '}
                      <b>
                        {e.to}
                      </b>
                    </div>
                  );
                }

                return null;
              })}

              {final && (
                <div className="final">

                  <small>
                    {final.agent}
                    {' • '}
                    resolved path
                  </small>

                  <p>
                    {final.answer}
                  </p>

                </div>
              )}

            </div>

            {/* -------------------------------------------------
                Composer
            ------------------------------------------------- */}
            <div className="composer">

              <textarea
                value={q}
                onChange={e =>
                  setQ(e.target.value)
                }
                onKeyDown={e => {
                  if (
                    e.key === 'Enter' &&
                    !e.shiftKey
                  ) {
                    e.preventDefault();
                    send();
                  }
                }}
                placeholder="Describe your KOART question or issue…"
              />

              <button onClick={send}>
                Send ↗
              </button>

            </div>

          </div>

          {/* -------------------------------------------------
              Live Agent Handoffs
          ------------------------------------------------- */}
          <div className="panel">

            <div className="head">

              <div>
                <b>
                  Live agent handoffs
                </b>

                <small>
                  3D orchestration view
                </small>
              </div>

              <label className="live">
                LIVE
              </label>

            </div>

            <Network
              handoffs={handoffs}
              active={active}
            />

            <div className="legend">

              {AGENTS.map(a => (
                <span key={a[0]}>

                  <i
                    style={{
                      background: a[2]
                    }}
                  />

                  {a[0]}

                </span>
              ))}

            </div>

          </div>

        </section>

        {/* -------------------------------------------------
            Request Lifecycle
        ------------------------------------------------- */}
        <section className="arch">

          <p className="eyebrow">
            REQUEST LIFECYCLE
          </p>

          <h2>
            One front door. Specialist handoffs.
          </h2>

          <div className="cards">

            {AGENTS.map((a, i) => (
              <div key={a[0]}>

                <small>
                  0{i + 1}
                </small>

                <h3>
                  {a[0]}
                </h3>

                <b>
                  {a[1]}
                </b>

                <p>
                  {
                    i === 0
                      ? 'Answers basic KB questions and routes the ticket.'
                      : i === 1
                      ? 'Handles support and delivery-process questions.'
                      : i === 2
                      ? 'Answers questions from the workbook and dashboard snapshots.'
                      : 'Scopes configuration/change requests and provides the SA intake form.'
                  }
                </p>

              </div>
            ))}

          </div>

        </section>

      </main>

      {/* -------------------------------------------------
          Footer
      ------------------------------------------------- */}
      <footer>
        KOART Support System • Prototype • Configure{' '}
        <code>
          SOLUTION_ARCHITECT_FORM_URL
        </code>{' '}
        for production.
      </footer>

    </div>
  );
}

createRoot(
  document.getElementById('root')
).render(
  <App />
);