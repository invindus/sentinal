"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  type Blog,
  fetchBlogs,
  ingestNvidiaFeed,
  latestSentiment,
} from "@/lib/api";
import styles from "./page.module.css";

function formatDate(d?: string) {
  if (!d) return "";
  return new Date(d).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function SentimentDashboard() {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Blog | null>(null);

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
      await ingestNvidiaFeed(10);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ingest failed");
    } finally {
      setIngesting(false);
    }
  }

  const stats = useMemo(() => {
    const all = blogs.flatMap((b) => b.sentiments ?? []);
    const pos = all.filter((s) => s.label === "positive").length;
    const neg = all.filter((s) => s.label === "negative").length;
    const neu = all.filter((s) => s.label === "neutral").length;

    return {
      total: all.length,
      pos,
      neg,
      neu,
    };
  }, [blogs]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Sentiment Terminal</h1>
          <p className={styles.subtitle}>
            Live blog intelligence + sentiment tracking
          </p>
        </div>

        <div className={styles.actions}>
          <button
            className={styles.btnSecondary}
            onClick={load}
            disabled={loading || ingesting}
          >
            {loading ? "Refreshing…" : "Refresh"}
          </button>

          <button
            className={styles.btnPrimary}
            onClick={onIngest}
            disabled={ingesting}
          >
            {ingesting ? "Scraping…" : "Ingest Feed"}
          </button>
        </div>
      </header>

      {error ? <div className={styles.error}>{error}</div> : null}

      {/* KPI Strip */}
      <section className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <h3>Total Analyses</h3>
          <p>{stats.total}</p>
        </div>
        <div className={styles.kpiCard}>
          <h3>Positive</h3>
          <p>{stats.pos}</p>
        </div>
        <div className={styles.kpiCard}>
          <h3>Neutral</h3>
          <p>{stats.neu}</p>
        </div>
        <div className={styles.kpiCard}>
          <h3>Negative</h3>
          <p>{stats.neg}</p>
        </div>
      </section>

      <div className={styles.layout}>
        {/* LEFT: Blog list */}
        <aside className={styles.sidebar}>
          <h2>Feeds</h2>
          {blogs.map((b) => {
            const s = latestSentiment(b);
            return (
              <button
                key={b.id}
                className={styles.blogItem}
                onClick={() => setSelected(b)}
              >
                <div className={styles.blogTitle}>
                  {b.title || "Untitled"}
                </div>
                <div className={styles.blogMeta}>
                  <span>{s?.label ?? "no sentiment"}</span>
                  <span>{formatDate(b.scraped_at)}</span>
                </div>
              </button>
            );
          })}
        </aside>

        {/* RIGHT: Detail panel */}
        <main className={styles.panel}>
          {!selected ? (
            <div className={styles.emptyState}>
              Select a blog to view sentiment timeline
            </div>
          ) : (
            <>
              <h2>{selected.title}</h2>
              <a href={selected.url} target="_blank" rel="noreferrer">
                Open source
              </a>

              <div className={styles.timeline}>
                {(selected.sentiments ?? []).map((s, i) => (
                  <div key={i} className={styles.timelineItem}>
                    <div className={styles.timelineLabel}>{s.label}</div>
                    <div className={styles.timelineScore}>
                      {s.score.toFixed(3)}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}