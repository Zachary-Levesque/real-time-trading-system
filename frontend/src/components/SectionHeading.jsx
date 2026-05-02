export function SectionHeading({ eyebrow, title, description }) {
  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-[0.35em] text-sky-300">{eyebrow}</p>
      <h2 className="text-3xl font-semibold text-white sm:text-4xl">{title}</h2>
      <p className="max-w-2xl text-base text-slate-300 sm:text-lg">{description}</p>
    </div>
  );
}

