#!/usr/bin/env python3
"""Build ownership.jsonl and company_structure.json for GENTING / GENM."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/raw"

GENT_AR25 = "https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf"
GENT_AR24 = "https://www.genting.com/wp-content/uploads/2025/05/GENTING_IAR24v3.pdf"
GENM_AR25 = "https://www.klsescreener.com/v2/announcements/view/11539849"
GENM_AR24 = "https://www.klsescreener.com/v2/announcements/view/9434623"
KL = "https://www.klsescreener.com/v2/announcements/view/"

ROWS: list[dict] = []


def own(
    holder: str,
    role: str,
    stake_pct: float | None,
    as_of: str,
    source_url: str,
    ticker: str,
    *,
    shares: int | None = None,
    basis: str = "direct",
    source_detail: str | None = None,
    notes: str | None = None,
) -> None:
    ROWS.append(
        {
            "record_type": "ownership",
            "holder": holder,
            "role": role,
            "stake_pct": stake_pct,
            "as_of": as_of,
            "source_url": source_url,
            "ticker": ticker,
            "shares": shares,
            "basis": basis,
            "source_detail": source_detail,
            "notes": notes,
        }
    )


# --- Genting Berhad: FY2024 annual report snapshot (15 Apr 2025) -----------
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 43.5870, "2025-04-15", GENT_AR24, "GENTING", shares=1_678_348_910, basis="direct", source_detail="GENT FY2024 AR pp. 227-228")
own("Kien Huat International Limited", "substantial shareholder", 1.2497, "2025-04-15", GENT_AR24, "GENTING", shares=48_119_980, basis="direct", source_detail="GENT FY2024 AR p. 228")
own("Kien Huat International Limited", "substantial shareholder", 43.5870, "2025-04-15", GENT_AR24, "GENTING", shares=1_678_348_910, basis="deemed via KHR", source_detail="GENT FY2024 AR p. 228")
own("Parkview Management Sdn Bhd (as trustee)", "trustee / deemed substantial shareholder", 44.8366, "2025-04-15", GENT_AR24, "GENTING", shares=1_726_468_890, basis="deemed via KHR + KHI", source_detail="GENT FY2024 AR p. 228")
own("Tan Sri Lim Kok Thay", "executive chairman / deemed substantial shareholder", 44.8366, "2025-04-15", GENT_AR24, "GENTING", shares=1_726_468_890, basis="deemed (beneficiary of trust)", source_detail="GENT FY2024 AR pp. 228-229")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 0.0327, "2025-04-15", GENT_AR24, "GENTING", shares=1_260_000, basis="direct", source_detail="GENT FY2024 AR p. 228")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 44.8366, "2025-04-15", GENT_AR24, "GENTING", shares=1_726_468_890, basis="deemed (beneficiary of trust)", source_detail="GENT FY2024 AR p. 228")

# --- Genting Berhad: FY2025 annual report snapshot (18 Mar 2026) -----------
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 43.8220, "2026-03-18", GENT_AR25, "GENTING", shares=1_687_398_610, basis="direct", source_detail="GENT FY2025 AR pp. 257-258")
own("Kien Huat International Limited", "substantial shareholder", 1.2497, "2026-03-18", GENT_AR25, "GENTING", shares=48_119_980, basis="direct", source_detail="GENT FY2025 AR p. 258")
own("Kien Huat International Limited", "substantial shareholder", 43.8220, "2026-03-18", GENT_AR25, "GENTING", shares=1_687_398_610, basis="deemed via KHR", source_detail="GENT FY2025 AR p. 258")
own("Parkview Management Sdn Bhd (as trustee)", "trustee / deemed substantial shareholder", 45.0717, "2026-03-18", GENT_AR25, "GENTING", shares=1_735_518_590, basis="deemed via KHR + KHI", source_detail="GENT FY2025 AR p. 258")
own("Tan Sri Lim Kok Thay", "executive chairman / deemed substantial shareholder", 45.0717, "2026-03-18", GENT_AR25, "GENTING", shares=1_735_518_590, basis="deemed (beneficiary of trust)", source_detail="GENT FY2025 AR pp. 258-259")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 0.0327, "2026-03-18", GENT_AR25, "GENTING", shares=1_260_000, basis="direct", source_detail="GENT FY2025 AR p. 258")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 45.0717, "2026-03-18", GENT_AR25, "GENTING", shares=1_735_518_590, basis="deemed (beneficiary of trust)", source_detail="GENT FY2025 AR p. 258")
own("Tan Sri Foong Cheng Yuen", "deputy chairman / independent non-executive director", 0.0030, "2026-03-18", GENT_AR25, "GENTING", shares=115_000, basis="direct", source_detail="GENT FY2025 AR p. 258")
own("Dato' Sri Tan Kong Han", "chief executive / president / executive director", 0.0335, "2026-03-18", GENT_AR25, "GENTING", shares=1_290_000, basis="direct", source_detail="GENT FY2025 AR p. 258")
own("Dato' Sri Tan Kong Han", "chief executive / president / executive director", 0.0026, "2026-03-18", GENT_AR25, "GENTING", shares=100_000, basis="deemed (family trust)", source_detail="GENT FY2025 AR p. 258")
own("Madam Koid Swee Lian", "independent non-executive director", 0.0049, "2026-03-18", GENT_AR25, "GENTING", shares=190_000, basis="direct", source_detail="GENT FY2025 AR p. 258")

# --- Genting Berhad: post-rights-issue insider purchases (Oct 2026) --------
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 43.9890, "2026-10-16", KL + "11686057", "GENTING", shares=1_693_821_110, basis="direct", source_detail="Bursa substantial-shareholder notice dated 16 Oct 2026")
own("Kien Huat International Limited", "substantial shareholder", 1.2497, "2026-10-16", KL + "11686073", "GENTING", shares=48_119_980, basis="direct", source_detail="Bursa substantial-shareholder notice dated 16 Oct 2026")
own("Kien Huat International Limited", "substantial shareholder", 43.9890, "2026-10-16", KL + "11686073", "GENTING", shares=1_693_821_110, basis="deemed via KHR", source_detail="Bursa substantial-shareholder notice dated 16 Oct 2026")
own("Parkview Management Sdn Bhd (as trustee)", "trustee / deemed substantial shareholder", 45.2388, "2026-10-16", KL + "11686065", "GENTING", shares=1_741_941_090, basis="deemed via KHR + KHI", source_detail="Bursa substantial-shareholder notice dated 16 Oct 2026")
own("Tan Sri Lim Kok Thay", "executive chairman / deemed substantial shareholder", 45.2388, "2026-10-16", KL + "11686075", "GENTING", shares=1_741_941_090, basis="deemed (beneficiary of trust)", source_detail="Bursa director notice dated 16 Oct 2026")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 0.0327, "2026-10-16", KL + "11686111", "GENTING", shares=1_260_000, basis="direct", source_detail="Bursa director notice dated 16 Oct 2026")
own("Dato' Sri Tan Kong Han", "chief executive / president / executive director", 0.0660, "2026-10-26", KL + "11691613", "GENTING", shares=2_540_000, basis="direct", source_detail="Bursa director notice dated 26 Oct 2026; includes purchases 29 Sep-23 Oct 2026")
own("Dato' Sri Tan Kong Han", "chief executive / president / executive director", 0.0026, "2026-10-26", KL + "11691613", "GENTING", shares=100_000, basis="deemed (family trust)", source_detail="Bursa director notice dated 26 Oct 2026")

# --- Capital / treasury / free float ---------------------------------------
own("Genting Berhad", "issued share capital", None, "2025-12-31", GENT_AR25, "GENTING", shares=3_876_896_099, basis="issued", source_detail="GENT FY2025 AR Note 33, p. 143")
own("Genting Berhad", "shares outstanding (excluding treasury)", None, "2025-12-31", GENT_AR25, "GENTING", shares=3_850_576_099, basis="outstanding", source_detail="GENT FY2025 AR Note 34")
own("Genting Berhad", "treasury shares", 0.6788, "2025-12-31", GENT_AR25, "GENTING", shares=26_320_000, basis="treasury", source_detail="GENT FY2025 AR Note 34; no purchases in FY2024 or FY2025", notes="0.6788% = 26,320,000 / 3,876,896,099; no cancellation, resale or reissuance.")
own("Genting Berhad public shareholders", "free float (calculated)", 54.9283, "2026-03-18", GENT_AR25, "GENTING", basis="calculated", source_detail="100% minus 45.0717% Lim-family deemed interest", notes="Does not deduct directors' small direct holdings; Bursa public-spread definition may differ slightly.")

# --- Genting Malaysia: FY2024 snapshot (17 Mar 2025) -----------------------
own("Genting Berhad", "substantial shareholder / parent", 49.3300, "2025-03-17", GENM_AR24, "GENM", shares=2_795_789_159, basis="direct", source_detail="GENM FY2024 AR p. 180")
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 0.0212, "2025-03-17", GENM_AR24, "GENM", shares=1_198_930, basis="direct", source_detail="GENM FY2024 AR p. 180")
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 49.3300, "2025-03-17", GENM_AR24, "GENM", shares=2_795_789_159, basis="deemed via GENT", source_detail="GENM FY2024 AR p. 180")
own("Kien Huat International Limited", "substantial shareholder", 49.3500, "2025-03-17", GENM_AR24, "GENM", shares=2_796_988_089, basis="deemed via KHR + GENT", source_detail="GENM FY2024 AR p. 180")
own("Parkview Management Sdn Bhd (as trustee)", "trustee / deemed substantial shareholder", 49.3500, "2025-03-17", GENM_AR24, "GENM", shares=2_796_988_089, basis="deemed via KHR + GENT", source_detail="GENM FY2024 AR p. 180")
own("Tan Sri Lim Kok Thay", "deputy chairman and chief executive / deemed substantial shareholder", 49.3493, "2025-03-17", GENM_AR24, "GENM", shares=2_796_992_189, basis="deemed (beneficiary of trust)", source_detail="GENM FY2024 AR p. 180")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 0.0755, "2025-03-17", GENM_AR24, "GENM", shares=4_280_322, basis="direct", source_detail="GENM FY2024 AR p. 180")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 49.3493, "2025-03-17", GENM_AR24, "GENM", shares=2_796_992_189, basis="deemed (beneficiary of trust)", source_detail="GENM FY2024 AR p. 180")

# --- Genting Malaysia: FY2025 snapshot (16 Mar 2026) -----------------------
own("Genting Berhad", "substantial shareholder / parent", 73.8383, "2026-03-16", GENM_AR25, "GENM", shares=4_184_966_253, basis="direct", source_detail="GENM FY2025 AR p. 186")
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 0.0212, "2026-03-16", GENM_AR25, "GENM", shares=1_198_930, basis="direct", source_detail="GENM FY2025 AR p. 186")
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 73.8383, "2026-03-16", GENM_AR25, "GENM", shares=4_184_966_253, basis="deemed via GENT", source_detail="GENM FY2025 AR p. 186")
own("Kien Huat International Limited", "substantial shareholder", 73.8595, "2026-03-16", GENM_AR25, "GENM", shares=4_186_165_183, basis="deemed via KHR + GENT", source_detail="GENM FY2025 AR p. 186")
own("Parkview Management Sdn Bhd (as trustee)", "trustee / deemed substantial shareholder", 73.8595, "2026-03-16", GENM_AR25, "GENM", shares=4_186_165_183, basis="deemed via KHR + GENT", source_detail="GENM FY2025 AR p. 186")
own("Tan Sri Lim Kok Thay", "deputy chairman and chief executive / deemed substantial shareholder", 73.8596, "2026-03-16", GENM_AR25, "GENM", shares=4_186_169_283, basis="deemed (beneficiary of trust)", source_detail="GENM FY2025 AR p. 186")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 73.8596, "2026-03-16", GENM_AR25, "GENM", shares=4_186_169_283, basis="deemed (beneficiary of trust)", source_detail="GENM FY2025 AR p. 186", notes="Direct GENM holding fell to zero after accepting the RM2.35 takeover offer for 4,280,322 shares.")
own("Gen. Dato' Seri DiRaja Tan Sri (Dr.) Mohd Zahidi bin Hj Zainuddin (R)", "chairman / non-independent non-executive director", 0.0002, "2026-03-16", GENM_AR25, "GENM", shares=10_000, basis="direct", source_detail="GENM FY2025 AR p. 186")
own("Dato' Sri Lee Choong Yan", "senior advisor and executive director (to 30 Apr 2026)", 0.0853, "2026-03-16", GENM_AR25, "GENM", shares=4_831_960, basis="direct", source_detail="GENM FY2025 AR p. 186")
own("Mr Quah Chek Tin", "non-independent non-executive director", 0.0001, "2026-03-16", GENM_AR25, "GENM", shares=5_000, basis="direct", source_detail="GENM FY2025 AR p. 186")
own("Mr Teo Eng Siong", "non-independent non-executive director (retired 10 Jun 2026)", 0.0095, "2026-03-16", GENM_AR25, "GENM", shares=540_000, basis="direct", source_detail="GENM FY2025 AR p. 186")

# --- Genting Malaysia: final 2026 stake and treasury ----------------------
own("Genting Berhad", "substantial shareholder / parent", 73.8670, "2026-04-02", KL + "11371165", "GENM", shares=4_186_582_953, basis="direct", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 0.0212, "2026-04-02", KL + "11371153", "GENM", shares=1_198_930, basis="direct", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Kien Huat Realty Sdn Berhad", "substantial shareholder", 73.8670, "2026-04-02", KL + "11371153", "GENM", shares=4_186_582_953, basis="deemed via GENT", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Kien Huat International Limited", "substantial shareholder", 73.8880, "2026-04-02", KL + "11371159", "GENM", shares=4_187_781_883, basis="deemed via KHR + GENT", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Parkview Management Sdn Bhd (as trustee)", "trustee / deemed substantial shareholder", 73.8880, "2026-04-02", KL + "11371151", "GENM", shares=4_187_781_883, basis="deemed via KHR + GENT", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Tan Sri Lim Kok Thay", "deputy chairman and chief executive / deemed substantial shareholder", 73.8880, "2026-04-02", KL + "11371155", "GENM", shares=4_187_785_983, basis="deemed (beneficiary of trust)", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Dato' Indera Lim Keong Hui", "deputy CEO / director and substantial shareholder", 73.8880, "2026-04-02", KL + "11371157", "GENM", shares=4_187_785_983, basis="deemed (beneficiary of trust)", source_detail="Bursa substantial-shareholder notice dated 2 Apr 2026")
own("Genting Malaysia Berhad", "issued share capital", None, "2025-12-31", GENM_AR25, "GENM", shares=5_938_044_648, basis="issued", source_detail="GENM FY2025 AR Note 32, p. 148")
own("Genting Malaysia Berhad", "shares outstanding (excluding treasury)", None, "2025-12-31", GENM_AR25, "GENM", shares=5_667_741_733, basis="outstanding", source_detail="GENM FY2025 AR Note 34")
own("Genting Malaysia Berhad", "treasury shares", 4.5520, "2025-12-31", GENM_AR25, "GENM", shares=270_302_915, basis="treasury", source_detail="GENM FY2025 AR Note 34", notes="4.5520% = 270,302,915 / 5,938,044,648; 10% buyback mandate renewed 11 Jun 2025.")
own("Genting Malaysia Berhad", "treasury shares", 4.56468, "2026-10-12", KL + "11683189", "GENM", shares=271_052_915, basis="treasury", source_detail="Bursa immediate share-buyback announcement dated 12 Oct 2026", notes="Includes 200,000 bought 17 Sep 2026 at RM1.50 and 550,000 bought 12 Oct 2026 at RM1.26-1.27.")
own("Genting Malaysia Berhad public shareholders", "free float (calculated)", 26.1404, "2026-03-16", GENM_AR25, "GENM", basis="calculated", source_detail="100% minus 73.8596% Lim-family deemed interest", notes="Close to the 25% Bursa public-spread floor; GENT+KHR direct combined = 73.8595%.")

# --- Group-level stakes ----------------------------------------------------
own("Genting Berhad -> Genting Malaysia Berhad", "listed subsidiary stake", 73.8383, "2026-03-16", GENM_AR25, "GENM", shares=4_184_966_253, basis="direct", source_detail="GENM FY2025 AR p. 186")
own("Genting Berhad -> Genting Plantations Berhad", "listed subsidiary stake", 55.4, "2026-03-18", GENT_AR25, "GENTING", basis="direct", source_detail="GENT FY2025 AR group corporate structure p. 20")
own("Genting Berhad -> Genting Singapore Limited", "listed subsidiary stake", 52.6, "2026-03-18", GENT_AR25, "GENTING", basis="direct", source_detail="GENT FY2025 AR group corporate structure p. 20")
own("Genting Berhad -> Genting Energy Limited", "unlisted subsidiary stake", 100.0, "2026-03-18", GENT_AR25, "GENTING", basis="direct", source_detail="GENT FY2025 AR group corporate structure p. 20")


def write_ownership() -> None:
    path = OUT / "ownership.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in ROWS:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(ROWS)} ownership rows -> {path}")


STRUCTURE = {
    "generated_utc": "2026-11-02T00:00:00Z",
    "as_of": "2026-03-18",
    "governance_as_of": "2026-11-02",
    "currency": "MYR",
    "sources": [
        {"name": "Genting Berhad FY2025 Integrated Annual Report", "url": GENT_AR25, "date": "2026-04-17", "pages": "20, 257-259"},
        {"name": "Genting Berhad FY2024 Integrated Annual Report", "url": GENT_AR24, "date": "2025-04-25", "pages": "20, 227-229"},
        {"name": "Genting Malaysia FY2025 Integrated Annual Report", "url": GENM_AR25, "date": "2026-04-16", "pages": "186-187"},
        {"name": "Genting Malaysia FY2024 Integrated Annual Report", "url": GENM_AR24, "date": "2025-04-11", "pages": "180-181"},
    ],
    "control_chain": [
        {"from": "Parkview Management Sdn Bhd (trustee of discretionary trust)", "to": "Kien Huat International Limited", "stake_pct": 100.0, "basis": "100% of voting shares", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Kien Huat International Limited", "to": "Kien Huat Realty Sdn Berhad", "stake_pct": 100.0, "basis": "100% of voting shares", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Kien Huat Realty Sdn Berhad", "to": "Genting Berhad", "stake_pct": 43.8220, "basis": "direct", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Kien Huat International Limited", "to": "Genting Berhad", "stake_pct": 1.2497, "basis": "direct", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Parkview Management Sdn Bhd (trustee)", "to": "Genting Berhad", "stake_pct": 45.0717, "basis": "deemed via KHR + KHI", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Tan Sri Lim Kok Thay", "to": "Genting Berhad", "stake_pct": 45.0717, "basis": "deemed beneficiary of trust", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Dato' Indera Lim Keong Hui", "to": "Genting Berhad", "stake_pct": 0.0327, "basis": "direct", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Dato' Indera Lim Keong Hui", "to": "Genting Berhad", "stake_pct": 45.0717, "basis": "deemed beneficiary of trust", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Genting Berhad", "to": "Genting Malaysia Berhad", "stake_pct": 73.8383, "basis": "direct", "as_of": "2026-03-16", "source_url": GENM_AR25},
        {"from": "Kien Huat Realty Sdn Berhad", "to": "Genting Malaysia Berhad", "stake_pct": 0.0212, "basis": "direct", "as_of": "2026-03-16", "source_url": GENM_AR25},
        {"from": "Kien Huat International Limited / Parkview Management", "to": "Genting Malaysia Berhad", "stake_pct": 73.8595, "basis": "deemed via KHR + GENT", "as_of": "2026-03-16", "source_url": GENM_AR25},
        {"from": "Tan Sri Lim Kok Thay / Dato' Indera Lim Keong Hui", "to": "Genting Malaysia Berhad", "stake_pct": 73.8596, "basis": "deemed beneficiary of trust", "as_of": "2026-03-16", "source_url": GENM_AR25},
        {"from": "Genting Berhad", "to": "Genting Plantations Berhad", "stake_pct": 55.4, "basis": "direct", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Genting Berhad", "to": "Genting Singapore Limited", "stake_pct": 52.6, "basis": "direct", "as_of": "2026-03-18", "source_url": GENT_AR25},
        {"from": "Genting Berhad", "to": "Genting Energy Limited", "stake_pct": 100.0, "basis": "direct", "as_of": "2026-03-18", "source_url": GENT_AR25},
    ],
    "nodes": [
        {"id": "PMSB", "name": "Parkview Management Sdn Bhd", "type": "trustee", "listed": False, "jurisdiction": "Malaysia", "notes": "Trustee of a discretionary trust dated 8 April 1983; owns 100% of the voting shares of KHI."},
        {"id": "KHI", "name": "Kien Huat International Limited", "type": "holding_company", "listed": False, "jurisdiction": "Malaysia", "notes": "100% owned by PMSB as trustee; owns 100% of the voting shares of KHR."},
        {"id": "KHR", "name": "Kien Huat Realty Sdn Berhad", "type": "holding_company", "listed": False, "jurisdiction": "Malaysia", "notes": "Lim-family vehicle; direct 43.822% of GENT and 0.0212% of GENM at the FY2025 AR date."},
        {"id": "GENT", "name": "Genting Berhad", "type": "listed_parent", "listed": True, "exchange": "Bursa Malaysia", "code": "3182", "ticker": "GENTING", "notes": "Investment holding and management company; 45.07% Lim-family deemed stake; 26,320,000 treasury shares."},
        {"id": "GENM", "name": "Genting Malaysia Berhad", "type": "listed_subsidiary", "listed": True, "exchange": "Bursa Malaysia", "code": "4715", "ticker": "GENM", "notes": "73.84% owned by GENT; Malaysia's sole casino licence, plus US, UK, Bahamas and Egypt gaming assets."},
        {"id": "GENP", "name": "Genting Plantations Berhad", "type": "listed_subsidiary", "listed": True, "exchange": "Bursa Malaysia", "code": "2297", "ticker": "GENP", "notes": "55.4% owned by GENT; plantations, property, agtech and downstream manufacturing."},
        {"id": "GENS", "name": "Genting Singapore Limited", "type": "listed_subsidiary", "listed": True, "exchange": "Singapore Exchange", "code": "G13", "ticker": "GENS", "notes": "52.6% owned by GENT; operates Resorts World Sentosa."},
        {"id": "GEL", "name": "Genting Energy Limited", "type": "unlisted_subsidiary", "listed": False, "jurisdiction": "Malaysia", "notes": "100% owned by GENT; power and oil & gas interests in Indonesia and China."},
        {"id": "GENNY", "name": "Genting New York LLC", "type": "operating_subsidiary", "listed": False, "jurisdiction": "United States", "parent": "GENM", "stake_pct": 100.0, "notes": "Holds the Resorts World New York City casino licence at Aqueduct Racetrack, Queens."},
        {"id": "RWLV", "name": "Resorts World Las Vegas LLC", "type": "operating_subsidiary", "listed": False, "jurisdiction": "United States", "parent": "GENM", "stake_pct": 100.0, "notes": "Las Vegas Strip integrated resort; subject of the 2025 civil RICO suit."},
        {"id": "EMPIRE", "name": "Empire Resorts, Inc.", "type": "operating_subsidiary", "listed": False, "jurisdiction": "United States", "parent": "GENM", "stake_pct": 100.0, "notes": "Became an indirect wholly owned subsidiary in May 2025 after GENM bought the remaining 51% of Genting Empire Resorts LLC for US$41m plus debt."},
        {"id": "GUK", "name": "Genting UK Plc", "type": "operating_subsidiary", "listed": False, "jurisdiction": "United Kingdom", "parent": "GENM", "stake_pct": 100.0, "notes": "Over 30 UK casinos and Resorts World Birmingham."},
        {"id": "BBEL", "name": "BB Entertainment Ltd", "type": "operating_subsidiary", "listed": False, "jurisdiction": "Bahamas", "parent": "GENM", "stake_pct": 78.0, "notes": "Owns and operates RW Bimini; RAV Bahamas holds 22%."},
        {"id": "RWSPL", "name": "Resorts World at Sentosa Pte Ltd", "type": "operating_subsidiary", "listed": False, "jurisdiction": "Singapore", "parent": "GENS", "stake_pct": 100.0, "notes": "Operates Resorts World Sentosa."},
    ],
    "listed_vehicles": [
        {"name": "Genting Berhad", "ticker": "GENTING", "exchange": "Bursa Malaysia", "code": "3182", "role": "parent"},
        {"name": "Genting Malaysia Berhad", "ticker": "GENM", "exchange": "Bursa Malaysia", "code": "4715", "role": "73.84%-owned subsidiary"},
        {"name": "Genting Plantations Berhad", "ticker": "GENP", "exchange": "Bursa Malaysia", "code": "2297", "role": "55.4%-owned subsidiary"},
        {"name": "Genting Singapore Limited", "ticker": "GENS", "exchange": "Singapore Exchange", "code": "G13", "role": "52.6%-owned subsidiary"},
    ],
    "principal_unlisted_subsidiaries": [
        {"name": "Genting Energy Limited", "parent": "GENT", "stake_pct": 100.0, "business": "Power generation and oil & gas"},
        {"name": "Genting RMTN Berhad", "parent": "GENT", "stake_pct": 100.0, "business": "MTN financing vehicle"},
        {"name": "Genting Vista Berhad", "parent": "GENT", "stake_pct": 100.0, "business": "Unrated MTN financing vehicle"},
        {"name": "Genting Overseas Holdings Limited", "parent": "GENT", "stake_pct": 100.0, "business": "Overseas investment holding; guarantor of GOHL Capital notes"},
        {"name": "GOHL Capital Limited / GOHL Capital Holdings Limited", "parent": "GENT", "stake_pct": 100.0, "business": "Offshore financing vehicles"},
        {"name": "Genting New York LLC", "parent": "GENM", "stake_pct": 100.0, "business": "RWNYC casino licence and operations"},
        {"name": "Resorts World Las Vegas LLC", "parent": "GENM", "stake_pct": 100.0, "business": "Las Vegas integrated resort"},
        {"name": "Genting UK Plc", "parent": "GENM", "stake_pct": 100.0, "business": "UK casinos and Resorts World Birmingham"},
        {"name": "Genting Americas Inc", "parent": "GENM", "stake_pct": 100.0, "business": "US investment holding"},
        {"name": "Empire Resorts, Inc.", "parent": "GENM", "stake_pct": 100.0, "business": "Resorts World Catskills, RW Hudson and RW Bet"},
        {"name": "BB Entertainment Ltd", "parent": "GENM", "stake_pct": 78.0, "business": "RW Bimini, Bahamas"},
        {"name": "Resorts World at Sentosa Pte Ltd", "parent": "GENS", "stake_pct": 100.0, "business": "Resorts World Sentosa"},
        {"name": "Genting Tanjung Bahagia Sdn Bhd", "parent": "GENP", "stake_pct": 100.0, "business": "Plantations"},
    ],
    "governance": [
        {"entity": "GENTING", "name": "Tan Sri Lim Kok Thay", "role": "Executive Chairman / Non-Independent Executive Director", "appointed": "1976-08-17", "changed": "Redesignated Executive Chairman on 2025-03-01 after relinquishing CEO", "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Dato' Sri Tan Kong Han", "role": "Chief Executive, President and Executive Director", "appointed": "2020-01-01", "changed": "Appointed Chief Executive on 2025-03-01", "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Dato' Indera Lim Keong Hui", "role": "Deputy Chief Executive and Executive Director", "appointed": "2012-06-15", "changed": "Executive Director 2013-03-01; Deputy CEO 2019-01-01", "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Tan Sri Foong Cheng Yuen", "role": "Deputy Chairman / Independent Non-Executive Director", "appointed": "2016-01-18", "changed": None, "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Madam Koid Swee Lian", "role": "Independent Non-Executive Director", "appointed": "2017-11-23", "changed": "Chairperson of Risk Management and Sustainability Committee from 2026-09-01", "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Datuk Manharlal A/L Ratilal", "role": "Independent Non-Executive Director", "appointed": "2019-03-01", "changed": "Relinquished Audit/Risk Committee chairmanships on 2026-02-26; remains member", "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Mr Lee Tuck Heng", "role": "Independent Non-Executive Director", "appointed": "2024-02-29", "changed": "Audit and Risk Committee Chairman from 2026-02-26", "source_url": GENT_AR25},
        {"entity": "GENTING", "name": "Mr Eric Ooi Lip Aun", "role": "Independent Non-Executive Director", "appointed": None, "resigned": "2025-02-27", "source_url": KL + "9161103"},
        {"entity": "GENTING", "name": "Ms Wong Yee Fun", "role": "Chief Financial Officer", "appointed": "2019-01-01", "changed": None, "source_url": GENT_AR25},
        {"entity": "GENM", "name": "Gen. Dato' Seri DiRaja Tan Sri (Dr.) Mohd Zahidi bin Hj Zainuddin (R)", "role": "Chairman / Non-Independent Non-Executive Director", "appointed": "2005-08-04", "changed": "Redesignated Chairman on 2024-06-12", "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Tan Sri Lim Kok Thay", "role": "Deputy Chairman and Chief Executive / Non-Independent Executive Director", "appointed": "1988-10-17", "changed": "Redesignated Deputy Chairman and Chief Executive on 2020-08-27", "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Dato' Indera Lim Keong Hui", "role": "Deputy Chief Executive and Executive Director", "appointed": "2012-07-23", "changed": "Executive Director 2015-01-01; Deputy CEO 2019-01-01", "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Dato' Sri Lee Choong Yan", "role": "Senior Advisor and Executive Director (1 Mar-30 Apr 2026); Non-Independent Non-Executive Director from 1 May 2026", "appointed": "2020-01-01", "changed": "President 2022-04-01 to 2026-02-28; Senior Advisor 2026-03-01; NED 2026-05-01", "source_url": KL + "11185095"},
        {"entity": "GENM", "name": "Mr Quah Chek Tin", "role": "Non-Independent Non-Executive Director", "appointed": "2003-01-15", "changed": None, "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Mr Teo Eng Siong", "role": "Non-Independent Non-Executive Director", "appointed": "2010-02-25", "retired": "2026-06-10", "source_url": KL + "11611205"},
        {"entity": "GENM", "name": "Madam Chong Kwai Ying", "role": "Independent Non-Executive Director", "appointed": "2018-12-03", "changed": None, "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Mr Ho Heng Chuan", "role": "Independent Non-Executive Director", "appointed": "2022-02-18", "changed": None, "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Puan Norazilla binti Md Tahir", "role": "Independent Non-Executive Director", "appointed": "2024-01-19", "changed": None, "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Mr Lee Thiam Kit", "role": "President", "appointed": "2026-03-01", "changed": None, "source_url": GENM_AR25},
        {"entity": "GENM", "name": "Ms Loh Wai Yee", "role": "Chief Financial Officer", "appointed": "2025-04-01", "changed": None, "source_url": GENM_AR25}
    ],
    "notes": [
        "Percentages are rounded as disclosed; the 73.8596% GENM figure includes KHR's 1,198,930 direct shares plus GENT's 4,184,966,253 shares.",
        "The Lim family's control is economic/deemed via a discretionary trust; it does not hold a single 45% direct block. KHR is the main direct holder.",
        "Genting Singapore and Genting Plantations are siblings under Genting Berhad, not subsidiaries of Genting Malaysia.",
        "Treasury share percentages use issued shares as the denominator and are calculated, not company-disclosed (except where the announcement states the percentage).",
    ],
}


def write_structure() -> None:
    genm_ids = {"GENM", "GENNY", "RWLV", "EMPIRE", "GUK", "BBEL"}
    for node in STRUCTURE["nodes"]:
        node.setdefault("source_url", GENM_AR25 if node["id"] in genm_ids else GENT_AR25)
    for vehicle in STRUCTURE["listed_vehicles"]:
        vehicle.setdefault("source_url", GENM_AR25 if vehicle["ticker"] == "GENM" else GENT_AR25)
    for sub in STRUCTURE["principal_unlisted_subsidiaries"]:
        sub.setdefault("source_url", GENM_AR25 if sub["parent"] == "GENM" else GENT_AR25)
    path = OUT / "company_structure.json"
    path.write_text(json.dumps(STRUCTURE, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote structure -> {path}")


if __name__ == "__main__":
    write_ownership()
    write_structure()
