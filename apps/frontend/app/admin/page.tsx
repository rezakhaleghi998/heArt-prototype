"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, BrainCircuit, Filter, RefreshCw } from "lucide-react";
import { api, type Application, type ApplicationStatus } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const statuses: Array<{ label: string; value: ApplicationStatus | "all" }> = [
  { label: "Tutte", value: "all" },
  { label: "Bozze", value: "draft" },
  { label: "Inviate", value: "submitted" },
  { label: "Screening", value: "screening" },
  { label: "Valutate", value: "reviewed" }
];

export default function AdminPage() {
  const [status, setStatus] = useState<ApplicationStatus | "all">("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const query = useQuery({
    queryKey: ["applications", status],
    queryFn: () => api.listApplications(status === "all" ? undefined : status)
  });
  const items = query.data?.items ?? [];
  const selected = useMemo(() => items.find((item) => item.id === selectedId) ?? items[0], [items, selectedId]);

  return (
    <main className="min-h-screen bg-paper">
      <div className="mx-auto max-w-7xl px-4 py-5 md:px-8">
        <header className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold text-ink/62 hover:text-ink">
              <ArrowLeft size={16} /> Home
            </Link>
            <h1 className="mt-3 text-3xl font-black md:text-5xl">Recruiter cockpit</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/65">
              Demo senza autenticazione: lista candidature, stato funnel, materiali e valutazione AI.
            </p>
          </div>
          <Button variant="secondary" onClick={() => query.refetch()}>
            <RefreshCw size={17} /> Aggiorna
          </Button>
        </header>

        <div className="mb-5 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-2 text-sm font-bold"><Filter size={16} /> Stato</span>
          {statuses.map((item) => (
            <button
              key={item.value}
              className={`rounded-md px-3 py-2 text-sm font-semibold ${status === item.value ? "bg-basil text-white" : "bg-white text-ink ring-1 ring-ink/10"}`}
              onClick={() => setStatus(item.value)}
            >
              {item.label}
            </button>
          ))}
        </div>

        {query.isError && (
          <Card className="mb-5 flex items-center gap-3 p-4 text-coral">
            <AlertTriangle size={20} /> API non raggiungibile. Avvia il backend o importa i seed.
          </Card>
        )}

        <div className="grid gap-5 lg:grid-cols-[420px_1fr]">
          <section className="space-y-3">
            {items.map((application) => (
              <button
                key={application.id}
                onClick={() => setSelectedId(application.id)}
                className={`w-full rounded-lg border bg-white p-4 text-left shadow-soft transition hover:border-basil ${selected?.id === application.id ? "border-basil" : "border-ink/10"}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="font-black">{application.candidate.full_name}</h2>
                    <p className="mt-1 text-sm text-ink/62">{application.role} · {application.candidate.city}</p>
                  </div>
                  <span className="rounded-md bg-ink/5 px-2 py-1 text-xs font-bold">{application.status}</span>
                </div>
                <div className="mt-4 h-2 rounded-full bg-ink/8">
                  <div className="h-full rounded-full bg-gold" style={{ width: `${application.completion_percent}%` }} />
                </div>
                <p className="mt-2 text-xs font-semibold text-ink/55">{application.completion_percent}% completo</p>
              </button>
            ))}
            {!items.length && <Card className="p-5 text-sm text-ink/65">Nessuna candidatura per questo filtro.</Card>}
          </section>
          <section>{selected ? <ApplicationDetail application={selected} /> : <Card className="p-6">Seleziona una candidatura.</Card>}</section>
        </div>
      </div>
    </main>
  );
}

function ApplicationDetail({ application }: { application: Application }) {
  const screening = application.screening_result;
  return (
    <div className="space-y-5">
      <Card className="p-5">
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
          <div>
            <h2 className="text-2xl font-black">{application.candidate.full_name}</h2>
            <p className="mt-1 text-ink/65">{application.candidate.email} · {application.candidate.phone || "Telefono non indicato"}</p>
          </div>
          <div className="rounded-lg bg-basil px-4 py-3 text-center text-white">
            <p className="text-xs font-bold uppercase">Fit score</p>
            <p className="text-3xl font-black">{screening?.fit_score ?? "-"}/10</p>
          </div>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <Info label="Ruolo" value={application.role} />
          <Info label="Esperienza" value={`${application.years_experience ?? 0} anni`} />
          <Info label="Disponibilità" value={application.availability ?? "-"} />
        </div>
        <p className="mt-5 leading-7 text-ink/75">{application.short_bio}</p>
        <div className="mt-5 flex flex-wrap gap-2">
          {application.skills.map((skill) => (
            <span key={skill} className="rounded-md bg-coral/10 px-3 py-2 text-sm font-semibold text-coral">{skill}</span>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <h3 className="flex items-center gap-2 text-lg font-black"><BrainCircuit size={20} /> Screening AI</h3>
        <p className="mt-3 leading-7 text-ink/75">{screening?.summary ?? "Screening non ancora disponibile."}</p>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <Insight title="Punti forti" items={screening?.strengths ?? []} />
          <Insight title="Gap o rischi" items={screening?.risks ?? []} />
        </div>
        <div className="mt-5 rounded-lg bg-paper p-4">
          <p className="text-sm font-bold">Prossima azione</p>
          <p className="mt-1 text-sm text-ink/70">{screening?.recommended_next_action ?? "Da definire"}</p>
        </div>
      </Card>

      <Card className="p-5">
        <h3 className="text-lg font-black">Media e portfolio</h3>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {application.media_assets.map((asset) => (
            <div key={asset.id} className="rounded-lg border border-ink/10 p-4">
              <p className="font-bold">{asset.kind}</p>
              <p className="mt-1 text-sm text-ink/62">{asset.file_name}</p>
              <p className="mt-2 text-xs font-semibold">{asset.uploaded ? "Upload confermato" : "In attesa"}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 space-y-2 text-sm">
          {application.portfolio_links.map((link) => (
            <a key={link} className="block font-semibold text-basil underline-offset-4 hover:underline" href={link} target="_blank">
              {link}
            </a>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-paper p-4">
      <p className="text-xs font-bold uppercase text-ink/48">{label}</p>
      <p className="mt-1 font-semibold">{value}</p>
    </div>
  );
}

function Insight({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h4 className="font-bold">{title}</h4>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-ink/70">
        {(items.length ? items : ["Non disponibile"]).map((item) => (
          <li key={item} className="rounded-md bg-paper px-3 py-2">{item}</li>
        ))}
      </ul>
    </div>
  );
}
