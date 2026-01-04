'use client'

import { useEffect, useState } from "react";

export default function Home() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((res) => res.json())
      .then(setData);
  }, []);

  return (
    <div>
      <h1>Backend Status</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
