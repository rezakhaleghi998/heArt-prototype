"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, ChevronRight, Film, ImageIcon, Save } from "lucide-react";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { api, type Application, type AssetKind } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const schema = z.object({
  full_name: z.string().min(2, "Inserisci nome e cognome"),
  email: z.string().email("Email non valida"),
  phone: z.string().optional(),
  city: z.string().min(2, "Indica la città"),
  role: z.string().min(2, "Indica il ruolo"),
  short_bio: z.string().min(30, "Scrivi almeno 30 caratteri"),
  years_experience: z.coerce.number().min(0).max(80),
  skills: z.string().min(2, "Aggiungi almeno una disciplina"),
  availability: z.string().min(2, "Indica disponibilità"),
  portfolio_links: z.string().optional(),
  gdpr_consent: z.boolean().refine(Boolean, "Consenso richiesto")
});

type FormValues = z.infer<typeof schema>;

const steps: Array<{ key: keyof FormValues; label: string; question: string; kind?: "textarea" | "number" | "checkbox" }> = [
  { key: "full_name", label: "Nome", question: "Partiamo dal tuo nome completo." },
  { key: "email", label: "Email", question: "Qual è la tua email professionale?" },
  { key: "phone", label: "Telefono", question: "Lasciaci un telefono per il contatto casting." },
  { key: "city", label: "Città", question: "Dove sei basato/a?" },
  { key: "role", label: "Ruolo", question: "Per quale ruolo o area ti candidi?" },
  { key: "short_bio", label: "Bio", question: "Raccontaci chi sei in poche righe.", kind: "textarea" },
  { key: "years_experience", label: "Esperienza", question: "Quanti anni di esperienza hai?", kind: "number" },
  { key: "skills", label: "Discipline", question: "Quali skill o discipline artistiche vuoi evidenziare?" },
  { key: "availability", label: "Disponibilità", question: "Quando sei disponibile per progetti, audizioni o colloqui?" },
  { key: "portfolio_links", label: "Portfolio", question: "Aggiungi link a portfolio, showreel o social professionali.", kind: "textarea" },
  { key: "gdpr_consent", label: "Consenso", question: "Confermi il consenso al trattamento dati per questa candidatura?", kind: "checkbox" }
];

export default function ApplyPage() {
  const [step, setStep] = useState(0);
  const [application, setApplication] = useState<Application | null>(null);
  const [videoUploaded, setVideoUploaded] = useState(false);
  const [profileUploaded, setProfileUploaded] = useState(false);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [uploadingKind, setUploadingKind] = useState<AssetKind | null>(null);
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: {
      full_name: "",
      email: "",
      phone: "",
      city: "",
      role: "",
      short_bio: "",
      years_experience: 0,
      skills: "",
      availability: "",
      portfolio_links: "",
      gdpr_consent: false
    }
  });

  const current = steps[step];
  const progress = useMemo(() => Math.round(((step + (videoUploaded ? 2 : 0)) / (steps.length + 2)) * 100), [step, videoUploaded]);

  async function saveDraft() {
    const values = form.getValues();
    const payload = toPayload(values);
    const saved = application ? await api.updateApplication(application.id, payload) : await api.createApplication(payload);
    setApplication(saved);
    setStatus("Bozza salvata");
    return saved;
  }

  async function nextStep() {
    setError("");
    const ok = await form.trigger(current.key);
    if (!ok) return;
    if (step === 3 || step === 7 || step === steps.length - 1) {
      try {
        await saveDraft();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Errore API");
        return;
      }
    }
    setStep((value) => Math.min(value + 1, steps.length));
  }

  async function upload(kind: AssetKind, file: File | null) {
    if (!file) return;
    setError("");
    setUploadingKind(kind);
    setStatus("Preparazione upload...");
    try {
      const saved = application ?? (await saveDraft());
      const init = await api.initUpload({
        application_id: saved.id,
        kind,
        file_name: file.name,
        content_type: file.type,
        size_bytes: file.size
      });
      if (init.upload_url.includes("storage.local")) {
        await api.uploadDirect(init.asset_id, file);
      } else {
        const uploadResponse = await fetch(init.upload_url, { method: "PUT", body: file, headers: { "Content-Type": file.type } });
        if (!uploadResponse.ok) {
          throw new Error("Upload verso storage non riuscito. Controlla CORS e credenziali dello storage.");
        }
        await api.confirmUpload(init.asset_id, init.upload_url.split("?")[0]);
      }
      if (kind === "intro_video") setVideoUploaded(true);
      if (kind === "profile_image") setProfileUploaded(true);
      setStatus("Media confermato");
    } finally {
      setUploadingKind(null);
    }
  }

  async function submit() {
    setError("");
    try {
      const saved = await saveDraft();
      const submitted = await api.submitApplication(saved.id);
      setApplication(submitted);
      setStatus("Candidatura inviata e screening AI completato");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invio non riuscito");
    }
  }

  return (
    <main className="min-h-screen bg-paper">
      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-5 lg:grid-cols-[1fr_360px]">
        <section>
          <div className="mb-5 flex items-center justify-between">
            <a href="/" className="text-2xl font-black">heArt</a>
            <span className="rounded-md bg-basil/10 px-3 py-2 text-sm font-semibold text-basil">Candidatura guidata</span>
          </div>
          <Card className="overflow-hidden">
            <div className="h-2 bg-ink/8">
              <div className="h-full bg-coral transition-all" style={{ width: `${Math.min(progress, 100)}%` }} />
            </div>
            <div className="space-y-5 p-4 md:p-6">
              <div className="flex justify-start">
                <div className="max-w-[86%] rounded-lg bg-ink px-4 py-3 text-white">
                  <p className="text-sm font-semibold">Assistant heArt</p>
                  <p className="mt-1 leading-7">{step < steps.length ? current.question : "Perfetto. Ora carica i media e invia la candidatura."}</p>
                </div>
              </div>
              {step < steps.length ? (
                <div className="flex justify-end">
                  <div className="w-full max-w-xl rounded-lg bg-white p-4 shadow-soft">
                    <label className="mb-2 block text-sm font-bold">{current.label}</label>
                    <Field step={current} form={form} />
                    {form.formState.errors[current.key]?.message && (
                      <p className="mt-2 text-sm text-coral">{String(form.formState.errors[current.key]?.message)}</p>
                    )}
                    <div className="mt-4 flex gap-2">
                      <Button onClick={nextStep}>Avanti <ChevronRight size={17} /></Button>
                      <Button variant="secondary" onClick={() => saveDraft().catch((err) => setError(err.message))}>
                        <Save size={17} /> Salva bozza
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  <UploadBox title="Foto profilo" hint="Opzionale, JPG/PNG/WebP" icon={<ImageIcon />} done={profileUploaded} busy={uploadingKind === "profile_image"} onFile={(file) => upload("profile_image", file).catch((err) => setError(err.message))} />
                  <UploadBox title="Intro video" hint="Richiesto per invio, MP4/MOV/WebM" icon={<Film />} done={videoUploaded} busy={uploadingKind === "intro_video"} onFile={(file) => upload("intro_video", file).catch((err) => setError(err.message))} />
                  <div className="md:col-span-2 flex flex-col gap-3 sm:flex-row">
                    <Button disabled={!application || !videoUploaded} onClick={submit}>
                      Invia candidatura
                    </Button>
                    <Button variant="secondary" onClick={() => saveDraft().catch((err) => setError(err.message))}>
                      Continua come bozza
                    </Button>
                  </div>
                </div>
              )}
              {status && <p className="text-sm font-semibold text-basil">{status}</p>}
              {error && <p className="text-sm font-semibold text-coral">{error}</p>}
            </div>
          </Card>
        </section>
        <aside className="space-y-4">
          <Card className="p-5">
            <h2 className="text-lg font-black">Completamento</h2>
            <p className="mt-2 text-4xl font-black text-basil">{application?.completion_percent ?? progress}%</p>
            <p className="mt-2 text-sm leading-6 text-ink/65">I dati diventano un profilo candidato strutturato, leggibile via API e pronto per screening AI.</p>
          </Card>
          <Card className="p-5">
            <h2 className="text-lg font-black">Stato demo</h2>
            <ul className="mt-4 space-y-3 text-sm">
              <li className="flex items-center gap-2"><CheckCircle2 size={18} className="text-basil" /> Bozza salvabile</li>
              <li className="flex items-center gap-2"><CheckCircle2 size={18} className="text-basil" /> Upload presigned</li>
              <li className="flex items-center gap-2"><CheckCircle2 size={18} className="text-basil" /> Screening Groq isolato</li>
            </ul>
          </Card>
        </aside>
      </div>
    </main>
  );
}

function Field({ step, form }: { step: (typeof steps)[number]; form: ReturnType<typeof useForm<FormValues>> }) {
  const register = form.register(step.key);
  if (step.kind === "textarea") return <Textarea {...form.register(step.key)} placeholder="Scrivi qui..." />;
  if (step.kind === "checkbox") {
    return (
      <label className="flex items-start gap-3 rounded-md border border-ink/10 bg-paper p-3 text-sm leading-6">
        <input type="checkbox" className="mt-1" {...form.register(step.key)} />
        Autorizzo heArt a trattare i dati della candidatura per finalità di recruiting e casting.
      </label>
    );
  }
  return <Input type={step.kind === "number" ? "number" : "text"} {...register} placeholder="Risposta" />;
}

function UploadBox({ title, hint, icon, done, busy, onFile }: { title: string; hint: string; icon: ReactNode; done: boolean; busy: boolean; onFile: (file: File | null) => void }) {
  return (
    <label className="flex cursor-pointer flex-col gap-3 rounded-lg border border-dashed border-ink/20 bg-white p-5 transition hover:border-basil">
      <div className="flex items-center gap-3 text-basil">{icon}<span className="font-bold">{title}</span></div>
      <span className="text-sm text-ink/62">{hint}</span>
      <input className="sr-only" type="file" disabled={busy} onChange={(event) => onFile(event.target.files?.[0] ?? null)} />
      <span className="text-sm font-semibold">{busy ? "Caricamento..." : done ? "Caricato" : "Scegli file"}</span>
    </label>
  );
}

function toPayload(values: FormValues) {
  return {
    candidate: {
      full_name: values.full_name || "Bozza senza nome",
      email: values.email || `draft-${Date.now()}@example.local`,
      phone: values.phone,
      city: values.city || "Da completare"
    },
    role: values.role || "Da completare",
    short_bio: values.short_bio,
    years_experience: Number(values.years_experience),
    skills: values.skills.split(",").map((item) => item.trim()).filter(Boolean),
    availability: values.availability,
    portfolio_links: (values.portfolio_links ?? "").split(/\n|,/).map((item) => item.trim()).filter(Boolean),
    gdpr_consent: values.gdpr_consent
  };
}
