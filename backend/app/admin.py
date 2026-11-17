"""Local/host-shell-only account administration. There is no public admin signup API."""
import argparse
import getpass

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User


def create_admin(email: str, full_name: str) -> None:
    if settings.ENVIRONMENT.lower() == "production" and settings.SEED_DEMO_DATA:
        raise SystemExit("Demo seed mode must remain disabled while bootstrapping production administrators.")
    password = getpass.getpass("New administrator password (12+ characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if len(password) < 12 or password != confirmation:
        raise SystemExit("Password must be at least 12 characters and both entries must match.")

    db = SessionLocal()
    try:
        normalized_email = email.strip().lower()
        if db.query(User).filter(User.email == normalized_email).first():
            raise SystemExit("An account with that email already exists.")
        account = User(
            email=normalized_email,
            full_name=full_name.strip(),
            role="admin",
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(account)
        db.commit()
    finally:
        db.close()
    print(f"Administrator account created for {normalized_email}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an administrator account from an authorized host shell.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("create", help="Create one admin account")
    create_parser.add_argument("--email", required=True)
    create_parser.add_argument("--name", required=True)
    args = parser.parse_args()
    if args.command == "create":
        create_admin(args.email, args.name)


if __name__ == "__main__":
    main()
