import Image from "next/image";
import Link from "next/link";
import { getAllKurals } from "./lib/kurals";

export default function Home() {
  const kurals = getAllKurals();

  if (kurals.length === 0) {
    return (
      <section className="rounded-lg border-2 border-dashed border-ink/20 p-12 text-center">
        <h1 className="mb-3 font-serif text-3xl text-indigo">No kurals yet</h1>
        <p className="text-ink/70">
          Run <code className="rounded bg-ink/5 px-1.5 py-0.5 text-sm">python generate.py --kural-id 211</code>{" "}
          in the pipeline to generate one, then refresh.
        </p>
      </section>
    );
  }

  return (
    <section>
      <h1 className="mb-2 font-serif text-4xl text-indigo">A kural a day</h1>
      <p className="mb-10 text-ink/70">
        Pick one. A six-line bedtime story, a four-panel folk-art comic, one gentle moral.
      </p>

      <ul className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {kurals.map((kural) => (
          <li key={kural.id}>
            <Link
              href={`/kural/${kural.id}/`}
              className="group block overflow-hidden rounded-md border-2 border-ink/10 bg-white transition hover:border-indigo focus:outline-none focus:ring-2 focus:ring-indigo"
            >
              <div className="relative aspect-square w-full bg-cream">
                <Image
                  src={`/images/${kural.id}/composite.png`}
                  alt={kural.title}
                  fill
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  className="object-cover"
                />
              </div>
              <div className="border-t-2 border-ink/10 p-4">
                <p className="text-xs uppercase tracking-wider text-terracotta">
                  Kural {kural.id}
                </p>
                <h2 className="mt-1 font-serif text-xl text-indigo group-hover:underline">
                  {kural.title}
                </h2>
                <p className="mt-2 line-clamp-2 text-sm text-ink/70">{kural.moral_line}</p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
