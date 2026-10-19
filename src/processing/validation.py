from datetime import date
from typing import Optional


def validate_batch_input(
    existing_codes: set,
    batch_code: str,
    quantity: float,
    production_date: date,
    expiration_date: Optional[date],
) -> None:
    if not batch_code.strip():
        raise ValueError("Le code de lot est obligatoire.")
    if batch_code in existing_codes:
        raise ValueError("Le code de lot existe déjà.")
    if quantity <= 0:
        raise ValueError("La quantité produite doit être strictement positive.")
    if expiration_date is not None and expiration_date < production_date:
        raise ValueError("La date de péremption ne peut pas précéder la date de production.")
