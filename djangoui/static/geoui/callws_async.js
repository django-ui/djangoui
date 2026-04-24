if (typeof window.StartAsync !== 'undefined') {
    // async_jobs.html was included more than once on this page; skip the
    // second class definition to avoid "Identifier 'StartAsync' has already
    // been declared".
} else {
/**
 * StartAsync — small client for the /jobs/start + /jobs/status + /jobs/cancel API.
 *
 *   new StartAsync({
 *     go:     'go'        | HTMLElement | null,   // optional: button that restarts the job
 *     stop:   'stop'      | HTMLElement | null,   // optional: button that cancels the job
 *     out:    'out'       | HTMLElement | null,   // optional: element whose textContent is updated
 *     cb:     function(status, message, jobId, snap) { ... }, // optional: progress + terminal callback
 *     target: '_run',                             // server-side callable name (see @webapi /jobs/start)
 *     params: { seconds: 10 },                    // extra query params sent to /jobs/start
 *     intervalMs: 3000,            // poll every 3s (default)
 *     timeoutMs:  5 * 60_000,
 *   });
 *
 * The constructor always fires `start()` — buttons are optional controls.
 */
class StartAsync {
    constructor(opts = {}) {
        this.go     = StartAsync._el(opts.go);
        this.stop   = StartAsync._el(opts.stop);
        this.out    = StartAsync._el(opts.out);
        this.cb     = typeof opts.cb === 'function' ? opts.cb : null;
        this.target = opts.target || '_run';
        this.params = opts.params || {};
        this.intervalMs = opts.intervalMs ?? 3000;
        this.timeoutMs  = opts.timeoutMs  ?? 5 * 60_000;

        this.jobId = null;
        this._cancelled = false;

        if (this.go)   this.go.onclick   = () => this.start();
        if (this.stop) { this.stop.onclick = () => this.cancel(); this.stop.disabled = true; }

        // Always kick the job off on construction. Buttons are optional
        // controls — they don't gate the initial start.
        this.start();
    }

    static _el(x) {
        if (!x) return null;
        if (typeof x === 'string') return document.getElementById(x);
        return x; // assume DOM element
    }

    static _sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    _render(snap) {
        if (this.out) {
            this.out.textContent = `status=${snap.status}\nmsg=${snap.message}`;
        }
        if (this.cb) this.cb(snap.status, snap.message, snap.job_id || this.jobId, snap);
    }

    async start() {
        if (this.jobId) return; // already running
        this._cancelled = false;
        if (this.go)   this.go.disabled   = true;
        if (this.stop) this.stop.disabled = false;
        if (this.out)  this.out.textContent = 'starting…';

        const qs = new URLSearchParams({ target: this.target, ...this.params }).toString();
        try {
            const startResp = await fetch(`/jobs/start/?${qs}`, {
                method: 'POST', credentials: 'same-origin'
            }).then(r => r.json());

            if (startResp.error) throw new Error(startResp.error);
            this.jobId = startResp.job_id;
            if (this.out) this.out.textContent = `job_id=${this.jobId}\nwaiting…`;
            window.dispatchEvent(new CustomEvent('async-jobs-changed', { detail: { job_id: this.jobId, reason: 'start' } }));

            // Fire-and-forget: if no callback (and no out), there's nothing to
            // update on terminal status, so skip the polling loop entirely.
            if (!this.cb && !this.out) {
                return { job_id: this.jobId, status: 'running' };
            }

            const snap = await this._pollUntilDone();
            this._render(snap); // terminal call
            return snap;
        } catch (e) {
            const errSnap = { status: 'error', message: e.message, job_id: this.jobId };
            this._render(errSnap);
            throw e;
        } finally {
            this.jobId = null;
            if (this.go)   this.go.disabled   = false;
            if (this.stop) this.stop.disabled = true;
        }
    }

    async cancel() {
        if (!this.jobId) return;
        this._cancelled = true;
        await fetch(`/jobs/cancel/?job_id=${encodeURIComponent(this.jobId)}`, {
            method: 'POST', credentials: 'same-origin'
        });
        window.dispatchEvent(new CustomEvent('async-jobs-changed', { detail: { job_id: this.jobId, reason: 'cancel' } }));
    }

    async _pollUntilDone() {
        const deadline = Date.now() + this.timeoutMs;
        while (Date.now() < deadline) {
            const r = await fetch(`/jobs/status/?job_id=${encodeURIComponent(this.jobId)}`, {
                credentials: 'same-origin'
            });
            if (!r.ok) throw new Error(`status HTTP ${r.status}`);
            const snap = await r.json();
            this._render(snap); // interim callback
            if (snap.status.startsWith('done') || snap.status.startsWith('error') || snap.status.startsWith('cancelled')) {
                return snap;
            }
            await StartAsync._sleep(this.intervalMs);
        }
        throw new Error('poll timeout');
    }
}
// Expose to window so later includes of this file can detect & skip.
window.StartAsync = StartAsync;
} // end guard