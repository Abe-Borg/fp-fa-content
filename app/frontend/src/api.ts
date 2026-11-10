/**
 * The page's link to the app's local server (app/fpfa/web/server.py): the
 * launch token from the address, one JSON POST per action, and the event
 * stream that brings the state and the words of a reply as they arrive.
 */
import type { State } from "./types";

const params = new URLSearchParams(window.location.search);
export const TOKEN = params.get("token") || "";
const HEADER = "X-Cynosure-Token";

export class ApiError extends Error {}

async function readJson(response: Response): Promise<any> {
  let body: any = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok || !body || body.ok === false) {
    throw new ApiError((body && body.error) || `The app answered ${response.status}.`);
  }
  return body;
}

export async function getState(): Promise<State> {
  const response = await fetch("/api/state", { headers: { [HEADER]: TOKEN }, cache: "no-store" });
  return readJson(response);
}

export async function getText(name: "about" | "license" | "notices"): Promise<string> {
  const response = await fetch(`/api/text/${name}`, { headers: { [HEADER]: TOKEN }, cache: "no-store" });
  return (await readJson(response)).text as string;
}

export async function post(action: string, body: Record<string, unknown> = {}): Promise<any> {
  const response = await fetch(`/api/${action}`, {
    method: "POST",
    headers: { [HEADER]: TOKEN, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJson(response);
}

export interface StreamHandlers {
  state: (state: State) => void;
  live: (event: { job_id: string; project_id: string | null; gen: number; start: number; text: string }) => void;
  liveEnd: (event: { job_id: string }) => void;
  connected: (up: boolean) => void;
}

/** The event stream. The browser reconnects by itself; a new connection starts with the whole state. */
export function connect(handlers: StreamHandlers): () => void {
  const source = new EventSource(`/api/events?token=${encodeURIComponent(TOKEN)}`);
  source.addEventListener("open", () => handlers.connected(true));
  source.addEventListener("error", () => handlers.connected(false));
  source.addEventListener("state", (event) => handlers.state(JSON.parse((event as MessageEvent).data)));
  source.addEventListener("live", (event) => handlers.live(JSON.parse((event as MessageEvent).data)));
  source.addEventListener("live_end", (event) => handlers.liveEnd(JSON.parse((event as MessageEvent).data)));
  return () => source.close();
}
