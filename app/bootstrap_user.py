"""Operator CLI for initial candidate-account creation and password resets."""

from __future__ import annotations

import argparse
from getpass import getpass

from app.db import SessionLocal, init_db
from app.models import User
from app.services.auth import create_user, remove_legacy_demo_account, update_user_credentials


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or reset a BCBA study account.")
    parser.add_argument("--reset", metavar="EMAIL", help="Reset the password for an existing account")
    args = parser.parse_args()

    init_db()
    with SessionLocal() as db:
        # Also handle databases that have not yet been opened by the new app
        # version, whose startup cleanup removes this public demo account.
        remove_legacy_demo_account(db)
        user = None
        if args.reset:
            user = db.query(User).filter(User.email == args.reset.strip().lower()).first()
            if user is None:
                raise SystemExit("No account exists for that email.")
            email = user.email
        else:
            if db.query(User.id).first() is not None:
                raise SystemExit("An account already exists. Use --reset EMAIL to rotate its password.")
            email = input("Candidate email: ").strip().lower()

        password = getpass("New password (at least 12 characters): ")
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            raise SystemExit("Passwords did not match.")

        try:
            if user is not None:
                update_user_credentials(db, user.id, new_password=password)
            else:
                create_user(db, email=email, password=password, name="BCBA Candidate")
        except ValueError as error:
            raise SystemExit(str(error)) from error

    print("Account credentials saved.")


if __name__ == "__main__":
    main()
