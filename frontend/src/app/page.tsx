"use client";

import { useCallback, useEffect, useState } from "react";
import {
  type Blog,
  fetchBlogs,
  ingestNvidiaFeed,
  latestSentiment,
} from "@/lib/api";
import styles from "./page.module.css";

export default function Home() {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetchBlogs();
      setBlogs(res.data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load blogs");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function onIngest() {
    setError(null);
    setIngesting(true);
    try {
      const summary = await ingestNvidiaFeed(10);
      if (summary.failed > 0) {
        const errPreview = summary.errors
          .slice(0, 2)
          .map((e) => `${e.url}: ${e.detail}`)
          .join(" · ");
        setError(
          `Ingested ${summary.ingested}/${summary.attempted}. ${summary.failed} failed. ${errPreview}`,
        );
      }
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ingest failed");
    } finally {
      setIngesting(false);
    }
  }

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>Sentinal</h1>
            <p className={styles.subtitle}>
              Blog posts and sentiment history from your API
            </p>
          </div>
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.btnSecondary}
              onClick={() => load()}
              disabled={loading || ingesting}
            >
              {loading ? "Loading…" : "Refresh"}
            </button>
            <button
              type="button"
              className={styles.btnPrimary}
              onClick={onIngest}
              disabled={loading || ingesting}
            >
              {ingesting
                ? "Scraping…"
                : "Scrape feed (10 posts, NVIDIA blog RSS)"}
            </button>
          </div>
        </header>

        {error ? (
          <p className={styles.error} role="alert">
            {error}
          </p>
        ) : null}

        {loading && blogs.length === 0 ? (
          <p className={styles.muted}>Loading blogs…</p>
        ) : null}

        {!loading && blogs.length === 0 ? (
          <p className={styles.muted}>
            No posts yet. Run <strong>Scrape & analyze</strong> with the API
            and Postgres running.
          </p>
        ) : null}

        <ul className={styles.list}>
          {blogs.map((blog) => {
            const s = latestSentiment(blog);
            return (
              <li key={blog.id} className={styles.card}>
                <h2 className={styles.cardTitle}>{blog.title || "(no title)"}</h2>
                <p className={styles.meta}>
                  <span className={styles.badge}>{blog.source}</span>
                  {blog.scraped_at ? (
                    <span>
                      Updated{" "}
                      {new Date(blog.scraped_at).toLocaleString(undefined, {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </span>
                  ) : null}
                </p>
                {s ? (
                  <p className={styles.sentiment}>
                    <span className={styles[`label_${s.label}`] ?? ""}>
                      {s.label}
                    </span>
                    <span className={styles.score}>
                      compound {s.score.toFixed(3)}
                    </span>
                    <span className={styles.runs}>
                      {blog.sentiments.length} analysis run
                      {blog.sentiments.length === 1 ? "" : "s"}
                    </span>
                  </p>
                ) : (
                  <p className={styles.muted}>No sentiment rows yet</p>
                )}
                <a
                  className={styles.link}
                  href={blog.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {blog.url}
                </a>
              </li>
            );
          })}
        </ul>
      </main>
    </div>
  );
}
