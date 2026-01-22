"""
Create User Script for Fleet Management System
Run this script to create new users or reset passwords.

Usage:
    python create_user.py                    # Interactive mode
    python create_user.py admin password123  # Direct mode (username password)
"""

import sys
from app import app, db, User


def create_user(username, password, email=None, is_admin=True):
    """Create a new user in the database"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists!")
            reset = input("Do you want to reset their password? (y/n): ").strip().lower()
            if reset == 'y':
                existing_user.set_password(password)
                db.session.commit()
                print(f"✅ Password reset for user '{username}'")
            return
        
        # Generate email if not provided
        if not email:
            email = f"{username}@fleet.local"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            is_admin=is_admin
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ User '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"   Admin: {'Yes' if is_admin else 'No'}")


def list_users():
    """List all users in the database"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found.")
            return
        
        print("\n=== Users ===")
        for user in users:
            admin_badge = "[ADMIN]" if user.is_admin else ""
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Never"
            print(f"  • {user.username} {admin_badge}")
            print(f"    Email: {user.email}")
            print(f"    Last Login: {last_login}")
            print()


def delete_user(username):
    """Delete a user from the database"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        confirm = input(f"Are you sure you want to delete user '{username}'? (y/n): ").strip().lower()
        if confirm == 'y':
            db.session.delete(user)
            db.session.commit()
            print(f"✅ User '{username}' deleted successfully!")


def interactive_mode():
    """Interactive mode for user management"""
    print("\n" + "="*50)
    print("Fleet Management - User Management")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("  1. Create new user")
        print("  2. List all users")
        print("  3. Reset user password")
        print("  4. Delete user")
        print("  5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            print("\n--- Create New User ---")
            username = input("Username: ").strip()
            if not username:
                print("❌ Username cannot be empty!")
                continue
            
            password = input("Password: ").strip()
            if len(password) < 6:
                print("❌ Password must be at least 6 characters!")
                continue
            
            email = input("Email (press Enter to auto-generate): ").strip()
            is_admin = input("Make admin? (y/n): ").strip().lower() == 'y'
            
            create_user(username, password, email if email else None, is_admin)
            
        elif choice == '2':
            list_users()
            
        elif choice == '3':
            print("\n--- Reset Password ---")
            username = input("Username: ").strip()
            password = input("New password: ").strip()
            if len(password) < 6:
                print("❌ Password must be at least 6 characters!")
                continue
            create_user(username, password)
            
        elif choice == '4':
            print("\n--- Delete User ---")
            username = input("Username to delete: ").strip()
            delete_user(username)
            
        elif choice == '5':
            print("\nGoodbye!")
            break
        
        else:
            print("❌ Invalid option!")


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        # Direct mode: python create_user.py username password
        username = sys.argv[1]
        password = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 else None
        create_user(username, password, email)
    elif len(sys.argv) == 2 and sys.argv[1] == '--list':
        # List mode: python create_user.py --list
        list_users()
    else:
        # Interactive mode
        interactive_mode()
