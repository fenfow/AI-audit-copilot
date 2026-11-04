import csv
from datetime import date
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "transactions.csv"

REQUIRED_COLUMNS = {
    "transaction_id",
    "vendor_id",
    "invoice_reference",
    "purchase_reference",
    "amount_cents",
    "currency",
    "payment_date",
}


def validate_transaction(row, seen_ids):
    transaction = {}

    for column in REQUIRED_COLUMNS:
        value = row.get(column)

        if value is None or not value.strip():
            raise ValueError(f"Missing value: {column}")

        transaction[column] = value.strip()

    transaction_id = transaction["transaction_id"]

    if transaction_id in seen_ids:
        raise ValueError(
            f"Repeated transaction ID: {transaction_id}"
        )

    amount_cents = int(transaction["amount_cents"])

    if amount_cents <= 0:
        raise ValueError("Amount must be positive")

    if transaction["currency"] != "CAD":
        raise ValueError("Only CAD is supported")

    payment_date = date.fromisoformat(
        transaction["payment_date"]
    )

    transaction["amount_cents"] = amount_cents
    transaction["payment_date"] = payment_date

    seen_ids.add(transaction_id)

    return transaction


def load_transactions(path):
    transactions = []
    seen_ids = set()

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - columns

        if missing_columns:
            raise ValueError(
                f"Missing columns: {sorted(missing_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                transaction = validate_transaction(
                    row, seen_ids
                )
            except ValueError as error:
                raise ValueError(
                    f"CSV row {row_number}: {error}"
                ) from error

            transactions.append(transaction)

    return transactions


def main():
    transactions = load_transactions(DATA_PATH)

    total_cents = sum(
        transaction["amount_cents"]
        for transaction in transactions
    )

    vendor_ids = {
        transaction["vendor_id"]
        for transaction in transactions
    }

    largest_payment = max(
        transaction["amount_cents"]
        for transaction in transactions 
    )

    print(f"Payments loaded: {len(transactions)}")
    print(f"Unique vendors: {len(vendor_ids)}")
    print(f"Total paid: CAD {total_cents / 100:,.2f}")
    print(f"Largest Payement amound: CAD {largest_payment/100:,.2f}")

if __name__ == "__main__":
    main()