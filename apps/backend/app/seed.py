from app.db.session import SessionLocal
from app.models.enums import ApplicationStatus, AssetKind, ScreeningStatus
from app.models.media_asset import MediaAsset
from app.models.screening_result import ScreeningResult
from app.repositories.applications import ApplicationRepository
from app.schemas.application import ApplicationDraftIn, CandidateIn


SAMPLES = [
    {
        "candidate": CandidateIn(full_name="Giulia Bianchi", email="giulia.bianchi@example.com", phone="+39 333 1010101", city="Milano"),
        "role": "Performer e cantante per produzioni musical",
        "short_bio": "Performer con formazione in canto moderno, danza jazz e teatro fisico. Ha lavorato in tour nazionali e produzioni corporate dal vivo.",
        "years_experience": 7,
        "skills": ["canto", "danza jazz", "recitazione", "improvvisazione", "tour live"],
        "availability": "Disponibile da maggio, trasferte incluse",
        "portfolio_links": ["https://vimeo.com/showcase/giulia-bianchi", "https://instagram.com/giuliabianchi.artist"],
        "gdpr_consent": True,
    },
    {
        "candidate": CandidateIn(full_name="Marco Ferri", email="marco.ferri@example.com", phone="+39 347 2020202", city="Roma"),
        "role": "Tecnico luci freelance",
        "short_bio": "Tecnico luci per eventi live, teatro e festival. Esperienza con console GrandMA e programmazione cue per spettacoli indoor.",
        "years_experience": 5,
        "skills": ["lighting design", "GrandMA", "festival", "teatro"],
        "availability": "Weekend e tournée brevi",
        "portfolio_links": ["https://marcoferri.example.com"],
        "gdpr_consent": True,
    },
    {
        "candidate": CandidateIn(full_name="Sara Conti", email="sara.conti@example.com", phone="+39 320 3030303", city="Torino"),
        "role": "Attrice per spot e branded content",
        "short_bio": "Attrice con esperienza in spot digital, voice-over e piccoli ruoli televisivi. Buona presenza camera e dizione neutra.",
        "years_experience": 3,
        "skills": ["recitazione camera", "voice-over", "dizione", "branded content"],
        "availability": "Disponibile con preavviso di 7 giorni",
        "portfolio_links": ["https://youtube.com/@saraconti"],
        "gdpr_consent": True,
    },
]


def run() -> None:
    db = SessionLocal()
    try:
        repo = ApplicationRepository(db)
        for index, sample in enumerate(SAMPLES):
            application = repo.upsert_draft(ApplicationDraftIn(**sample))
            has_intro = any(asset.kind == AssetKind.intro_video for asset in application.media_assets)
            if not has_intro:
                db.add(
                    MediaAsset(
                        application_id=application.id,
                        kind=AssetKind.intro_video,
                        file_name="intro-video.mp4",
                        content_type="video/mp4",
                        size_bytes=18_000_000,
                        storage_key=f"seed/{application.id}/intro-video.mp4",
                        public_url="https://example.com/seed/intro-video.mp4",
                        uploaded=True,
                    )
                )
            if index == 0:
                application.status = ApplicationStatus.reviewed
                if application.screening_result is None:
                    db.add(
                        ScreeningResult(
                            application_id=application.id,
                            status=ScreeningStatus.completed,
                            summary="Profilo forte per produzioni musical e live: esperienza coerente, materiali portfolio presenti e disponibilità alle trasferte.",
                            strengths=["Esperienza di tour nazionale", "Skill multidisciplinari", "Portfolio chiaro", "Disponibilità operativa"],
                            risks=["Verificare range vocale e disponibilità date specifiche"],
                            fit_score=9,
                            recommended_next_action="Invitare a colloquio e richiedere showreel completo",
                            raw_response={},
                        )
                    )
            else:
                application.status = ApplicationStatus.submitted
            db.commit()
        print("Seed data loaded.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
