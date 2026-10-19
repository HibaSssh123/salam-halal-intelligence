from datetime import date
from typing import Optional


def validate_batch_input(
    existing_codes: set,
    batch_code: str,
    quantity: float,
    production_date: date,
    expiration_date: Optional[date],
) -> str:
    normalized_batch_code = batch_code.strip()
    normalized_existing = {str(code).strip().casefold() for code in existing_codes}

    if not normalized_batch_code:
        raise ValueError("Le code de lot est obligatoire.")
    if normalized_batch_code.casefold() in normalized_existing:
        raise ValueError("Le code de lot existe déjà.")
    if quantity <= 0:
        raise ValueError("La quantité produite doit être strictement positive.")
    if expiration_date is not None and expiration_date < production_date:
        raise ValueError("La date de péremption ne peut pas précéder la date de production.")

    return normalized_batch_code
