"""/jobs/* webapi endpoints backed by mangorest.AsyncJobs.

Public routes:
    POST /jobs/start/?target=<name>[&...]    -> {"job_id": "..."}
    GET  /jobs/status/?job_id=XXXX           -> snapshot (marks terminal as fetched)
    POST /jobs/cancel/?job_id=XXXX           -> {"ok": true}
    POST /jobs/cleanup/[?job_id=XXXX|all=1]  -> {"removed": [...]}
    GET  /jobs/list/[?all=1]                 -> dict[job_id, brief]

Targets are resolved by `_resolve()` — any dotted path like
`pkg.mod.func` or a bare name that resolves in this module's globals.
"""
import logging
import random
import sys
import time

from mangorest.mango import webapi, start_async_job, get_argspec
from mangorest.AsyncJobs import AsyncJobs

logger = logging.getLogger(__name__)


def _resolve(target):
    """Resolve a dotted string like 'pkg.mod.func' (mangorest-style) to a
    callable. If `target` is already callable, return as-is. Falls back to
    looking up a bare name in this module's globals. Returns None if not
    resolvable."""
    if callable(target):
        return target
    if not isinstance(target, str) or not target:
        return None
    spl = target.split(".")
    if len(spl) >= 2:
        modName = ".".join(spl[:-1])
        funName = spl[-1]
        try:
            __import__(modName, fromlist="dummy")
        except Exception:
            return None
        for v in sys.modules:
            if v.startswith(modName):
                fn = getattr(sys.modules[v], funName, None)
                if callable(fn):
                    return fn
        return None
    # bare name: look up in this module
    fn = globals().get(target)
    return fn if callable(fn) else None


# --- example target function ------------------------------------------------
# Example fo call by target name
def _run(request=None, job: AsyncJobs = None, **kwargs):
    """Example / demo target. Call `job.running(message=...)` for interim
    updates; return a value to auto-finalize the job (done)."""
    seconds = int(kwargs.get("seconds", random.randint(30, 60)))
    logger.info(f"Starting demo job with seconds: {seconds}")

    for i in range(1, seconds + 1):
        # Cooperative cancellation: /jobs/cancel flips the job status; we
        # notice it here, clean up, stash a partial result / message, and
        # exit the loop. Status is already "cancelled @ ...", so the
        # auto-finalizer in mangorest will NOT overwrite it with done.
        if job.is_cancelled():
            logger.info(f"job {job.job_id} cancelled at step {i}/{seconds} — cleaning up")
            # (demo) pretend we close files / release handles here
            job.running(message=f"cancelled at step {i}/{seconds} — cleaned up",
                        result={"cancelled_at_step": i, "total_steps": seconds})
            return None

        time.sleep(1)
        job.running(message=f"step {i}/{seconds}",
                    percent_complete=int(100 * i / seconds))
    return {"answer": 42, "took_s": seconds}

#
# test this by callws_async("/jobs/example_job", ...)
#
@webapi("/jobs/example_job")
def _run_sync_asycn(request=None,  **kwargs):

    seconds = int(kwargs.get("seconds", random.randint(5, 60)))
    logger.info(f"Starting demo job with seconds: {seconds}")

    job: AsyncJobs = kwargs.get("job", None)
    if not job :
        logger.info(f"?? Called Sychronous {seconds} waiting ....??")
    else:
        logger.info(f"** CALLED ASYNCHRONOUSLY will finish in {seconds} ??")

    for i in range(1, seconds + 1):
        if job and job.is_cancelled():
            logger.info(f"job {job.job_id} cancelled at step {i}/{seconds} — cleaning up")
            # (demo) pretend we close files / release handles here
            job.running(message=f"cancelled at step {i}/{seconds} — cleaned up",
                        result={"cancelled_at_step": i, "total_steps": seconds})
            return None

        time.sleep(1)
        if (job):
            job.running(message=f"step {i}/{seconds}", percent_complete=int(100 * i / seconds))

    return {"answer": 42, "took_s": seconds}


# --- helpers ----------------------------------------------------------------
def _current_user(request, kwargs):
    """Derive a user identity for a job. Priority: kwargs['user']
    explicitly passed by the caller, else request.user.username, else
    'anonymous'."""
    u = kwargs.get("user")
    if u:
        return str(u)
    try:
        username = getattr(getattr(request, "user", None), "username", None)
        if username:
            return str(username)
    except Exception:
        pass
    return "anonymous"


# --- webapi endpoints -------------------------------------------------------
@webapi("/jobs/start")
def start(request, target="_run", **kwargs):
    """POST /jobs/start/?seconds=10&target=pkg.mod.func -> {"job_id": "..."}.

    Thin wrapper over mangorest.start_async_job: resolves `target` (dotted
    path or bare name registered in this module) and delegates the actual
    thread dispatch + AsyncJobs bookkeeping to mangorest.
    """
    func = _resolve(target)
    if func is None:
        return {"error": f"target {target!r} not resolvable to a callable"}

    # request has already been attached to kwargs by getparms(); drop it
    # so start_async_job's par dict is a clean set of kwargs.
    par = {k: v for k, v in kwargs.items() if k != "request"}
    par["user"] = _current_user(request, par)
    return start_async_job(
        func, request, par,
        args=get_argspec(func),
        job_name=par.pop("job_name", None),
        target_label=target,
    )


@webapi("/jobs/status")
def status(request, job_id="", **kwargs):
    """GET /jobs/status/?job_id=XXXX -> current snapshot. Marks terminal
    jobs as 'fetched' so /jobs/cleanup/ can reap them."""
    logger.info(f"*: status for job '{job_id}'")
    job = AsyncJobs.get(job_id)
    if job is None:
        logger.error(f"**** ERROR: Job '{job_id}' not found")
        return {"error": "unknown job_id"}
    return job.snapshot(mark_fetched=True)


@webapi("/jobs/cancel")
def cancel(request, job_id="", **kwargs):
    """Optional: mark a job cancelled. (Doesn't actually kill the thread in
    this toy example — real code would check a flag inside the target.)"""
    job = AsyncJobs.get(job_id)
    if job is None:
        logger.error(f"**** ERROR: Job '{job_id}' not found")
        return {"error": "unknown job_id"}
    job.cancel()
    return {"ok": True}


@webapi("/jobs/cleanup")
def cleanup(request, job_id="", all="", **kwargs):
    """Remove finished jobs.

    - /jobs/cleanup/?job_id=XXXX     -> remove that one job
    - /jobs/cleanup/                 -> remove all terminal jobs whose status
                                        has already been fetched by the client
    - /jobs/cleanup/?all=1           -> remove all terminal jobs regardless
    """
    if job_id:
        return AsyncJobs.remove(job_id=job_id)
    remove_all = str(all).lower() in ("1", "true", "yes")
    return AsyncJobs.remove(only_fetched=not remove_all)


@webapi("/jobs/list")
def list_jobs(request, all="", **kwargs):
    """Return a brief listing of jobs in the registry.

    - /jobs/list/           -> only the current user's jobs (default)
    - /jobs/list/?all=1     -> all jobs on the server
    """
    show_all = str(all).lower() in ("1", "true", "yes")
    me = _current_user(request, kwargs)
    out = {}
    for jid, j in AsyncJobs.all().items():
        if not show_all and j.get("user") != me:
            continue
        start_ts = j.get("start")
        out[jid] = {
            "status":           j.get("status"),
            "message":          j.get("message"),
            "target":           j.get("target"),
            "job_name":         j.get("job_name"),
            "user":             j.get("user"),
            "fetched":          j.get("fetched"),
            "percent_complete": j.get("percent_complete"),
            "start":            start_ts.isoformat() if start_ts else None,
        }
    return out
