"""
Amar Passport — CrewAI Multi-Agent Assignment
Bangladesh e-Passport readiness assistant.

Install:
    pip install crewai

Run:
    python amar_passport_agent.py

Notes:
- Fee values below match the Bangladesh e-Passport portal fee table available
  when this example was prepared. Amounts already INCLUDE 15% VAT.
- The local JSON-style database is the fallback if live policy retrieval fails.
- This is an educational assistant, not an official decision or legal advice.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process


# Keep CrewAI's internal task/agent logs from duplicating the final report.
logging.getLogger("crewai").setLevel(logging.ERROR)
logging.getLogger("litellm").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

# Prefer UTF-8 output. The terminal itself must also use a Bengali-capable font.
if os.name == "nt":
    os.system("chcp 65001 > nul")
for _stream_name in ("stdout", "stderr", "stdin"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


# Load .env from the same folder as this script, regardless of terminal location.
load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY পাওয়া যায়নি। amar_passport_agent.py-এর একই ফোল্ডারে "
        ".env ফাইল তৈরি করে OPENROUTER_API_KEY=আপনার_key লিখুন।"
    )

# Shared LLM: explicitly pass this to EVERY CrewAI Agent below.
llm = LLM(
    model="openrouter/deepseek/deepseek-chat",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.2,
)

# Local fallback database. Amounts are VAT-inclusive, so do NOT add VAT again.
LOCAL_DB: Dict[str, Any] = {
    "fees_2026": {
        "48_pages": {
            "5_years": {"regular": 4025, "express": 6325, "super_express": 8625},
            "10_years": {"regular": 5750, "express": 8050, "super_express": 10350},
        },
        "64_pages": {
            "5_years": {"regular": 6325, "express": 8625, "super_express": 12075},
            "10_years": {"regular": 8050, "express": 10350, "super_express": 13800},
        },
    },
    "required_docs": {
        "adult": ["NID Card (required for applicants over 20 applying in Bangladesh)",
                  "Online Application Summary / printed application form",
                  "Payment receipt / e-challan as applicable"],
        "minor_under_18": ["Online Birth Registration Certificate (English version)",
                           "Parent's NID number/card",
                           "Parent(s)' photo where required by age-specific rules"],
        "government_staff": ["GO/NOC or applicable official permission document"],
        "profession_change": ["Professional certificate or Student ID, if applicable"],
        "marital_status_change": ["Marriage certificate / Nikahnama, if applicable"],
        "under_6": ["3R-size photo, as specified by the official portal"],
    },
    "policy": {
        "under_18": "5-year validity, 48 pages; English-version online BRC; parent NID details required if applicant has no NID.",
        "age_18_to_20": "NID or English-version online BRC may be used.",
        "over_20": "NID required for applications inside Bangladesh.",
        "age_over_65": "Do not automatically apply an old 5-year-only restriction; verify current official instructions. The official portal note says the previous restriction was cancelled.",
        "delivery_days": {
            "regular": "within 15 working days (portal also describes 21 days from enrolment in its fee section)",
            "express": "within 7 working days (portal also describes 10 days from enrolment in its fee section)",
            "super_express": "within 2 working days",
        },
    },
    "official_sources": [
        "https://www.epassport.gov.bd/instructions/passport-fees",
        "https://www.epassport.gov.bd/instructions/instructions",
        "https://www.epassport.gov.bd/landing/faqs/21",
    ],
}


def normalize_urgency(value: str) -> str:
    """Map common user wording to the fee database delivery key."""
    value = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "normal": "regular",
        "standard": "regular",
        "urgent": "express",
        "emergency": "super_express",
        "superurgent": "super_express",
        "super_express": "super_express",
        "express": "express",
        "regular": "regular",
    }
    return aliases.get(value, "regular")


def fee_from_local_db(pages: int, validity_years: int, delivery: str) -> int:
    """Deterministic fallback lookup; fees already include VAT."""
    page_key = f"{pages}_pages"
    validity_key = f"{validity_years}_years"
    delivery_key = normalize_urgency(delivery)
    try:
        return int(LOCAL_DB["fees_2026"][page_key][validity_key][delivery_key])
    except KeyError as exc:
        raise ValueError(
            "Unsupported fee combination. Pages must be 48 or 64, "
            "validity 5 or 10 years, delivery regular/express/super_express."
        ) from exc


def make_agents():
    policy_guardian = Agent(
        role="Bangladesh Passport Policy Expert (Policy Guardian)",
        goal=(
            "Assess e-passport eligibility using the applicant's age and identity "
            "documents; identify incompatible choices and clearly flag uncertainty."
        ),
        backstory=(
            "You are a careful policy analyst who uses the official Bangladesh "
            "e-Passport portal as the primary source and a local policy database "
            "only as a fallback. You never invent rules. Applicants under 18 are "
            "limited to a 5-year, 48-page passport under the portal instructions. "
            "For ages 18–20, NID or English-version online BRC may be used; over 20 "
            "applicants applying inside Bangladesh need NID. Verify age-over-65 "
            "rules instead of repeating outdated restrictions."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    fee_calculator = Agent(
        role="Passport Fee Auditor (Fee Calculator)",
        goal=(
            "Return the exact fee for the eligible combination of page count, "
            "validity, and delivery speed using the supplied 2026 local database."
        ),
        backstory=(
            "You are a meticulous financial auditor. The local fee values already "
            "include 15% VAT, so never add VAT a second time. Use the Policy "
            "Guardian's findings as task context. If a requested combination is "
            "invalid or eligibility is unresolved, report that clearly instead of "
            "silently charging for an incompatible option."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    document_architect = Agent(
        role="Passport Documentation Officer (Document Architect)",
        goal=(
            "Create a tailored document checklist based on age, identity document, "
            "profession, and any name or marital-status change."
        ),
        backstory=(
            "You are a precise documentation specialist. You distinguish required "
            "documents from conditional documents, and avoid presenting optional "
            "items as mandatory. Government employees may need GO/NOC or applicable "
            "official permission. Profession changes may need a professional "
            "certificate or Student ID; marital-status changes may need a marriage "
            "certificate. Use the local database if official retrieval fails."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
    return policy_guardian, fee_calculator, document_architect


def run_passport_agent(
    age: int,
    profession: str,
    pages: int,
    requested_validity_years: int,
    urgency: str,
    identity_document: str,
    lives_in_bangladesh: bool = True,
    name_change: bool = False,
    marital_status_change: bool = False,
) -> str:
    """Run the three-agent CrewAI workflow and return the report text."""
    if age < 0:
        raise ValueError("Age cannot be negative.")
    if pages not in (48, 64):
        raise ValueError("Page count must be 48 or 64.")
    if requested_validity_years not in (5, 10):
        raise ValueError("Requested validity must be 5 or 10 years.")

    delivery_key = normalize_urgency(urgency)
    applicant = {
        "age": age,
        "profession": profession,
        "pages_requested": pages,
        "validity_requested_years": requested_validity_years,
        "urgency_requested": urgency,
        "normalized_delivery": delivery_key,
        "identity_document_available": identity_document,
        "applying_inside_bangladesh": lives_in_bangladesh,
        "name_change": name_change,
        "marital_status_change": marital_status_change,
    }

    policy, fees, docs = make_agents()

    policy_task = Task(
        description=(
            "Assess this applicant against the supplied official-policy notes and "
            "local fallback data. State eligible validity, eligible page count, "
            "identity document rule, and any conflict. In particular, flag a "
            "15-year-old requesting a 10-year passport and explain the valid "
            "alternative. Do not assume every age above 65 has a 5-year-only limit.\n\n"
            f"Applicant profile:\n{json.dumps(applicant, ensure_ascii=False, indent=2)}\n\n"
            f"Local policy fallback:\n{json.dumps(LOCAL_DB['policy'], ensure_ascii=False, indent=2)}\n"
            f"Official sources to consult if tools are available: {LOCAL_DB['official_sources']}"
        ),
        expected_output=(
            "A concise policy decision with: status, eligible validity, eligible "
            "pages, identity document requirement, and explicit warnings."
        ),
        agent=policy,
        verbose=False,
    )

    fee_task = Task(
        description=(
            "Calculate the fee using the Policy Guardian's result supplied as "
            "context. Use LOCAL_DB fees only. The fee table already includes 15% "
            "VAT. If policy says the requested validity/pages are not eligible, "
            "price the closest valid option and label it as an alternative, not "
            "as the requested option. If policy is unclear, state that verification "
            "is needed.\n\n"
            f"Applicant profile:\n{json.dumps(applicant, ensure_ascii=False, indent=2)}\n\n"
            f"Local fee database:\n{json.dumps(LOCAL_DB['fees_2026'], ensure_ascii=False, indent=2)}"
        ),
        expected_output=(
            "Requested fee status, valid fee option if available, amount in BDT, "
            "delivery label, and a note that VAT is already included."
        ),
        agent=fees,
        context=[policy_task],
        verbose=False,
    )

    docs_task = Task(
        description=(
            "Create a customized checklist in English and Bangla. Mark items as "
            "Required or Conditional. Use age and identity-document rules, and "
            "include conditional documents for government employment, profession "
            "change, marital-status change, and under-six photo rules where relevant. "
            "Do not claim a private-sector employee always needs profession proof.\n\n"
            f"Applicant profile:\n{json.dumps(applicant, ensure_ascii=False, indent=2)}\n\n"
            f"Local document fallback:\n{json.dumps(LOCAL_DB['required_docs'], ensure_ascii=False, indent=2)}"
        ),
        expected_output=(
            "An English checklist and a Bangla checklist with required/conditional "
            "labels, plus a short note to verify current official instructions."
        ),
        agent=docs,
        context=[policy_task, fee_task],
        verbose=False,
    )

    final_task = Task(
        description=(
            "Produce ONE concise final report only. Do not repeat the same fact in "
            "multiple sections. First give one English Markdown table with columns "
            "Field | Result | Notes and rows for eligibility, validity, pages, "
            "delivery, fee, identity document, and warnings. Then give a short Bangla "
            "summary (not a second full table). Then give ONE bilingual checklist: "
            "required items first and conditional items only when relevant. List the "
            "official URLs once at the end. Clearly say when information came from "
            "LOCAL_DB and has not been live-verified. Never claim browsing occurred "
            "unless a browsing tool was actually used. Highlight conflicts in a "
            "WARNING row. Use clear, natural Bangla Unicode text."
        ),
        expected_output=(
            "One concise English Markdown table, one short Bangla summary, one "
            "non-repeated bilingual checklist, and official URLs listed once."
        ),
        agent=docs,
        context=[policy_task, fee_task, docs_task],
        verbose=False,
    )

    crew = Crew(
        agents=[policy, fees, docs],
        tasks=[policy_task, fee_task, docs_task, final_task],
        process=Process.sequential,
        verbose=False,
    )
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    print("\n=== AMAR PASSPORT: Applicant Details ===")
    try:
        age = int(input("Age: ").strip())
        profession = input("Profession (e.g., private employee / government employee): ").strip()
        pages = int(input("Passport pages (48 or 64): ").strip())
        validity = int(input("Requested validity (5 or 10 years): ").strip())
        urgency = input("Delivery (regular / express / super express): ").strip()
        identity = input("Available ID (NID / English BRC / none): ").strip()
        inside = input("Applying inside Bangladesh? (y/n): ").strip().lower() != "n"
        name_change = input("Name change? (y/n): ").strip().lower() == "y"
        marital_change = input("Marital-status change? (y/n): ").strip().lower() == "y"

        report = run_passport_agent(
            age=age,
            profession=profession,
            pages=pages,
            requested_validity_years=validity,
            urgency=urgency,
            identity_document=identity,
            lives_in_bangladesh=inside,
            name_change=name_change,
            marital_status_change=marital_change,
        )
        print("\n" + "=" * 64)
        print("AMAR PASSPORT — FINAL READINESS REPORT")
        print("=" * 64)
        print(report.strip())

    except (ValueError, KeyboardInterrupt) as error:
        print(f"\nInput error: {error}")
