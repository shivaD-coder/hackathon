"""Run a local, Python-powered student hackathon website."""

from __future__ import annotations

import json
import re
import webbrowser
from email.utils import parseaddr
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_SIZE = 16_384

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Join your campus hackathon and build something meaningful with fellow students.">
  <title>Build Together — Campus Hackathon</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17241d;
      --muted: #64736a;
      --paper: #f7f8f2;
      --white: #fffefa;
      --green: #214f3a;
      --green-dark: #183c2b;
      --lime: #d7f36a;
      --orange: #ef8056;
      --line: #e2e8de;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    a { color: inherit; text-decoration: none; }
    button, input, select { font: inherit; }
    .shell { width: min(1120px, calc(100% - 44px)); margin: 0 auto; }
    .topbar {
      display: flex;
      min-height: 78px;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 800; letter-spacing: -.04em; }
    .brand-mark {
      display: grid;
      width: 34px;
      height: 34px;
      place-items: center;
      border-radius: 11px;
      background: var(--green);
      color: var(--lime);
      font-size: 18px;
    }
    nav { display: flex; align-items: center; gap: 28px; color: var(--muted); font-size: 12px; font-weight: 650; }
    nav a:hover, .plain-link:hover { color: var(--green); }
    nav .nav-cta { padding: 11px 16px; border-radius: 99px; background: var(--green); color: white; }
    .hero { display: grid; grid-template-columns: 1.05fr .95fr; gap: 42px; align-items: center; padding: 72px 0 52px; }
    .eyebrow { color: var(--green); font-size: 10px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
    .eyebrow::before { display: inline-block; width: 8px; height: 8px; margin-right: 8px; border-radius: 50%; background: var(--orange); content: ""; }
    h1 { margin: 20px 0 18px; font-size: clamp(48px, 7vw, 76px); line-height: .98; letter-spacing: -.075em; }
    h1 span { color: var(--green); }
    .intro { max-width: 470px; color: var(--muted); font-size: 15px; line-height: 1.75; }
    .actions { display: flex; align-items: center; gap: 20px; margin-top: 26px; }
    .button {
      display: inline-flex;
      min-height: 46px;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 0 20px;
      border: 0;
      border-radius: 99px;
      background: var(--green);
      color: white;
      cursor: pointer;
      font-size: 12px;
      font-weight: 750;
    }
    .button:hover { background: var(--green-dark); }
    .plain-link { color: var(--muted); font-size: 12px; font-weight: 700; }
    .art {
      position: relative;
      display: grid;
      min-height: 350px;
      overflow: hidden;
      place-items: center;
      border-radius: 25px;
      background-color: #e7eddc;
      background-image: linear-gradient(#becbb7 1px, transparent 1px), linear-gradient(90deg, #becbb7 1px, transparent 1px);
      background-size: 34px 34px;
    }
    .sun { position: absolute; top: 42px; right: 48px; width: 67px; height: 67px; border-radius: 50%; background: var(--lime); }
    .orbit { position: absolute; width: 300px; height: 300px; border: 1px solid #214f3a40; border-radius: 50%; transform: rotate(-24deg) scaleY(.53); }
    .orbit.two { width: 360px; height: 360px; transform: rotate(38deg) scaleY(.53); }
    .idea-card {
      position: relative;
      z-index: 1;
      display: flex;
      width: min(290px, 78%);
      min-height: 205px;
      flex-direction: column;
      justify-content: space-between;
      padding: 23px;
      border: 1px solid #ffffff99;
      border-radius: 20px;
      background: #fffefaeb;
      box-shadow: 0 22px 55px #23432d24;
      transform: rotate(-5deg);
    }
    .card-top { display: flex; justify-content: space-between; }
    .spark { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 13px; background: var(--green); color: var(--lime); font-size: 22px; }
    .tag { align-self: flex-start; padding: 6px 9px; border-radius: 99px; background: #edf2e8; color: var(--green); font-size: 9px; font-weight: 800; text-transform: uppercase; }
    .idea-card strong { font-size: 24px; letter-spacing: -.06em; }
    .idea-card small { display: block; margin-top: 5px; color: var(--muted); font-size: 10px; line-height: 1.5; }
    .sticky-note { position: absolute; right: 8%; bottom: 17%; z-index: 2; padding: 11px 13px; border-radius: 12px; background: var(--orange); font-size: 10px; font-weight: 800; transform: rotate(5deg); }
    .facts { display: grid; grid-template-columns: repeat(3, 1fr); margin: 0 auto 72px; padding: 20px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .fact { padding: 3px 25px; border-right: 1px solid var(--line); }
    .fact:first-child { padding-left: 0; }
    .fact:last-child { border: 0; }
    .fact-label { display: block; margin-bottom: 7px; color: var(--muted); font-size: 9px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .fact strong { font-size: 13px; }
    .section-heading { max-width: 600px; margin-bottom: 25px; }
    h2 { margin: 12px 0; font-size: clamp(32px, 4vw, 45px); line-height: 1.06; letter-spacing: -.065em; }
    .section-heading p { color: var(--muted); font-size: 13px; line-height: 1.7; }
    .experience { padding-bottom: 76px; }
    .steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
    .step { min-height: 175px; padding: 22px; border: 1px solid var(--line); border-radius: 17px; background: var(--white); }
    .number { display: grid; width: 32px; height: 32px; place-items: center; border-radius: 11px; background: #edf2e8; color: var(--green); font-size: 11px; font-weight: 800; }
    .step h3 { margin: 19px 0 8px; font-size: 16px; letter-spacing: -.04em; }
    .step p { margin: 0; color: var(--muted); font-size: 11px; line-height: 1.65; }
    .register {
      display: grid;
      grid-template-columns: .9fr 1.1fr;
      gap: 42px;
      align-items: start;
      margin-bottom: 72px;
      padding: 40px;
      border-radius: 24px;
      background: var(--green);
      color: white;
    }
    .register .eyebrow { color: var(--lime); }
    .register-copy h2 { max-width: 400px; margin: 16px 0; font-size: clamp(34px, 4vw, 48px); }
    .register-copy p { max-width: 350px; color: #d0ddd3; font-size: 12px; line-height: 1.75; }
    .note { margin-top: 23px; color: #dce8df; font-size: 10px; line-height: 1.6; }
    .form-card { padding: 24px; border-radius: 18px; background: var(--white); color: var(--ink); }
    .form-card h3 { margin: 0 0 5px; font-size: 18px; letter-spacing: -.04em; }
    .form-intro { margin: 0 0 19px; color: var(--muted); font-size: 10px; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 13px 11px; }
    .field { display: flex; min-width: 0; flex-direction: column; gap: 6px; }
    .field.full { grid-column: 1 / -1; }
    label { color: #3a4a40; font-size: 10px; font-weight: 700; }
    input, select { width: 100%; min-height: 41px; padding: 0 10px; border: 1px solid #dfe5dc; border-radius: 9px; outline: none; background: white; color: var(--ink); font-size: 11px; }
    input:focus, select:focus { border-color: var(--green); box-shadow: 0 0 0 3px #214f3a19; }
    .submit { width: 100%; margin-top: 16px; }
    .privacy { margin: 10px 0 0; color: #7a887f; font-size: 9px; line-height: 1.5; text-align: center; }
    .message { display: none; margin-top: 12px; padding: 11px; border-radius: 9px; background: #edf5e9; color: var(--green-dark); font-size: 11px; line-height: 1.5; }
    .message.visible { display: block; }
    .student-login { display: grid; grid-template-columns: .9fr 1.1fr; gap: 32px; align-items: center; margin: 0 auto 72px; padding: 28px 32px; border: 1px solid var(--line); border-radius: 18px; background: var(--white); }
    .student-login h2 { margin: 12px 0; }
    .student-login-copy p { margin: 0; color: var(--muted); font-size: 12px; line-height: 1.7; }
    .login-form { display: grid; gap: 12px; }
    .login-options { display: flex; align-items: center; }
    .login-toggle { display: inline-flex; align-items: center; gap: 7px; color: var(--muted); font-size: 10px; font-weight: 600; }
    .login-toggle input { width: 15px; min-height: 15px; margin: 0; accent-color: var(--green); }
    .login-form .submit { margin-top: 0; }
    .login-message { margin-top: 0; }
    .faq { display: grid; grid-template-columns: .8fr 1.2fr; gap: 48px; padding-bottom: 70px; }
    .faq .section-heading { margin: 0; }
    .faq-list { border-top: 1px solid var(--line); }
    details { border-bottom: 1px solid var(--line); }
    summary { padding: 16px 0; cursor: pointer; font-size: 12px; font-weight: 700; list-style: none; }
    summary::-webkit-details-marker { display: none; }
    summary::after { float: right; color: var(--green); content: "+"; font-size: 17px; font-weight: 400; }
    details[open] summary::after { content: "−"; }
    details p { margin: -3px 0 16px; color: var(--muted); font-size: 11px; line-height: 1.7; }
    footer { border-top: 1px solid var(--line); }
    .footer { display: flex; min-height: 70px; align-items: center; justify-content: space-between; gap: 18px; color: var(--muted); font-size: 10px; }
    .footer strong { color: var(--ink); }
    @media (max-width: 760px) {
      .hero { grid-template-columns: 1fr; gap: 30px; padding-top: 52px; }
      .art { min-height: 310px; }
      .register { grid-template-columns: 1fr; gap: 24px; padding: 30px; }
      .student-login { grid-template-columns: 1fr; gap: 18px; }
      .faq { grid-template-columns: 1fr; gap: 20px; }
    }
    @media (max-width: 540px) {
      .shell { width: calc(100% - 32px); }
      .topbar { min-height: 68px; }
      nav { gap: 13px; font-size: 11px; }
      nav a:not(.nav-cta) { display: none; }
      nav .nav-cta { padding: 10px 13px; }
      .hero { padding: 42px 0 35px; }
      h1 { font-size: clamp(46px, 14vw, 64px); }
      .intro { font-size: 13px; }
      .facts { grid-template-columns: 1fr; margin-bottom: 52px; }
      .fact, .fact:first-child { padding: 13px 0; border-right: 0; border-bottom: 1px solid var(--line); }
      .fact:last-child { border-bottom: 0; }
      .steps { grid-template-columns: 1fr; }
      .step { min-height: 150px; }
      .experience { padding-bottom: 54px; }
      .register { margin-bottom: 53px; padding: 24px 16px; }
      .student-login { margin-bottom: 52px; padding: 22px 16px; }
      .form-card { padding: 19px 15px; }
      .form-grid { grid-template-columns: 1fr; }
      .field.full { grid-column: auto; }
      .faq { padding-bottom: 50px; }
      .footer { align-items: flex-start; flex-direction: column; justify-content: center; gap: 7px; }
    }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
  </style>
</head>
<body>
  <header class="shell topbar">
    <a class="brand" href="#" aria-label="Build Together home"><span class="brand-mark" aria-hidden="true">✳</span> BUILD TOGETHER</a>
    <nav aria-label="Main navigation">
      <a href="#about">The event</a>
      <a href="#faq">FAQs</a>
      <a class="nav-cta" href="#student-login">Student login ↗</a>
    </nav>
  </header>
  <main>
    <section class="shell hero" aria-labelledby="hero-title">
      <div>
        <div class="eyebrow">Campus-only hackathon</div>
        <h1 id="hero-title">Big ideas.<br><span>Built together.</span></h1>
        <p class="intro">Bring a curious mind and make something that matters. Team up with fellow students, learn by doing, and turn a challenge into a working idea.</p>
        <div class="actions">
          <a class="button" href="#register">Save your spot ↗</a>
          <a class="plain-link" href="#about">See how it works ↓</a>
        </div>
      </div>
      <div class="art" role="img" aria-label="Creative project card illustration">
        <div class="sun"></div><div class="orbit"></div><div class="orbit two"></div>
        <div class="idea-card">
          <div class="card-top"><span class="spark">✳</span><span class="tag">Make it real</span></div>
          <div><strong>Ideas in motion.</strong><small>One team. One challenge. A whole lot of possibility.</small></div>
        </div>
        <div class="sticky-note">YOUR IDEA STARTS HERE ↗</div>
      </div>
    </section>
    <section class="shell student-login" id="student-login" aria-labelledby="login-title">
      <div class="student-login-copy">
        <div class="eyebrow">Student access</div>
        <h2 id="login-title">Welcome back.</h2>
        <p>Use your student email or ID to sign in to the campus portal.</p>
      </div>
      <form class="login-form" id="login-form">
        <div class="field">
          <label for="login-username">Student email or ID</label>
          <input id="login-username" name="username" type="text" autocomplete="username" maxlength="200" placeholder="you@school.edu or student ID" required>
        </div>
        <div class="field">
          <label for="login-password">Password</label>
          <input id="login-password" name="password" type="password" autocomplete="current-password" required>
        </div>
        <div class="login-options">
          <label class="login-toggle"><input id="show-password" type="checkbox"> Show password</label>
        </div>
        <button class="button submit" type="submit">Sign in</button>
        <p class="privacy">Demo only: your password is not sent or saved. School account verification is not connected.</p>
        <div class="message login-message" id="login-message" role="status" aria-live="polite"></div>
      </form>
    </section>
    <section class="shell facts" aria-label="Event information">
      <div class="fact"><span class="fact-label">When</span><strong>Date to be announced</strong></div>
      <div class="fact"><span class="fact-label">Where</span><strong>Campus · Venue to be announced</strong></div>
      <div class="fact"><span class="fact-label">Who can join</span><strong>Students of our institution</strong></div>
    </section>
    <section class="shell experience" id="about">
      <div class="section-heading">
        <div class="eyebrow">The experience</div>
        <h2>More than a competition.</h2>
        <p>No hackathon experience needed. Bring a problem you care about, find your people, and learn as you build.</p>
      </div>
      <div class="steps">
        <article class="step"><span class="number">01</span><h3>Find your challenge</h3><p>Explore real-world themes and choose a problem worth solving.</p></article>
        <article class="step"><span class="number">02</span><h3>Make it together</h3><p>Team up, sketch your idea, and build a demo with mentor support.</p></article>
        <article class="step"><span class="number">03</span><h3>Share what you made</h3><p>Show your prototype, tell its story, and celebrate what you learned.</p></article>
      </div>
    </section>
    <section class="shell register" id="register" aria-labelledby="register-title">
      <div class="register-copy">
        <div class="eyebrow">Registration</div>
        <h2 id="register-title">Make room for your idea.</h2>
        <p>Register your interest with your school email. Event details and next steps will be shared when confirmed.</p>
        <div class="note">✳ &nbsp;Internal event registration is intended for students of this institution.</div>
      </div>
      <form class="form-card" id="registration-form">
        <h3>Join the list</h3>
        <p class="form-intro">Tell us a little about yourself.</p>
        <div class="form-grid">
          <div class="field"><label for="student-name">Full name</label><input id="student-name" name="name" autocomplete="name" maxlength="100" placeholder="Your name" required></div>
          <div class="field"><label for="student-email">School email</label><input id="student-email" name="email" type="email" autocomplete="email" maxlength="200" placeholder="you@school.edu" required></div>
          <div class="field"><label for="department">Department / course</label><input id="department" name="department" maxlength="100" placeholder="e.g. Computer Science" required></div>
          <div class="field"><label for="study-year">Year of study</label><select id="study-year" name="year" required><option value="" selected disabled>Select your year</option><option>1st year</option><option>2nd year</option><option>3rd year</option><option>4th year</option><option>Other</option></select></div>
          <div class="field full"><label for="team-status">Team status</label><select id="team-status" name="team" required><option value="" selected disabled>Choose one</option><option>I have a team</option><option>I'm looking for teammates</option><option>I'd like to join solo</option></select></div>
        </div>
        <button class="button submit" type="submit">Register interest ↗</button>
        <p class="privacy">This local demo validates your details but does not save or send them.</p>
        <div class="message" id="form-message" role="status" aria-live="polite"></div>
      </form>
    </section>
    <section class="shell faq" id="faq">
      <div class="section-heading"><div class="eyebrow">Good to know</div><h2>Questions? Start here.</h2><p>More event details will be shared when they are confirmed.</p></div>
      <div class="faq-list">
        <details><summary>Do I need to know how to code?</summary><p>No. Ideas need designers, researchers, storytellers, and problem-solvers too. Bring your skills and be ready to learn.</p></details>
        <details><summary>Can I register without a team?</summary><p>Yes. Choose “I'm looking for teammates” or “I'd like to join solo” in the form.</p></details>
        <details><summary>When and where will it happen?</summary><p>The event date and venue have not been announced yet. Updates will be shared with interested students.</p></details>
        <details><summary>Does this website store my details?</summary><p>No. This demo validates submissions and returns a confirmation, but does not save or email your information.</p></details>
      </div>
    </section>
  </main>
  <footer><div class="shell footer"><span><strong>BUILD TOGETHER</strong> · A campus hackathon</span><span>Make something meaningful.</span></div></footer>
  <script>
    const form = document.querySelector("#registration-form");
    const message = document.querySelector("#form-message");
    const loginForm = document.querySelector("#login-form");
    const loginPassword = document.querySelector("#login-password");
    const loginMessage = document.querySelector("#login-message");
    document.querySelector("#show-password").addEventListener("change", (event) => {
      loginPassword.type = event.target.checked ? "text" : "password";
    });
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!loginForm.reportValidity()) return;
      loginPassword.value = "";
      loginMessage.textContent = "Sign-in is not connected yet. Your password was not sent or saved.";
      loginMessage.classList.add("visible");
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      message.textContent = "Sending your registration...";
      message.classList.add("visible");
      try {
        const response = await fetch("/register", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
          body: new URLSearchParams(new FormData(form))
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || "Registration could not be checked.");
        message.textContent = result.message;
        form.reset();
      } catch (error) {
        message.textContent = error.message || "Could not connect to the local Python server.";
      }
    });
  </script>
</body>
</html>
"""

REQUIRED_FIELDS = ("name", "email", "department", "year", "team")
VALID_YEARS = {"1st year", "2nd year", "3rd year", "4th year", "Other"}
VALID_TEAMS = {
    "I have a team",
    "I'm looking for teammates",
    "I'd like to join solo",
}


class HackathonHandler(BaseHTTPRequestHandler):
    """Serve the event page and validate registration interest locally."""

    def do_GET(self) -> None:
        if urlsplit(self.path).path != "/":
            self.send_error(404, "Page not found")
            return

        page = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/register":
            self._send_json(404, {"message": "Endpoint not found."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"message": "Invalid request."})
            return

        if content_length <= 0 or content_length > MAX_REQUEST_SIZE:
            self._send_json(413, {"message": "Registration request is too large or empty."})
            return

        content_type = self.headers.get_content_type()
        if content_type != "application/x-www-form-urlencoded":
            self._send_json(415, {"message": "Unsupported form format."})
            return

        form = parse_qs(
            self.rfile.read(content_length).decode("utf-8", errors="replace"),
            keep_blank_values=True,
            max_num_fields=10,
        )
        values = {field: form.get(field, [""])[0].strip() for field in REQUIRED_FIELDS}

        if any(not value for value in values.values()):
            self._send_json(400, {"message": "Please complete all registration fields."})
            return

        if any(len(value) > 200 for value in values.values()):
            self._send_json(400, {"message": "One or more fields are too long."})
            return

        email = values["email"]
        if parseaddr(email)[1] != email or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            self._send_json(400, {"message": "Enter a valid email address."})
            return

        if values["year"] not in VALID_YEARS or values["team"] not in VALID_TEAMS:
            self._send_json(400, {"message": "Choose a valid year and team status."})
            return

        self._send_json(
            200,
            {
                "message": (
                    "Thanks for registering your interest. This demo does not "
                    "store or send your information."
                )
            },
        )

    def _send_json(self, status: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        # Keep terminal output free of request details such as submitted email addresses.
        super().log_message(format, *args)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), HackathonHandler)
    print(f"Hackathon website is running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    try:
        webbrowser.open(f"http://{HOST}:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the hackathon website.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
