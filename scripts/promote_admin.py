
from app.repositories.commerce_repository import CommerceRepository


def main():
    email = input("Account email: ").strip().lower()

    if not email:
        print("Email is required.")
        return

    repo = CommerceRepository()

    with repo.lock:
        db = repo.read()

        customer = next(
            (
                customer
                for customer in db["customers"].values()
                if customer["email"].lower() == email
            ),
            None,
        )

        if customer is None:
            print("Account not found. Register an account first.")
            return

        if not customer["active"]:
            print("Cannot promote a deactivated account.")
            return

        if customer.get("role") == "admin":
            print("This account is already an admin.")
            return

        confirmation = input(
            f"Promote {email} to admin? (yes/no): "
        ).strip().lower()

        if confirmation != "yes":
            print("Cancelled.")
            return

        customer["role"] = "admin"
        repo.save(db)

    print("Admin role updated successfully.")


if __name__ == "__main__":
    main()
