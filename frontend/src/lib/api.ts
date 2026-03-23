export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type SentimentRow = {
  id: string;
  score: number;
  label: string;
  emotion: string | null;
  analyzed_at: string | null;
};

export type Blog = {
  id: string;
  source: string;
  url: string;
  title: string;
  author: string | null;
  scraped_at: string | null;
  published_at: string | null;
  content: string;
  sentiments: SentimentRow[];
};

export type BlogsResponse = { count: number; data: Blog[] };

export type IngestResponse = { status: string; data: Blog };

async function readError(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const j = JSON.parse(text) as { detail?: string | unknown };
    if (typeof j.detail === "string") return j.detail;
  } catch {
    /* use raw text */
  }
  return text || res.statusText;
}

export async function fetchBlogs(): Promise<BlogsResponse> {
  const res = await fetch(`${API_BASE}/blogs`, { cache: "no-store" });
  if (!res.ok) throw new Error(await readError(res));
  return res.json() as Promise<BlogsResponse>;
}

export async function ingestNvidiaBlog(): Promise<IngestResponse> {
  const res = await fetch(`${API_BASE}/scrape/nvidia`, { method: "POST" });
  if (!res.ok) throw new Error(await readError(res));
  return res.json() as Promise<IngestResponse>;
}

export type FeedIngestResponse = {
  status: string;
  feed_url: string;
  attempted: number;
  ingested: number;
  failed: number;
  results: { url: string; blog_id: string; title: string }[];
  errors: { url: string; detail: string }[];
};

/** Scrape up to `limit` posts from https://blogs.nvidia.com/feed/ */
export async function ingestNvidiaFeed(limit: number = 10): Promise<FeedIngestResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  const res = await fetch(`${API_BASE}/scrape/nvidia/feed?${params}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json() as Promise<FeedIngestResponse>;
}

export function latestSentiment(blog: Blog): SentimentRow | undefined {
  return blog.sentiments[0];
}
