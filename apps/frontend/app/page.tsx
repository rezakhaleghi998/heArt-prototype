import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, Clapperboard, SearchCheck, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  { icon: BriefcaseBusiness, title: "Funnel conversazionale", text: "Raccoglie dati strutturati senza sembrare un form freddo." },
  { icon: UploadCloud, title: "Media upload", text: "Foto, showreel e materiali gestiti come asset pronti per produzione." },
  { icon: SearchCheck, title: "AI screening", text: "Sintesi, score e gap per velocizzare il primo triage recruiter." }
];

export default function HomePage() {
  return (
    <main>
      <section
        className="min-h-[88vh] bg-cover bg-center"
        style={{
          backgroundImage:
            "linear-gradient(90deg, rgba(23,23,23,.78), rgba(23,23,23,.36)), url('https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1800&q=80')"
        }}
      >
        <div className="mx-auto flex min-h-[88vh] max-w-6xl flex-col justify-between px-5 py-5 text-white md:px-8">
          <nav className="flex items-center justify-between">
            <div className="text-2xl font-black tracking-normal">heArt</div>
            <Link className="text-sm font-semibold underline-offset-4 hover:underline" href="/admin">
              Area recruiter
            </Link>
          </nav>
          <div className="max-w-2xl pb-12">
            <div className="mb-4 inline-flex rounded-md bg-white/12 px-3 py-2 text-sm backdrop-blur">
              Casting, cultura e spettacolo
            </div>
            <h1 className="text-5xl font-black leading-none tracking-normal md:text-7xl">heArt</h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-white/88">
              Un prototipo AI-native per trasformare candidature artistiche in profili strutturati, materiali media e insight utili al team casting.
            </p>
            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              <Link href="/apply">
                <Button className="w-full bg-coral hover:bg-[#bf4f43] sm:w-auto">
                  Inizia la candidatura <ArrowRight size={18} />
                </Button>
              </Link>
              <Link href="/admin">
                <Button variant="secondary" className="w-full border-white/25 bg-white/12 text-white hover:bg-white/20 sm:w-auto">
                  Demo recruiter <Clapperboard size={18} />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
      <section className="mx-auto grid max-w-6xl gap-4 px-5 py-8 md:grid-cols-3 md:px-8">
        {features.map((feature) => (
          <article key={feature.title} className="rounded-lg border border-ink/10 bg-white p-5">
            <feature.icon className="mb-4 text-basil" size={28} />
            <h2 className="text-lg font-bold">{feature.title}</h2>
            <p className="mt-2 text-sm leading-6 text-ink/68">{feature.text}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
