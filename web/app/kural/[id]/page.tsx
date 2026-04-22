import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllKuralIds, getKural } from "../../lib/kurals";

type Props = { params: Promise<{ id: string }> };

export function generateStaticParams() {
  return getAllKuralIds().map((id) => ({ id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const kural = getKural(id);
  if (!kural) return {};
  const compositeUrl = `/images/${kural.id}/composite.png`;
  return {
    title: kural.title,
    description: kural.moral_line,
    openGraph: {
      title: kural.title,
      description: kural.moral_line,
      type: "article",
      images: [{ url: compositeUrl, width: 1600, height: 1800, alt: kural.title }],
    },
    twitter: {
      card: "summary_large_image",
      title: kural.title,
      description: kural.moral_line,
      images: [compositeUrl],
    },
  };
}

export default async function KuralDetail({ params }: Props) {
  const { id } = await params;
  const kural = getKural(id);
  if (!kural) notFound();

  return (
    <article className="space-y-12">
      <header>
        <Link href="/" className="text-sm text-indigo hover:underline">
          &larr; All kurals
        </Link>
        <p className="mt-4 text-xs uppercase tracking-wider text-terracotta">
          Kural {kural.id} &middot; {kural.chapter}
        </p>
        <h1 className="mt-1 font-serif text-4xl text-indigo">{kural.title}</h1>
      </header>

      <section className="rounded-md border-2 border-ink/10 bg-white p-6">
        <p className="whitespace-pre-line font-serif text-lg leading-relaxed text-ink">
          {kural.tamil}
        </p>
        <p className="mt-4 text-ink/80">{kural.translation}</p>
      </section>

      <section>
        <h2 className="mb-4 font-serif text-2xl text-indigo">The story</h2>
        <ol className="space-y-3 font-serif text-lg leading-relaxed">
          {kural.story.map((line, i) => (
            <li key={i} className="flex gap-4">
              <span className="select-none text-sm text-terracotta">{i + 1}</span>
              <span>{line}</span>
            </li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="mb-4 font-serif text-2xl text-indigo">The comic</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {kural.panels.map((panel, i) => (
            <figure key={i} className="overflow-hidden rounded-md border-2 border-ink/10 bg-white">
              <div className="relative aspect-square w-full">
                <Image
                  src={`/images/${kural.id}/panel-${i + 1}.png`}
                  alt={panel.beat}
                  fill
                  sizes="(max-width: 640px) 100vw, 50vw"
                  className="object-cover"
                />
              </div>
              <figcaption className="border-t-2 border-ink/10 px-4 py-3 text-sm text-ink/70">
                {panel.beat}
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section className="border-t-2 border-ink/10 pt-8 text-center">
        <p className="font-serif text-xl text-terracotta">{kural.moral_line}</p>
      </section>
    </article>
  );
}
