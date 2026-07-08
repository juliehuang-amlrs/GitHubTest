from datetime import datetime
from pathlib import Path
from typing import Callable, Dict


# =============================================================================
# SWIFT MT Test Message Generator
# Supports: MT300, MT540, MT700, MT910, MT999
# =============================================================================


def _swift_header(mt_type: str) -> str:
    """
    Basic SWIFT test header.

    Change sender/receiver BICs here if your filter requires specific BICs.
    """
    return (
        "{1:F01CHASUS33XXXX0000000000}"
        f"{{2:I{mt_type}DEUTDEFFXXXXN}}"
        "{3:{108:TESTMSG}}"
    )


def _hit_party(
    hit_field: str,
    hit_type: str,
    field_key: str,
    hit_values: Dict[str, str],
    clean_values: Dict[str, str],
    clean_name: str,
    clean_addr1: str,
    clean_city: str,
    clean_country: str,
) -> str:
    """
    Builds a multi-line party field.

    If this field is selected as the hit field, the party name is replaced
    with the configured hit value. Otherwise clean data is used.
    """
    name = hit_values.get(field_key, clean_name) if hit_field == field_key else clean_values.get(field_key, clean_name)

    return (
        f"/{hit_type}/{field_key}\n"
        f"{name}\n"
        f"{clean_addr1}\n"
        f"{clean_city}\n"
        f"{clean_country}"
    )


def _hit_bic(
    hit_field: str,
    hit_type: str,
    field_key: str,
    hit_values: Dict[str, str],
    clean_bic: str,
) -> str:
    """
    Builds a BIC field.

    If this field is selected as the hit field, the BIC is replaced with
    the configured hit value. Otherwise clean BIC is used.
    """
    return hit_values.get(field_key, clean_bic) if hit_field == field_key else clean_bic


# =============================================================================
# MT300 - Foreign Exchange Confirmation
# =============================================================================

def build_mt300(test_id: int, hit_field: str, hit_type: str, cfg: dict) -> str:
    hv = cfg["hit_values"]
    cv = cfg["clean_values"]
    now = datetime.now()

    bic_52A = _hit_bic(hit_field, hit_type, "OrderingInst_52A", hv, "CHASUS33XXX")
    bic_56A = _hit_bic(hit_field, hit_type, "Intermediary_56A", hv, "BOFAUS3NXXX")
    bic_57A = _hit_bic(hit_field, hit_type, "AccountWithInst_57A", hv, "CITIUS33XXX")

    party_82D = _hit_party(
        hit_field, hit_type, "PartyA_82D",
        hv, cv, "PARTY A BANK LTD", "100 Wall Street", "New York", "US"
    )

    party_87D = _hit_party(
        hit_field, hit_type, "PartyB_87D",
        hv, cv, "PARTY B BANK LTD", "400 Lombard Street", "London", "GB"
    )

    lines = [
        f":20:FX-TC{test_id:02d}",
        f":22A:NEWT",
        f":94A:BILA",
        f":22C:123456ABCD12",
        f":82D:\n{party_82D}",
        f":87D:\n{party_87D}",
        f":30T:{now:%y%m%d}",
        f":30V:{now:%y%m%d}",
        f":36:1,2500",
        f":32B:USD1000000,00",
        f":53A:{bic_52A}",
        f":56A:{bic_56A}",
        f":57A:{bic_57A}",
        f":15C:",
    ]

    header = _swift_header("300")
    body = "\n".join(lines)
    return f"{header}{{4:\n{body}\n-}}"


# =============================================================================
# MT540 - Receive Free Securities
# =============================================================================

def build_mt540(test_id: int, hit_field: str, hit_type: str, cfg: dict) -> str:
    hv = cfg["hit_values"]
    cv = cfg["clean_values"]
    now = datetime.now()

    buyer_95Q = _hit_party(
        hit_field, hit_type, "Buyer_95Q",
        hv, cv, "BUYER SECURITIES LTD", "300 Wall Street", "New York", "US"
    )

    seller_95Q = _hit_party(
        hit_field, hit_type, "Seller_95Q",
        hv, cv, "SELLER HOLDINGS PLC", "400 Lombard Street", "London", "GB"
    )

    bic_deag = _hit_bic(hit_field, hit_type, "DeliveringAgent_95P_DEAG", hv, "CITIUS33XXX")
    bic_sell = _hit_bic(hit_field, hit_type, "Seller_95P_SELL", hv, "DEUTDEFFXXX")
    bic_buyr = _hit_bic(hit_field, hit_type, "Buyer_95P_BUYR", hv, "CHASUS33XXX")

    lines = [
        f":16R:GENL",
        f":20C::SEME//SEC-TC{test_id:02d}",
        f":23G:NEWM",
        f":16S:GENL",
        f":16R:TRADET",
        f":98A::SETT//{now:%Y%m%d}",
        f":98A::TRAD//{now:%Y%m%d}",
        f":35B:ISIN US0378331005",
        f"/US/AAPL",
        f"APPLE INC COMMON STOCK",
        f":16S:TRADET",
        f":16R:FIAC",
        f":36B::SETT//UNIT/1000,",
        f":97A::SAFE//ACCT001",
        f":16S:FIAC",
        f":16R:SETDET",
        f":22F::SETR//TRAD",
        f":16R:SETPRTY",
        f":95P::DEAG//{bic_deag}",
        f":95P::SELL//{bic_sell}",
        f":95P::BUYR//{bic_buyr}",
        f":95Q::BUYR//\n{buyer_95Q}",
        f":95Q::SELL//\n{seller_95Q}",
        f":16S:SETPRTY",
        f":16S:SETDET",
    ]

    header = _swift_header("540")
    body = "\n".join(lines)
    return f"{header}{{4:\n{body}\n-}}"


# =============================================================================
# MT700 - Issue of a Documentary Credit
# =============================================================================

def build_mt700(test_id: int, hit_field: str, hit_type: str, cfg: dict) -> str:
    hv = cfg["hit_values"]
    cv = cfg["clean_values"]
    now = datetime.now()

    applicant = _hit_party(
        hit_field, hit_type, "Applicant_50",
        hv, cv, "APPLICANT TRADING CO", "500 Broadway", "New York", "US"
    )

    beneficiary = _hit_party(
        hit_field, hit_type, "Beneficiary_59",
        hv, cv, "BENEFICIARY EXPORTS LTD", "100 High Street", "London", "GB"
    )

    bic_52A = _hit_bic(hit_field, hit_type, "IssuingBank_52A", hv, "CHASUS33XXX")
    bic_57A = _hit_bic(hit_field, hit_type, "AdvisingBank_57A", hv, "CITIUS33XXX")

    lines = [
        f":27:1/1",
        f":40A:IRREVOCABLE",
        f":20:LC-TC{test_id:02d}",
        f":31C:{now:%y%m%d}",
        f":40E:UCP LATEST VERSION",
        f":31D:{now:%y%m%d}NEW YORK",
        f":50:\n{applicant}",
        f":59:\n{beneficiary}",
        f":32B:USD1000000,00",
        f":41A:{bic_57A}",
        f":42C:SIGHT",
        f":43P:ALLOWED",
        f":43T:ALLOWED",
        f":44A:NEW YORK",
        f":44E:NEW YORK PORT",
        f":44F:LONDON",
        f":44B:LONDON PORT",
        f":45A:GOODS AS PER CONTRACT 12345",
        f":46A:COMMERCIAL INVOICE IN TRIPLICATE",
        f":47A:ALL DOCUMENTS MUST BE IN ENGLISH",
        f":71B:ALL CHARGES OUTSIDE THE ISSUING BANK ARE FOR BENEFICIARY",
        f":48:21 DAYS AFTER SHIPMENT",
        f":49:CONFIRM",
        f":52A:{bic_52A}",
        f":57A:{bic_57A}",
        f":72:ADVISE BENEFICIARY BY SWIFT",
    ]

    header = _swift_header("700")
    body = "\n".join(lines)
    return f"{header}{{4:\n{body}\n-}}"


# =============================================================================
# MT910 - Confirmation of Credit
# =============================================================================

def build_mt910(test_id: int, hit_field: str, hit_type: str, cfg: dict) -> str:
    hv = cfg["hit_values"]
    cv = cfg["clean_values"]
    now = datetime.now()

    ordering_cust = _hit_party(
        hit_field, hit_type, "OrderingCust_50K",
        hv, cv, "ORDERING CUSTOMER INC", "200 Park Avenue", "New York", "US"
    )

    bic_52A = _hit_bic(hit_field, hit_type, "OrderingInst_52A", hv, "CHASUS33XXX")
    bic_56A = _hit_bic(hit_field, hit_type, "Intermediary_56A", hv, "BOFAUS3NXXX")

    lines = [
        f":20:CR-TC{test_id:02d}",
        f":25:123456789",
        f":32A:{now:%y%m%d}USD1000000,00",
        f":50K:\n{ordering_cust}",
        f":52A:{bic_52A}",
        f":56A:{bic_56A}",
        f":72:/REC/PAYMENT FOR SERVICES",
    ]

    header = _swift_header("910")
    body = "\n".join(lines)
    return f"{header}{{4:\n{body}\n-}}"


# =============================================================================
# MT999 - Free Format Message
# =============================================================================

def build_mt999(test_id: int, hit_field: str, hit_type: str, cfg: dict) -> str:
    hv = cfg["hit_values"]
    cv = cfg["clean_values"]

    narrative = _hit_party(
        hit_field, hit_type, "Narrative_79",
        hv, cv, "REFERENCE TO OUR MESSAGE", "DATED TODAY", "NEW YORK", "US"
    )

    lines = [
        f":20:FF-TC{test_id:02d}",
        f":21:RELATED-REF-001",
        f":79:\n{narrative}",
    ]

    header = _swift_header("9999")  # Keep same as your screenshot. Change to "999" if your filter expects 3 digits.
    body = "\n".join(lines)
    return f"{header}{{4:\n{body}\n-}}"


# =============================================================================
# Builder registry
# =============================================================================

BUILDERS: Dict[str, Callable[[int, str, str, dict], str]] = {
    "mt300": build_mt300,
    "mt540": build_mt540,
    "mt700": build_mt700,
    "mt910": build_mt910,
    "mt999": build_mt999,
}


# =============================================================================
# Example config and runner
# =============================================================================

DEFAULT_CFG = {
    "hit_values": {
        # Example hit values. Replace these with your sanctions/watchlist test names/BICs.
        "PartyA_82D": "RADHA KRISHNA",
        "PartyB_87D": "RADHA KRISHNA",
        "OrderingInst_52A": "RADHKRISHXXX",
        "Intermediary_56A": "RADHKRISHXXX",
        "AccountWithInst_57A": "RADHKRISHXXX",

        "Buyer_95Q": "RADHA KRISHNA",
        "Seller_95Q": "RADHA KRISHNA",
        "DeliveringAgent_95P_DEAG": "RADHKRISHXXX",
        "Seller_95P_SELL": "RADHKRISHXXX",
        "Buyer_95P_BUYR": "RADHKRISHXXX",

        "Applicant_50": "RADHA KRISHNA",
        "Beneficiary_59": "RADHA KRISHNA",
        "IssuingBank_52A": "RADHKRISHXXX",
        "AdvisingBank_57A": "RADHKRISHXXX",

        "OrderingCust_50K": "RADHA KRISHNA",
        "Narrative_79": "RADHA KRISHNA",
    },
    "clean_values": {},
}


def write_message(mt_type: str, test_id: int, hit_field: str, hit_type: str, output_dir: str = "output") -> Path:
    mt_type = mt_type.lower()

    if mt_type not in BUILDERS:
        raise ValueError(f"Unsupported MT type: {mt_type}. Valid values: {', '.join(BUILDERS)}")

    msg = BUILDERS[mt_type](test_id, hit_field, hit_type, DEFAULT_CFG)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    file_path = out_dir / f"{mt_type}_{test_id:02d}_{hit_field}.txt"
    file_path.write_text(msg, encoding="utf-8")

    return file_path


if __name__ == "__main__":
    # Example: generate one file for each MT type.
    examples = [
        ("mt300", 1, "PartyA_82D"),
        ("mt540", 2, "Buyer_95Q"),
        ("mt700", 3, "Beneficiary_59"),
        ("mt910", 4, "OrderingCust_50K"),
        ("mt999", 5, "Narrative_79"),
    ]

    for mt_type, test_id, hit_field in examples:
        path = write_message(
            mt_type=mt_type,
            test_id=test_id,
            hit_field=hit_field,
            hit_type="NAME",
            output_dir="output",
        )
        print(f"Created: {path}")
